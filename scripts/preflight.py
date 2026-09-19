"""提出前チェック。docs/06_submission.md のチェックリストを自動で通す。

仕様: docs/06_submission.md（提出前チェックリスト）, 05_evaluation.md §4（合格基準）

使い方:
    .venv\\Scripts\\python.exe scripts\\preflight.py
    .venv\\Scripts\\python.exe scripts\\preflight.py --build   :: submission.tar.gz も作る

すべて通れば終了コード0。1つでも落ちたら1。
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 提出物。模倣モデル（models/macro.json）は main.py が使うときだけ入れる（ADR-0002、doc 06）
SUBMISSION_PATHS = ["main.py", "agent"]
MODEL_PATHS = ["models/macro.json"]
MAX_TURN_SECONDS = 0.2    # doc 05 §4 / NFR-1：最悪 < 200ms（actTimeout 1秒の1/5）
P99_TURN_SECONDS = 0.05   # 同：99%のターンが 50ms 未満
BROKEN_OBSERVATIONS = [{}, {"player": 0}, {"farms": []}, {"player": 5, "farms": [{}]}, None]


class Check:
    def __init__(self, name: str, ok: bool, detail: str = ""):
        self.name = name
        self.ok = ok
        self.detail = detail

    def line(self) -> str:
        mark = "OK  " if self.ok else "NG  "
        return f"[{mark}] {self.name}" + (f" … {self.detail}" if self.detail else "")


def _last_callable_name(source: str) -> str | None:
    tree = ast.parse(source)
    names = [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    return names[-1] if names else None


def call_like_kaggle(agent, obs, config):
    """Kaggle 本体と同じく、引数の数に合わせて (obs, config) を切り詰めて呼ぶ。

    `kaggle_environments/agent.py` の `args[: agent.__code__.co_argcount]`（doc 05 §1.1, doc 06）。
    `agent(obs)` と1引数で書かれた公開エージェント（v16rc5）を2引数で呼ぶと TypeError になる。
    """
    code = getattr(agent, "__code__", None)
    count = code.co_argcount if code is not None else 2
    return agent(*[obs, config][:count])


def check_last_callable(main_path: Path, entry: str = "agent") -> Check:
    """Kaggle は最後に定義された callable を agent として使う（doc 06）。"""
    name = _last_callable_name(main_path.read_text(encoding="utf-8"))
    return Check(f"main.py の最後の関数が {entry}", name == entry, f"最後の関数: {name}")


def check_imports(paths: list[Path]) -> Check:
    """提出環境に無いライブラリを import していないか（doc 06）。"""
    allowed_local = {"agent", "main"}
    stdlib = set(getattr(sys, "stdlib_module_names", ()))
    external: set[str] = set()
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [(node.module or "").split(".")[0]]
            else:
                continue
            for name in names:
                if name and name not in stdlib and name not in allowed_local:
                    external.add(name)
    return Check(
        "標準ライブラリと自前モジュールだけを import している",
        not external,
        "外部ライブラリ: " + ", ".join(sorted(external)) if external else "外部ライブラリなし",
    )


def load_like_kaggle(main_path: Path):
    """Kaggle と同じ手順で main.py を読み込む（`kaggle_environments/agent.py` の
    `get_last_callable` を再現）。

    - `exec(compile(raw), {})`：**`__file__` も `__name__` も無い**名前空間で実行される
    - agent は「名前空間の中で最後に現れた callable な値」
    - main.py のあるディレクトリは Kaggle 側が `sys.path` に追加する
    """
    raw = main_path.read_text(encoding="utf-8")
    code_object = compile(raw, str(main_path), "exec")
    env: dict = {}
    sys.path.append(str(main_path.parent))
    try:
        exec(code_object, env)
    finally:
        sys.path.pop()
    callables = [value for value in env.values() if callable(value)]
    if not callables:
        raise ValueError("callable が1つも無い")
    return callables[-1]


def check_kaggle_loader(main_path: Path, entry: str = "agent") -> Check:
    """本番と同じ読み込み方で動くか。`__file__` 依存はここで落ちる（doc 06）。"""
    try:
        agent = load_like_kaggle(main_path)
    except Exception as exc:
        return Check("Kaggle と同じ方法で読み込める", False, f"{type(exc).__name__}: {exc}")
    name = getattr(agent, "__name__", str(agent))
    if name != entry:
        return Check("Kaggle と同じ方法で読み込める", False, f"最後の callable が {name}")
    try:
        result = call_like_kaggle(agent, {}, None)
    except Exception as exc:
        return Check("Kaggle と同じ方法で読み込める", False, f"呼び出しで例外: {exc!r}")
    ok = isinstance(result, dict) and set(result) == {"farmer", "hands", "market"}
    return Check("Kaggle と同じ方法で読み込める", ok, f"最後の callable: {name}")


def load_agent(main_path: Path, entry: str = "agent"):
    spec = importlib.util.spec_from_file_location("_preflight_main", main_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return getattr(module, entry)


def check_action_shape(agent) -> Check:
    """返り値が {farmer, hands, market} の dict か。"""
    try:
        result = call_like_kaggle(agent, {}, None)
    except Exception as exc:  # フォールバックが無い
        return Check("行動の形式が正しい", False, f"例外: {exc!r}")
    ok = (
        isinstance(result, dict)
        and set(result) == {"farmer", "hands", "market"}
        and isinstance(result["farmer"], list)
        and isinstance(result["hands"], list)
        and isinstance(result["market"], list)
    )
    return Check("行動の形式が正しい", ok, str(result)[:80])


def check_fallback(agent) -> Check:
    """壊れた観測でも例外を出さず、形の正しい行動を返す（NFR-2 / doc 06）。

    中身が PASS であることまでは求めない（NFR-2 は「落ちない・フォールバック行動を返す」）。
    公開エージェント（v16rc5）は壊れた観測でも自分の行動列から行動を返す。ADR-0003 で緩めた。
    """
    for observation in BROKEN_OBSERVATIONS:
        try:
            result = call_like_kaggle(agent, observation, None)
        except Exception as exc:
            return Check("壊れた観測でも落ちない", False, f"{observation} で例外: {exc!r}")
        ok = (isinstance(result, dict) and set(result) == {"farmer", "hands", "market"}
              and all(isinstance(result[key], list) for key in result))
        if not ok:
            return Check("壊れた観測でも落ちない", False, f"{observation} の返り値の形が違う: {str(result)[:80]}")
    return Check("壊れた観測でも落ちない", True, f"{len(BROKEN_OBSERVATIONS)}パターン確認")


def turn_time_stats(timings: list[float]) -> dict:
    """中央値・99%点・最悪と、NFR-1 を満たすか（最悪 < 200ms かつ 99%点 < 50ms）。"""
    ordered = sorted(timings)
    if not ordered:
        return {"median": 0.0, "p99": 0.0, "worst": 0.0, "ok": True}
    stats = {
        "median": ordered[len(ordered) // 2],
        "p99": ordered[min(len(ordered) - 1, int(len(ordered) * 0.99))],
        "worst": ordered[-1],
    }
    stats["ok"] = stats["worst"] < MAX_TURN_SECONDS and stats["p99"] < P99_TURN_SECONDS
    return stats


def check_turn_time(agent, episode_steps: int | None = None) -> Check:
    """1ターンの推論時間（doc 05 §4 / NFR-1：最悪 < 200ms かつ 99%点 < 50ms）。"""
    from kaggle_environments import make

    timings: list[float] = []

    def timed(obs, config=None):
        start = time.perf_counter()
        action = call_like_kaggle(agent, obs, config)
        timings.append(time.perf_counter() - start)
        return action

    configuration = {"seed": 1}
    if episode_steps:
        configuration["episodeSteps"] = episode_steps
    env = make("kaggriculture", configuration=configuration)
    env.run([timed, "starter"])
    stats = turn_time_stats(timings)
    statuses = [state["status"] for state in env.state]
    return Check(
        f"1ターンの推論が最悪 {MAX_TURN_SECONDS * 1000:.0f}ms・99%点 {P99_TURN_SECONDS * 1000:.0f}ms 未満で完走する",
        stats["ok"] and statuses[0] == "DONE",
        f"中央値 {stats['median'] * 1000:.2f}ms / 99%点 {stats['p99'] * 1000:.2f}ms / "
        f"最悪 {stats['worst'] * 1000:.2f}ms / status {statuses[0]}",
    )


def check_files(paths: list[Path]) -> Check:
    missing = [str(path) for path in paths if not path.exists()]
    total = sum(
        f.stat().st_size for path in paths for f in
        ([path] if path.is_file() else path.rglob("*.py")) if f.is_file()
    )
    return Check(
        "提出物が揃っている",
        not missing,
        f"不足: {missing}" if missing else f"{len(paths)}項目、合計 {total:,} bytes",
    )


def build_archive(output: Path, paths: list[Path], root: Path = ROOT) -> Path:
    """`main.py` をルートに置いた tar.gz を作る（doc 06）。

    ファイルも `root` からの相対パスで入れる。`models/macro.json` を直下の `macro.json` に
    潰すと、本番で agent/plan.py がモデルを見つけられずルール表に落ちる。
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(output, "w:gz") as archive:
        for path in paths:
            if path.is_file():
                try:
                    arcname = path.resolve().relative_to(Path(root).resolve()).as_posix()
                except ValueError:
                    arcname = path.name
                archive.add(path, arcname=arcname)
            else:
                for file in sorted(path.rglob("*.py")):
                    archive.add(file, arcname=str(file.relative_to(path.parent)).replace("\\", "/"))
    return output


