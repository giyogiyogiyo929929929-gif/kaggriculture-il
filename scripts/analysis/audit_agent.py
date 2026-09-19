# -*- coding: utf-8 -*-
"""埋め込み（exec される）ソースまで再帰的にたどって、危ない import・呼び出しが無いか確かめる。

ファイル内の長い文字列・バイト列の定数を、そのまま / b85・b64 → zlib・gzip の順で Python として読めるか試し、
読めたものを同じ方法で再帰的に調べる。実行はしない。

仕様: docs/05_evaluation.md §8（分析ツール）
使い方:
    .venv\\Scripts\\python.exe scripts\\analysis\\audit_agent.py <main.py>...
v9/4 系は `open(path)`（環境変数 V92_SELL_LIB があるときだけ読む開発用の処理）が1件出るのが正常。
"""
import ast
import base64
import gzip
import os
import sys
import zlib

sys.stdout.reconfigure(encoding="utf-8")
RISKY_MODULES = {"subprocess", "socket", "urllib", "requests", "http", "shutil", "ctypes", "multiprocessing",
                 "pickle", "marshal", "importlib", "sys", "builtins", "threading", "asyncio", "pathlib", "tempfile"}
RISKY_CALLS = {"system", "popen", "urlopen", "Popen", "rmtree", "unlink", "rmdir", "__import__", "open"}


def candidates(text):
    """文字列から Python ソースを復元できる候補を返す。"""
    if isinstance(text, bytes):
        variants = [text]
    else:
        variants = [text.encode("utf-8", "ignore")]
        yield text
    for raw in variants:
        for dec in (lambda b: b, base64.b85decode, base64.b64decode):
            try:
                data = dec(raw)
            except Exception:
                continue
            for unz in (lambda b: b, zlib.decompress, gzip.decompress):
                try:
                    out = unz(data)
                except Exception:
                    continue
                try:
                    yield out.decode("utf-8")
                except Exception:
                    pass


def audit(code, where, depth=0, seen=None):
    seen = seen if seen is not None else set()
    key = hash(code)
    if key in seen or depth > 6:
        return []
    seen.add(key)
    try:
        tree = ast.parse(code)
    except Exception:
        return []
    problems = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] in RISKY_MODULES:
                    problems.append((where, depth, node.lineno, f"import {a.name}"))
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in RISKY_MODULES:
                problems.append((where, depth, node.lineno, f"from {node.module} import"))
        elif isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
            if name in RISKY_CALLS:
                problems.append((where, depth, node.lineno, f"call {name}: {ast.unparse(node)[:90]}"))
        elif isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes)) and len(node.value) > 400:
            for inner in candidates(node.value):
                if "def " in inner or "import " in inner:
                    problems += audit(inner, f"{where}>L{node.lineno}", depth + 1, seen)
    return problems


def audit_file(path):
    code = open(path, encoding="utf-8").read()
    problems = audit(code, os.path.basename(path))
    return problems


if __name__ == "__main__":
    for path in sys.argv[1:]:
        problems = audit_file(path)
        print(f"== {os.path.basename(path)}: 注意 {len(problems)}件")
        for where, depth, line, what in problems[:15]:
            print(f"   [{where} 深さ{depth} L{line}] {what}")
