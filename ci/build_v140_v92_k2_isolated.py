from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

OLD = "votes = sum(1 for ev in best if ev.get((step + 1, i), 0) + ev.get((step + 2, i), 0) >= _V92_P_K)"
NEW = "votes = sum(1 for ev in best if ev.get((step + 1, i), 0) + ev.get((step + 2, i), 0) >= 2)"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("output")
    args = ap.parse_args()

    source = Path(args.source)
    output = Path(args.output)
    text = source.read_text(encoding="utf-8")

    # Important: do NOT change _V92_P_K itself.  That constant is also reused
    # by the later KIL v52 copy-preempt path.  v139 changed both paths at once;
    # v140 isolates only the primary _v92_predict quantity gate.
    count = text.count(OLD)
    if count != 1:
        raise SystemExit(f"expected exactly one primary V92 vote expression, found {count}")
    if text.count("_V92_P_K = 1") != 1:
        raise SystemExit("exact v115 K constant not found uniquely")

    text = text.replace(OLD, NEW, 1)
    output.write_text(text, encoding="utf-8")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(f"v140_sha256={digest}")
    print(f"v140_bytes={output.stat().st_size}")
    print("change=primary _v92_predict threshold only: >= _V92_P_K(1) -> >= 2")
    print("kil_v52_shared_constant_preserved=_V92_P_K = 1")


if __name__ == "__main__":
    main()