# 展開したアーカイブの中で、Kaggle と同じ読み込み方をしてモデルが使われるかを見る。
# 別プロセスで動かす：このプロセスには既にリポジトリの agent が import されていて、
# 同じプロセスで試すとアーカイブではなくリポジトリのモデルを読んでしまう。
_MODEL_PROBE = r"""
import json, os, sys
root = sys.argv[1]
sys.path.insert(0, root)
env = {}
with open(os.path.join(root, "main.py"), encoding="utf-8") as handle:
    exec(compile(handle.read(), "main.py", "exec"), env)
from agent import plan
model = plan.get_model()
tiles = [[None] * 10 for _ in range(10)]
obs = {"player": 0, "day": 5, "hour": 0,
       "farms": [{"money": 3000.0, "tiles": tiles, "farmer": [4, 4], "hands": [],
                  "unlocked_quadrants": ["NW"], "hires_today": 0}],
       "market": {}, "town": {}, "private": {}}
result = plan.plan_for_turn(obs)
print(json.dumps({"plan_file": os.path.abspath(plan.__file__),
                  "model_path": plan.DEFAULT_MODEL_PATH,
                  "loaded": model is not None,
                  "heads": sorted(model["heads"]) if model else [],
                  "planned": result is not None}))
"""


def check_model_in_archive(archive_path: Path) -> Check:
    """アーカイブを展開し、模倣モデルが読めてルール表に落ちていないか（doc 06 チェックリスト7）。

    モデルが読めないと agent/plan.py は黙ってルール表に落ちる（試合を止めないための設計）。
    そのまま提出すると v2 と同じ中身になるので、ここで必ず止める。
    """
    name = "模倣モデルが読めて、ルール表に落ちていない"
    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(archive_path) as archive:
            archive.extractall(tmp, filter="data")
        try:
            proc = subprocess.run(
                [sys.executable, "-c", _MODEL_PROBE, tmp],
                cwd=tmp, capture_output=True, text=True, timeout=120,
            )
            info = json.loads(proc.stdout.strip().splitlines()[-1])
        except Exception as exc:
            return Check(name, False, f"確認できなかった（{type(exc).__name__}）。ルール表で提出になる恐れ")
        inside = Path(info["plan_file"]).resolve().is_relative_to(Path(tmp).resolve())
    if not inside:
        return Check(name, False, f"アーカイブではなく別の場所の agent を読んだ: {info['plan_file']}")
    if not (info["loaded"] and info["planned"]):
        return Check(name, False, "モデルが読めない。このまま出すとルール表（v2 と同じ中身）で提出になる"
                                  f"（探した場所: {info['model_path']}）")
    return Check(name, True, f"ヘッド {', '.join(info['heads'])}")


