from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

V153_SHA256 = "128836e8e945d9b5b8c6776dc68cd45f4c21775713ebd3bd50655cd2f711ebfd"
OLD = "if st['confirmed'] and not st['rejected'] and _v105_standard(configuration) and _v44y_clone_gate(observation):"
NEW = "if parent_changed and st['confirmed'] and not st['rejected'] and _v105_standard(configuration) and _v44y_clone_gate(observation):"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("output")
    args = ap.parse_args()

    src = Path(args.source)
    dst = Path(args.output)
    got = hashlib.sha256(src.read_bytes()).hexdigest()
    if got != V153_SHA256:
        raise SystemExit(f"v153 sha mismatch: {got}")

    text = src.read_text(encoding="utf-8")
    count = text.count(OLD)
    if count != 1:
        raise SystemExit(f"expected exactly one v153 second-pass guard, found {count}")
    if "_V153_PARENT = agent" not in text:
        raise SystemExit("required v153 wrapper marker missing")

    text = text.replace(OLD, NEW, 1)
    text += "\n# v157: runtime-v150 rebased onto exact v153; skip redundant second pass only when parent_changed is false.\nkaggle_submission_agent_v157 = agent\n"
    dst.write_text(text, encoding="utf-8")

    print("source_v153_sha256=" + got)
    print("candidate_sha256=" + hashlib.sha256(dst.read_bytes()).hexdigest())
    print("change=runtime-only parent_changed guard on existing second pass")


if __name__ == "__main__":
    main()
