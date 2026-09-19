"""リプレイ JSON の構造を調査して人間が読める形で出力する。

仕様: docs/03_replay_schema.md §6（出力項目）, §7（受け入れ条件）

使い方:
    .venv\\Scripts\\python.exe scripts\\inspect_replay.py data\\raw\\<file>.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

MAX_INLINE = 400  # 1項目あたりの表示上限（文字数）


def load_replay(path: str | Path) -> tuple[dict, dict | None]:
    """リプレイ JSON を読む。

    Kaggle からの実リプレイが環境 JSON を何かで包んでいる可能性があるため、
    `steps` を持つ dict を探して (本体, 包んでいた側の情報) を返す。
    包まれていなければ wrapper は None。
    """
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(obj, dict) and "steps" in obj:
        return obj, None
    if isinstance(obj, dict):
        for key, value in obj.items():
            inner = value
            if isinstance(inner, str):
                try:
                    inner = json.loads(inner)
                except (ValueError, TypeError):
                    continue
            if isinstance(inner, dict) and "steps" in inner:
                return inner, {"key": key, "keys": sorted(obj.keys())}
    raise ValueError(f"steps を持つ dict が見つからない: {path}")


def _brief(value: Any, limit: int = MAX_INLINE) -> str:
    text = json.dumps(value, ensure_ascii=False, default=str)
    if len(text) > limit:
        return text[:limit] + f"... (全{len(text)}文字)"
    return text


def _type_name(value: Any) -> str:
    if isinstance(value, list):
        return f"list[{len(value)}]"
    if isinstance(value, dict):
        return f"dict[{len(value)}]"
    return type(value).__name__


def observation_keys(rep: dict) -> dict[int, set[str]]:
    """席ごとの observation キーの和集合。"""
    keys: dict[int, set[str]] = {}
    for step in rep.get("steps", []):
        for seat, record in enumerate(step):
            obs = record.get("observation") or {}
            keys.setdefault(seat, set()).update(obs.keys())
    return keys


def step_record_keys(rep: dict) -> set[str]:
    """steps[t][i] が持つキーの和集合。"""
    keys: set[str] = set()
    for step in rep.get("steps", []):
        for record in step:
            keys.update(record.keys())
    return keys


def _money(rep: dict, t: int, seat: int) -> float | None:
    obs = rep["steps"][t][0].get("observation") or {}
    farms = obs.get("farms")
    if not farms or seat >= len(farms):
        return None
    return farms[seat].get("money")


def check_action_alignment(rep: dict, seat: int = 0) -> dict:
    """行動と観測の対応（doc 03 §3.1）を実データで確認する。

    `steps[t].action` が `steps[t-1].observation` に対する行動なら、
    market 注文の効果は同じ t の観測の所持金に出ているはず。
    """
    steps = rep.get("steps", [])
    result: dict[str, Any] = {
        "seat": seat,
        "first_market_step": None,
        "first_market_action": None,
        "money_before": None,
        "money_after": None,
        "aligned": None,
    }
    for t in range(1, len(steps)):
        if seat >= len(steps[t]):
            break
        action = steps[t][seat].get("action") or {}
        orders = action.get("market") if isinstance(action, dict) else None
        if not orders:
            continue
        result["first_market_step"] = t
        result["first_market_action"] = orders
        result["money_before"] = _money(rep, t - 1, seat)
        result["money_after"] = _money(rep, t, seat)
        if result["money_before"] is not None and result["money_after"] is not None:
            result["aligned"] = result["money_before"] != result["money_after"]
        break
    return result


def final_outcome(rep: dict) -> dict:
    """最終 rewards / statuses と勝者（同点は None）。"""
    steps = rep.get("steps", [])
    rewards = rep.get("rewards")
    if rewards is None and steps:
        rewards = [record.get("reward") for record in steps[-1]]
    statuses = rep.get("statuses")
    if statuses is None and steps:
        statuses = [record.get("status") for record in steps[-1]]
    winner: int | None = None
    if rewards and len(rewards) == 2 and None not in rewards:
        if rewards[0] > rewards[1]:
            winner = 0
        elif rewards[1] > rewards[0]:
            winner = 1
    return {"rewards": rewards, "statuses": statuses, "winner": winner}


def _action_examples(rep: dict, first_n: int = 5, market_n: int = 10) -> list[str]:
    lines: list[str] = []
    steps = rep.get("steps", [])
    lines.append(f"-- 最初の{first_n}ターン --")
    for t in range(min(first_n, len(steps))):
        for seat, record in enumerate(steps[t]):
            lines.append(f"t={t} seat={seat} action={_brief(record.get('action'))}")
    lines.append(f"-- market が空でない最初の{market_n}ターン --")
    found = 0
    for t in range(len(steps)):
        hit = False
        for seat, record in enumerate(steps[t]):
            action = record.get("action") or {}
            if isinstance(action, dict) and action.get("market"):
                lines.append(f"t={t} seat={seat} market={_brief(action['market'])}")
                hit = True
        if hit:
            found += 1
            if found >= market_n:
                break
    if found == 0:
        lines.append("（market 注文が1件も無い）")
    return lines


def describe(rep: dict, path: str | Path | None = None, wrapper: dict | None = None) -> str:
    """doc 03 §6 の1〜8をまとめたレポート文字列を返す。"""
    out: list[str] = []
    steps = rep.get("steps", [])

    out.append(f"===== inspect_replay: {path if path else '(memory)'} =====")
    if wrapper:
        out.append(f"※ 本体は外側 dict のキー {wrapper['key']!r} の中。外側キー: {wrapper['keys']}")

    out.append("\n[1] トップレベル")
    for key in sorted(rep.keys()):
        value = rep[key]
        size = len(json.dumps(value, default=str))
        out.append(f"  {key:16} {_type_name(value):12} {size:>9} bytes  {_brief(value, 120)}")

    out.append("\n[2] configuration")
    conf = json.dumps(rep.get("configuration"), ensure_ascii=False, indent=2, default=str)
    out.append("  " + conf.replace("\n", "\n  "))

    out.append("\n[3] info")
    info = json.dumps(rep.get("info"), ensure_ascii=False, indent=2, default=str)
    out.append("  " + info.replace("\n", "\n  "))

    out.append("\n[4] steps")
    out.append(f"  ステップ数: {len(steps)}")
    out.append(f"  1ステップあたりの席数: {len(steps[0]) if steps else 0}")
    out.append(f"  steps[t][i] のキー: {sorted(step_record_keys(rep))}")

    out.append("\n[5] observation のキー（席ごと）")
    for seat, keys in sorted(observation_keys(rep).items()):
        out.append(f"  seat={seat}: {sorted(keys)}")
        out.append(f"    step キー: {'あり' if 'step' in keys else 'なし'}")

    out.append("\n[6] action の例")
    out.extend("  " + line for line in _action_examples(rep))
    alignment = check_action_alignment(rep)
    out.append("  -- 行動と観測の対応（doc 03 §3.1）--")
    out.append(f"  {alignment}")
    if alignment["aligned"] is True:
        out.append("  → steps[t].action の効果が steps[t].observation に出ている（doc どおり）")
    elif alignment["aligned"] is False:
        out.append("  → 所持金が動いていない。doc 03 §3.1 を見直すこと")

    out.append("\n[7] 最終結果")
    out.append(f"  {final_outcome(rep)}")

    out.append("\n[8] サイズ")
    full = json.dumps(rep, default=str)
    without_spec = json.dumps({k: v for k, v in rep.items() if k != "specification"}, default=str)
    out.append(f"  JSON 全体: {len(full):,} bytes")
    out.append(f"  specification を除く: {len(without_spec):,} bytes")
    if path is not None and Path(path).exists():
        out.append(f"  ファイルサイズ: {Path(path).stat().st_size:,} bytes")
    if steps:
        out.append(f"  1ステップあたり平均: {len(full) // len(steps):,} bytes")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(__doc__)
        return 2
    try:
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    except (AttributeError, ValueError):
        pass
    for path in argv:
        rep, wrapper = load_replay(path)
        print(describe(rep, path=path, wrapper=wrapper))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
