from pathlib import Path
import sys, hashlib

NEEDLE = '''        qty = min(int(stock.get(item, 0)), ours)\n        if qty > 0:\n'''
REPLACEMENT = '''        qty = min(int(stock.get(item, 0)), ours)\n        # v150: v143 singleton weak-vote abstention layered onto formal v147.\n        if qty == 1 and _r37_quote_priority(obs, ["SELL", item, qty], stock) > 0:\n            _v150_preds = [\n                ev.get((step + 1, i), 0) + ev.get((step + 2, i), 0)\n                for ev in best\n            ]\n            if sum(1 for x in _v150_preds if x >= 1) == 1 and not any(x >= 2 for x in _v150_preds):\n                continue\n        if qty > 0:\n'''

src=Path(sys.argv[1]); dst=Path(sys.argv[2]); text=src.read_text(encoding='utf-8')
if text.count(NEEDLE) != 1: raise SystemExit(f'primary V92 block count={text.count(NEEDLE)}')
dst.write_text(text.replace(NEEDLE, REPLACEMENT, 1), encoding='utf-8')
print('v150_sha256='+hashlib.sha256(dst.read_bytes()).hexdigest())
