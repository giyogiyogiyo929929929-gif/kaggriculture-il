#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load(path: Path):
    spec = importlib.util.spec_from_file_location("v99_candidate", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: synthetic_v99.py <candidate.py>")
    m = load(Path(sys.argv[1]))

    # Minimal state for actor 0. The key property is that a weed block begins at
    # step 23, then step 24 crosses the day boundary. v96 clears all active lag
    # state there; v99 must retain actor 0 and replay the intended action.
    m._E343_WL_STATE.clear()
    m._E343_WL_REPORT.update(events=0, replays=0, errors=0)
    m._V99_WL_REPORT.update(main_boundary_preserved=0, errors=0)

    old_tape = m._e343_tape_units
    try:
        def fake_tape(player, step):
            if step == 23:
                return [["BUILD_PASTURE"]]
            if step == 24:
                return [["EAST"]]
            return [["PASS"]]
        m._e343_tape_units = fake_tape

        obs23 = {
            "step": 23,
            "player": 0,
            "farms": [{
                "farmer": [1, 1],
                "hands": [],
                "tiles": [[None for _ in range(3)] for _ in range(3)],
            }],
        }
        obs23["farms"][0]["tiles"][1][1] = {"kind": "WEED"}
        a23 = {"farmer": ["BUILD_PASTURE"], "hands": [], "market": []}
        r23 = m._e343_weedlag(obs23, a23)
        assert r23["farmer"] == ["DIG"], r23
        assert 0 in m._E343_WL_STATE[0]["active"]

        obs24 = {
            "step": 24,
            "player": 0,
            "farms": [{
                "farmer": [1, 1],
                "hands": [],
                "tiles": [[None for _ in range(3)] for _ in range(3)],
            }],
        }
        a24 = {"farmer": ["EAST"], "hands": [], "market": []}
        r24 = m._e343_weedlag(obs24, a24)
        assert r24["farmer"] == ["BUILD_PASTURE"], r24
        assert m._V99_WL_REPORT["main_boundary_preserved"] == 1
        assert m._E343_WL_REPORT["replays"] == 1

        # Farmhand lag state must still be discarded at the boundary.
        m._E343_WL_STATE[0] = {
            "step": 23,
            "active": {
                0: {"start": 23, "intended": ["BUILD_PASTURE"]},
                1: {"start": 23, "intended": ["PLANT", "WHEAT"]},
            },
        }
        obs24h = {
            "step": 24,
            "player": 0,
            "farms": [{
                "farmer": [1, 1],
                "hands": [[0, 0]],
                "tiles": [[None for _ in range(3)] for _ in range(3)],
            }],
        }
        a24h = {"farmer": ["EAST"], "hands": [["PASS"]], "market": []}
        m._e343_weedlag(obs24h, a24h)
        assert 1 not in m._E343_WL_STATE[0]["active"]

        print("PASS main-farmer weedlag survives day boundary")
        print("PASS farmhand weedlag still resets at day boundary")
    finally:
        m._e343_tape_units = old_tape


if __name__ == "__main__":
    main()
