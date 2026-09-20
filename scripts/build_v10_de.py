# -*- coding: utf-8 -*-
r"""submissions/v10_de/main.py を作る：v8_lategate（候補D）の末尾に候補E の層を足す。

仕様: docs/07_v4_improvement.md §3 候補D・候補E
目的: 独立に作った2つの層が足し算になるかを測る（EXP-20260920-25）

    .venv\Scripts\python.exe scripts\build_v10_de.py

層の中身は `scripts\build_v9_reorder.py` の LAYER をそのまま使う（同じものを2つ置かない）。
v9/4 の原本も v5〜v8 の層も1バイトも変えない。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_v9_reorder import build  # noqa: E402

if __name__ == "__main__":
    build("v8_lategate", "v10_de")
