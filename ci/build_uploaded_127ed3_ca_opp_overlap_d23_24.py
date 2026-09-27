from pathlib import Path
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PARENT_SHA256 = "87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df"
OLD = b'if _CA_FROM <= day <= _CA_TO and pays_now:'
NEW = b'if _CA_FROM <= day <= _CA_TO and pays_now and not (23 <= day <= 24 and any(isinstance(_tt, dict) and _tt.get("crop") == "CARROT" for _row in observation["farms"][1 - seat]["tiles"] for _tt in _row)):'


def build(parent_path: Path, output: Path) -> str:
    parent = Path(parent_path).read_bytes()
    got_parent = hashlib.sha256(parent).hexdigest()
    assert got_parent == PARENT_SHA256, got_parent
    assert parent.count(OLD) == 1, parent.count(OLD)
    child = parent.replace(OLD, NEW, 1)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(child)
    return hashlib.sha256(child).hexdigest()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: build_uploaded_127ed3_ca_opp_overlap_d23_24.py PARENT.py OUTPUT.py")
    sha = build(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"sha256={sha}")
