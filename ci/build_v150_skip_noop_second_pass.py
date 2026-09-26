from pathlib import Path
import sys

OLD = "if st['confirmed'] and not st['rejected'] and _v105_standard(configuration) and _v44y_clone_gate(observation):"
NEW = "if parent_changed and st['confirmed'] and not st['rejected'] and _v105_standard(configuration) and _v44y_clone_gate(observation):"

if __name__ == '__main__':
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    text = src.read_text(encoding='utf-8')
    count = text.count(OLD)
    if count != 1:
        raise RuntimeError(f'expected exactly one v147 second-pass guard, found {count}')
    text = text.replace(OLD, NEW, 1)
    text += '\n# v150: skip provably redundant second pass when parent v111 made no change.\nkaggle_submission_agent_v150 = agent\n'
    dst.write_text(text, encoding='utf-8')
