# -*- coding: utf-8 -*-
"""公開ノートブックから main.py を取り出す（セルは実行しない。ast でリテラルだけ読む）。

扱う形：
- `SOURCE_BYTES = b''.join([...])` / 文字列・バイト列のリテラル
- base64 → (tar | tar.gz | gzip | zlib | そのまま) → main.py
ノートブックに `EXPECTED_MAIN_SHA256` があれば照合する。

仕様: docs/05_evaluation.md §8（分析ツール）、AGENTS.md §5（セルは実行しない）
使い方:
    .venv\\Scripts\\kaggle.exe kernels pull <作者>/<ノートブック> -p <notebook_dir>\\<名前>
    .venv\\Scripts\\python.exe scripts\\analysis\\extract_notebook_agents.py <notebook_dir> <out_dir>
    .venv\\Scripts\\python.exe scripts\\analysis\\audit_agent.py <out_dir>\\<名前>.py
<notebook_dir>\\*\\*.ipynb を読み、<out_dir>\\<ノートブック名>.py に書く。取り出したら必ず audit_agent.py で監査し、
opponents\\<名前>\\main.py と SOURCE.md（出典・取り出し方・SHA-256・監査結果）を作る（例：opponents\\v50\\SOURCE.md）。
"""
import ast
import base64
import glob
import gzip
import hashlib
import io
import json
import os
import re
import sys
import tarfile
import zlib

sys.stdout.reconfigure(encoding="utf-8")
BASE, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)


def literal(node):
    """文字列・バイト列のリテラル、または b''.join([...]) / ''.join([...]) / 連結を値にする。"""
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes)):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        a, b = literal(node.left), literal(node.right)
        if a is not None and b is not None and type(a) is type(b):
            return a + b
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "join"
            and isinstance(node.func.value, ast.Constant) and len(node.args) == 1
            and isinstance(node.args[0], (ast.List, ast.Tuple))):
        parts = [literal(e) for e in node.args[0].elts]
        if parts and all(p is not None for p in parts):
            return node.func.value.value.join(parts)
    return None


def unpack(data):
    """バイト列から main.py の候補を返す（名前, バイト列）。"""
    out = []
    for name, fn in (("tar", lambda b: tarfile.open(fileobj=io.BytesIO(b))),):
        try:
            with fn(data) as tf:
                for m in tf.getmembers():
                    if m.isfile() and m.name.endswith(".py"):
                        out.append((m.name, tf.extractfile(m).read()))
            return out
        except Exception:
            pass
    for dec in (gzip.decompress, zlib.decompress):
        try:
            return unpack(dec(data))
        except Exception:
            pass
    return [("raw", data)]


def candidates(value):
    data = value.encode("utf-8") if isinstance(value, str) else value
    found = []
    try:
        text = data.decode("utf-8")
        ast.parse(text)
        if "def " in text and len(text) > 5000:
            found.append(("literal", data))
    except Exception:
        pass
    for dec in (base64.b64decode, base64.b85decode):
        try:
            raw = dec(re.sub(rb"\s", b"", data))
        except Exception:
            continue
        for name, blob in unpack(raw):
            try:
                ast.parse(blob.decode("utf-8"))
                found.append((name, blob))
            except Exception:
                pass
    return found


for nb in sorted(glob.glob(os.path.join(BASE, "*", "*.ipynb"))):
    label = os.path.basename(nb)[:-6]
    cells = json.load(open(nb, encoding="utf-8"))["cells"]
    expected = set()
    results = []
    for c in cells:
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"])
        expected.update(re.findall(r"EXPECTED_MAIN_SHA256\s*=\s*['\"]([0-9a-f]{64})", src))
        if src.startswith("%%writefile"):
            first, _, body = src.partition("\n")
            if first.split()[-1].endswith("main.py"):
                results.append(("writefile", (body + "\n").encode("utf-8")))
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            val = literal(node)
            if val is not None and len(val) > 5000:
                results.extend(candidates(val))
    uniq = {}
    for name, blob in results:
        uniq[hashlib.sha256(blob).hexdigest()] = (name, blob)
    main = [(h, n, b) for h, (n, b) in uniq.items() if n.endswith("main.py") or n in ("literal", "writefile", "raw")]
    ok = [(h, n, b) for h, n, b in main if h in expected]
    pick = ok or (main if len(main) == 1 else [])
    if not pick:
        print(f"{label}: 決められない（候補 {[(n, len(b)) for h, n, b in main]}、期待SHA {len(expected)}件）")
        continue
    h, n, b = max(pick, key=lambda x: len(x[2]))
    open(os.path.join(OUT, label + ".py"), "wb").write(b)
    print(f"{label}: {n} {len(b):,} bytes sha {h[:16]} 照合 {'一致' if h in expected else ('期待値なし' if not expected else '不一致')}")
