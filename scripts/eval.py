"""エージェント同士を席入れ替えのペアで対戦させて比較する。

仕様: docs/05_evaluation.md §1（方法）, §2（出力）, §4（合格基準）, §5（受け入れ条件）

使い方:
    .venv\\Scripts\\python.exe scripts\\eval.py main.py starter -n 20
    .venv\\Scripts\\python.exe scripts\\eval.py main.py starter -n 20 -j 4 --json data\\eval\\latest.json

合格基準の判定に使う推論時間は `-j 1` で測ること（並列だと他プロセスの影響で伸びる）。
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import os
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BUILTIN_AGENTS = ("starter", "random", "pass")
ANIMAL_STRUCTURES = ("COOP", "PASTURE")


# ---------------------------------------------------------------- エージェント


def _last_callable_name(source: str) -> str | None:
    """最後に定義された関数名（提出時の規則。doc 06）。"""
    tree = ast.parse(source)
    names = [
        node.name for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    return names[-1] if names else None


def resolve_agent(spec: str):
    """組み込み名ならそのまま、パスならファイルを読み込んで callable を返す（doc 05 §1.1）。"""
    if spec in BUILTIN_AGENTS:
        return spec
    path = Path(spec)
    if not path.is_absolute():
        path = (ROOT / spec).resolve()
    if not path.exists():
        raise FileNotFoundError(f"エージェントが見つからない: {spec}")
    module_spec = importlib.util.spec_from_file_location(f"_eval_agent_{path.stem}", path)
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_spec.name] = module
    # Kaggle は main.py のあるディレクトリを sys.path に入れる（doc 06「仕様」）。
    # 複数ファイルのエージェント（例：opponents\gods_mode）はここが無いと import に失敗する。
    sys.path.insert(0, str(path.parent))
    try:
        module_spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(path.parent))
    # ★ Kaggle が選ぶのは「名前空間の中で最後に現れた callable **な値**」であって、
    #   「最後に def された関数」ではない（doc 06「仕様」、`preflight.load_like_kaggle` と同じ規則）。
    #   両者が食い違うエージェントがある（opponents\v38・v43 は最後の def が補助関数で、
    #   そちらを呼ぶと何もしないまま試合が終わる。EXP-20260920-20）。
    agent = None
    for value in vars(module).values():
        if callable(value):
            agent = value
    if agent is None:
        raise ValueError(f"callable が1つも無い: {path}")
    return agent


class _TimedAgent:
    """推論時間と例外を数えるラッパ。例外時はフォールバック行動を返して試合を続ける。"""

    FALLBACK = {"farmer": ["PASS"], "hands": [], "market": []}

    def __init__(self, agent):
        self.agent = agent
        self.timings: list[float] = []
        self.exceptions = 0
        # Kaggle 本体と同じく、関数の引数の数に合わせて (obs, config) を切り詰める
        # （kaggle_environments/agent.py の `args[: agent.__code__.co_argcount]`。doc 05 §1.1）
        code = getattr(agent, "__code__", None)
        self.argcount = code.co_argcount if code is not None else 2

    def __call__(self, obs, config=None):
        start = time.perf_counter()
        try:
            action = self.agent(*[obs, config][: self.argcount])
        except Exception:
            self.exceptions += 1
            action = dict(self.FALLBACK)
        self.timings.append(time.perf_counter() - start)
        return action


# ---------------------------------------------------------------- 健全性の集計


def _tile_kind(tile):
    if tile is None:
        return "EMPTY"
    if tile == "LOCKED":
        return "LOCKED"
    if isinstance(tile, dict):
        kind = tile.get("kind")
        if kind == "PLANT":
            return "PLANT"
        if kind == "WEED":
            return "WEED"
        if kind in ANIMAL_STRUCTURES:
            return "ANIMAL" if tile.get("animal") else "STRUCTURE"
    return "OTHER"


def classify_weed(previous_tile: dict, step_index: int) -> str:
    """PLANT だったタイルが WEED になった理由を返す（doc 05 §2.1）。

    `ongoing` 作物は最終収穫の翌日に必ず WEED になる。これは仕様どおりの寿命終了で
    失敗ではないので、水やり失敗（水切れ枯死）や収穫失敗（未収穫損失）と区別する。
    """
    lifespan_step = previous_tile.get("max_lifespan_step", -1)
    if lifespan_step >= 0 and step_index - 1 >= lifespan_step:
        return "unharvested_lost" if previous_tile.get("yield_units", 0) > 0 else "lifespan_ended"
    # 寿命以外で消えたなら水切れ。判別できない形でも損失として数える（見落としより安全）。
    return "withered"


def health_metrics(steps, seat: int) -> dict:
    """連続する2ステップのタイル比較で健全性を数える（doc 05 §2.1）。"""
    counts = {
        "planted": 0,
        "harvested": 0,
        "withered": 0,
        "unharvested_lost": 0,
        "lifespan_ended": 0,
        "weed_spawned": 0,
        "animals_lost": 0,
    }
    previous = None
    for index, step in enumerate(steps):
        observation = step[0].get("observation") or {}
        farms = observation.get("farms") or []
        if seat >= len(farms):
            continue
        tiles = farms[seat].get("tiles") or []
        if previous is not None:
            for row_before, row_after in zip(previous, tiles):
                for before, after in zip(row_before, row_after):
                    kind_before = _tile_kind(before)
                    kind_after = _tile_kind(after)
                    if kind_before == "EMPTY" and kind_after == "PLANT":
                        counts["planted"] += 1
                    elif kind_before == "PLANT" and kind_after == "EMPTY":
                        counts["harvested"] += 1
                    elif kind_before == "PLANT" and kind_after == "WEED":
                        counts[classify_weed(before, index)] += 1
                    elif kind_before == "EMPTY" and kind_after == "WEED":
                        counts["weed_spawned"] += 1
                    elif kind_before == "ANIMAL" and kind_after == "STRUCTURE":
                        counts["animals_lost"] += 1
        previous = [list(row) for row in tiles]

    # 合格基準に使うのは「本当に失った分」だけ（寿命終了は除外）
    counts["crop_losses"] = counts["withered"] + counts["unharvested_lost"]

    last = steps[-1]
    private = (last[seat].get("observation") or {}).get("private") or {} if seat < len(last) else {}
    counts["shed_final"] = sum((private.get("shed") or {}).values())
    return counts


# ---------------------------------------------------------------- 1試合


def play_match(spec_a: str, spec_b: str, seed: int, swap: bool, episode_steps: int | None = None) -> dict:
    """1試合。`swap` が True なら A が席1に座る。戻り値は常に A 視点。"""
    from kaggle_environments import make

    agent_a = _TimedAgent(resolve_agent(spec_a)) if spec_a not in BUILTIN_AGENTS else None
    agent_b = _TimedAgent(resolve_agent(spec_b)) if spec_b not in BUILTIN_AGENTS else None
    runner_a = agent_a if agent_a is not None else spec_a
    runner_b = agent_b if agent_b is not None else spec_b

    configuration = {"seed": seed}
    if episode_steps:
        configuration["episodeSteps"] = episode_steps
    env = make("kaggriculture", configuration=configuration)
    env.run([runner_b, runner_a] if swap else [runner_a, runner_b])

    seat_a = 1 if swap else 0
    seat_b = 1 - seat_a
    rewards = [state["reward"] for state in env.state]

    def timing_stats(wrapper):
        if wrapper is None or not wrapper.timings:
            return {"median": 0.0, "max": 0.0}
        return {
            "median": statistics.median(wrapper.timings),
            "max": max(wrapper.timings),
        }

    return {
        "seed": seed,
        "swap": swap,
        "steps": len(env.steps),
        "money": [rewards[seat_a], rewards[seat_b]],
        "timings": {"a": timing_stats(agent_a), "b": timing_stats(agent_b)},
        "exceptions": {
            "a": agent_a.exceptions if agent_a else 0,
            "b": agent_b.exceptions if agent_b else 0,
        },
        "health": {"a": health_metrics(env.steps, seat_a), "b": health_metrics(env.steps, seat_b)},
        "statuses": [state.get("status") for state in env.state],
    }


def _run_match(args) -> dict:
    """ProcessPoolExecutor のワーカー（spawn なので引数は文字列と数値だけ）。"""
    spec_a, spec_b, seed, swap, episode_steps = args
    return play_match(spec_a, spec_b, seed, swap, episode_steps)


# ---------------------------------------------------------------- まとめ


def build_matches(pairs: int, seed_start: int = 1) -> list[tuple[int, bool]]:
    """各 seed について席を入れ替えた2試合（doc 05 §1）。"""
    matches: list[tuple[int, bool]] = []
    for index in range(pairs):
        seed = seed_start + index
        matches.append((seed, False))
        matches.append((seed, True))
    return matches


def default_jobs() -> int:
    return max(1, min(4, (os.cpu_count() or 2) - 1))


def evaluate(spec_a: str, spec_b: str, pairs: int, jobs: int | None = None,
             seed_start: int = 1, episode_steps: int | None = None) -> dict:
    """ペア比較を回して要約を返す（doc 05 §1, §2）。"""
    jobs = default_jobs() if jobs is None else max(1, jobs)
    matches = build_matches(pairs, seed_start)
    tasks = [(spec_a, spec_b, seed, swap, episode_steps) for seed, swap in matches]

    if jobs == 1:
        results = [_run_match(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as pool:
            results = list(pool.map(_run_match, tasks))

    by_seed: dict[int, list[dict]] = {}
    for result in results:
        by_seed.setdefault(result["seed"], []).append(result)

    pair_diffs: list[float] = []
    wins = losses = draws = 0
    for seed in sorted(by_seed):
        games = by_seed[seed]
        diffs = [game["money"][0] - game["money"][1] for game in games]
        diff = statistics.mean(diffs)
        pair_diffs.append(diff)
        if diff > 0:
            wins += 1
        elif diff < 0:
            losses += 1
        else:
            draws += 1

    money_a = [game["money"][0] for game in results]
    money_b = [game["money"][1] for game in results]
    stderr = (statistics.stdev(pair_diffs) / len(pair_diffs) ** 0.5) if len(pair_diffs) > 1 else 0.0

    def merge_timings(side):
        medians = [game["timings"][side]["median"] for game in results]
        return {
            "median": statistics.median(medians) if medians else 0.0,
            "max": max((game["timings"][side]["max"] for game in results), default=0.0),
        }

    def merge_health(side):
        keys = results[0]["health"][side].keys()
        return {key: sum(game["health"][side][key] for game in results) // len(results) for key in keys}

    return {
        "agents": [spec_a, spec_b],
        "pairs": pairs,
        "matches": len(results),
        "jobs": jobs,
        "episode_steps": episode_steps,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "pair_diff_mean": statistics.mean(pair_diffs) if pair_diffs else 0.0,
        "pair_diff_stderr": stderr,
        "money_median": [
            statistics.median(money_a) if money_a else 0.0,
            statistics.median(money_b) if money_b else 0.0,
        ],
        "timings": {"a": merge_timings("a"), "b": merge_timings("b")},
        "exceptions": {
            "a": sum(game["exceptions"]["a"] for game in results),
            "b": sum(game["exceptions"]["b"] for game in results),
        },
        "health": {"a": merge_health("a"), "b": merge_health("b")},
        "matches_detail": results,
    }


def format_summary(summary: dict) -> str:
    """人が読む表（doc 05 §2）。"""
    a, b = summary["agents"]
    lines = [
        f"対戦: {a} vs {b}   ペア数 {summary['pairs']}（{summary['matches']}試合、-j {summary['jobs']}）",
        f"勝敗          : {summary['wins']}勝 {summary['losses']}敗 {summary['draws']}分（ペア単位）",
        f"ペア差        : {summary['pair_diff_mean']:+,.0f} ± {summary['pair_diff_stderr']:,.0f}"
        f"（平均 ± 標準誤差）",
        f"最終所持金    : A 中央値 {summary['money_median'][0]:,.0f} / "
        f"B 中央値 {summary['money_median'][1]:,.0f}",
        f"1ターン推論   : A 中央値 {summary['timings']['a']['median'] * 1000:.1f}ms "
        f"最悪 {summary['timings']['a']['max'] * 1000:.1f}ms / "
        f"B 中央値 {summary['timings']['b']['median'] * 1000:.1f}ms "
        f"最悪 {summary['timings']['b']['max'] * 1000:.1f}ms",
        f"例外          : A {summary['exceptions']['a']}件 / B {summary['exceptions']['b']}件",
    ]
    for side, label in (("a", "A"), ("b", "B")):
        health = summary["health"][side]
        lines.append(
            f"健全性({label})     : 植え付け {health['planted']} → 収穫 {health['harvested']} "
            f"/ 損失 {health['crop_losses']}"
            f"（水切れ {health['withered']} + 未収穫 {health['unharvested_lost']}"
            f"／寿命終了 {health['lifespan_ended']} は正常）"
            f"/ 家畜逃走 {health['animals_lost']} / 最終shed {health['shed_final']}"
        )
    if summary["timings"]["a"]["max"] >= 0.2:
        lines.append("※ A の推論時間が 200ms を超えている（05 §4）。-j 1 か preflight で測り直すこと")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="席入れ替えのペア比較（docs/05_evaluation.md）")
    parser.add_argument("agent_a", help="組み込み名（starter/random/pass）かファイルパス")
    parser.add_argument("agent_b")
    parser.add_argument("-n", "--pairs", type=int, default=20, help="ペア数（試合数はこの2倍）")
    parser.add_argument("-j", "--jobs", type=int, default=None, help="並列数（既定: min(4, CPU-1)）")
    parser.add_argument("--seed-start", type=int, default=1)
    parser.add_argument("--episode-steps", type=int, default=None, help="試合の長さ（既定720。動作確認用）")
    parser.add_argument("--json", type=Path, default=None, help="結果を JSON で書き出す")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except (AttributeError, ValueError):
        pass
    started = time.perf_counter()
    summary = evaluate(
        args.agent_a, args.agent_b, pairs=args.pairs, jobs=args.jobs,
        seed_start=args.seed_start, episode_steps=args.episode_steps,
    )
    print(format_summary(summary))
    print(f"所要時間      : {time.perf_counter() - started:.1f}秒")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"JSON          : {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