def uses_model(main_path: Path) -> bool:
    """main.py が模倣モデルのプラン（`plan_for_turn`）を使っているか。ast で見る。"""
    tree = ast.parse(Path(main_path).read_text(encoding="utf-8"))
    return any(
        (isinstance(node, ast.Attribute) and node.attr == "plan_for_turn")
        or (isinstance(node, ast.Name) and node.id == "plan_for_turn")
        for node in ast.walk(tree)
    )


def submission_paths(root: Path = ROOT) -> list[str]:
    """提出物の一覧。

    - `agent\\` はあるときだけ入れる（公開エージェントは main.py 1枚。ADR-0003）
    - main.py がモデルを使うときだけ models/macro.json を足す（ADR-0002）
    """
    root = Path(root)
    items = [item for item in SUBMISSION_PATHS if item == "main.py" or (root / item).exists()]
    return items + (MODEL_PATHS if uses_model(root / "main.py") else [])


def run_checks(root: Path = ROOT, episode_steps: int | None = None,
               main_path: Path | None = None, entry: str = "agent") -> list[Check]:
    """`main_path` を渡すと、そのファイルのディレクトリを提出物のルートにする（doc 06、ADR-0003）。"""
    if main_path is not None:
        root = Path(main_path).parent
    main_path = Path(root) / "main.py"
    paths = [root / item for item in submission_paths(root)]
    python_files = [main_path] + sorted((root / "agent").glob("*.py"))

    checks = [
        check_files(paths),
        check_last_callable(main_path, entry),
        check_kaggle_loader(main_path, entry),
        check_imports(python_files),
    ]
    if uses_model(main_path):
        with tempfile.TemporaryDirectory() as tmp:
            archive = build_archive(Path(tmp) / "submission.tar.gz", paths, root=root)
            checks.append(check_model_in_archive(archive))
    else:
        # どちらで提出するのかを毎回はっきり出す
        checks.append(Check("模倣モデルの有無", True, "main.py は模倣モデルを使っていない（models/ は同梱しない）"))
    agent = load_agent(main_path, entry)
    checks.append(check_action_shape(agent))
    checks.append(check_fallback(agent))
    checks.append(check_turn_time(agent, episode_steps))
    return checks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="提出前チェック（docs/06_submission.md）")
    parser.add_argument("--build", action="store_true", help="通ったら submission.tar.gz を作る")
    parser.add_argument("--output", type=Path, default=ROOT / "submission.tar.gz")
    parser.add_argument("--episode-steps", type=int, default=None, help="時間計測の試合長（既定720）")
    parser.add_argument("--json", type=Path, default=None)
    parser.add_argument("--main", type=Path, default=None,
                        help="提出する main.py（既定はリポジトリ直下）。そのディレクトリを提出物のルートにする")
    parser.add_argument("--entry", default="agent", help="最後の callable の名前（既定 agent）")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except (AttributeError, ValueError):
        pass
    root = args.main.resolve().parent if args.main else ROOT
    checks = run_checks(root=root, episode_steps=args.episode_steps, entry=args.entry)
    print(f"対象: {root / 'main.py'}")
    for check in checks:
        print(check.line())
    failed = [check for check in checks if not check.ok]
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(
            [{"name": c.name, "ok": c.ok, "detail": c.detail} for c in checks],
            ensure_ascii=False, indent=2), encoding="utf-8")
    if failed:
        print(f"\n{len(failed)}件が未達。提出しないこと。")
        return 1
    print("\nすべて通った。")
    if args.build:
        archive = build_archive(args.output, [root / item for item in submission_paths(root)], root=root)
        print(f"作成: {archive}（{archive.stat().st_size:,} bytes）")
        with tarfile.open(archive) as tar:
            print("中身: " + ", ".join(tar.getnames()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
