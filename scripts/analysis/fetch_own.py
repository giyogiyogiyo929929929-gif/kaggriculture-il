# -*- coding: utf-8 -*-
"""自分（チーム）の提出の公開対戦リプレイをまとめて取得する（取得済みは飛ばす）。

仕様: docs/05_evaluation.md §8（分析ツール）
使い方:
    .venv\\Scripts\\python.exe scripts\\analysis\\fetch_own.py <submission_id> <out_dir>
生リプレイは1本約33MB。分析が終わったら `scripts\\digest_replay.py --out data\\digest_own\\<版> --delete-raw` で圧縮する。
ネットワークが必要（Kaggle CLI）。
"""
import csv
import io
import subprocess
import sys
from pathlib import Path

import _common as C

sub, out = sys.argv[1], Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
kaggle = str(C.ROOT / ".venv" / "Scripts" / "kaggle.exe")
text = subprocess.run([kaggle, "competitions", "episodes", sub, "-v"], capture_output=True, text=True,
                      encoding="utf-8", check=True).stdout
# 末尾に説明文の行が付くことがあるので、数字で始まる行だけを CSV として読む
lines = [l for l in text.splitlines() if l[:1].isdigit() or l.startswith("id,")]
rows = list(csv.DictReader(io.StringIO("\n".join(lines))))
new = 0
for r in rows:
    ep = r["id"]
    if list(out.glob(f"*{ep}*.json")):
        continue
    subprocess.run([kaggle, "competitions", "replay", ep, "-p", str(out)], check=True, capture_output=True)
    new += 1
    print("取得", ep, flush=True)
print(f"エピソード {len(rows)} 本、新しく取得 {new} 本 → {out}")
