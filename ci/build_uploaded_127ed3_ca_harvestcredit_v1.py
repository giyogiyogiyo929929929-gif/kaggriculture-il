from pathlib import Path
import hashlib
import sys

PARENT_SHA256 = "87a990786d123112cdd1e34cdaff9e1a390c94ebb078117ee77bea3d8dce27df"
CANDIDATE_SHA256 = "ea296402b43b2e389e2f9cf8a23e27f92434b5b25212c3095f720840d9a91eb0"


def replace_once(src: bytes, old: bytes, new: bytes, label: str) -> bytes:
    count = src.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, got {count}")
    return src.replace(old, new, 1)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: python ci/build_uploaded_127ed3_ca_harvestcredit_v1.py PARENT OUTPUT")
    parent = Path(sys.argv[1]).read_bytes()
    got = hashlib.sha256(parent).hexdigest()
    if got != PARENT_SHA256:
        raise SystemExit(f"parent sha mismatch: {got}")

    newline = b"\r\n" if b"\r\n" in parent else b"\n"
    def block(x: bytes) -> bytes:
        return x.replace(b"\n", newline)

    old_report = block(b'''_CA_REPORT = {"ca_swaps": 0, "ca_rescues": 0, "ca_harvested": 0, "ca_sold": 0, "ca_seed_bought": 0,
              "ca_wheat_seed_saved": 0, "ca_carrot_seed_saved": 0, "ca_feed_block": 0, "ca_errors": 0,
              "ca_min_wheat": 999}''')
    new_report = block(b'''_CA_REPORT = {"ca_swaps": 0, "ca_rescues": 0, "ca_harvested": 0, "ca_sold": 0, "ca_seed_bought": 0,
              "ca_wheat_seed_saved": 0, "ca_carrot_seed_saved": 0, "ca_feed_block": 0,
              "ca_feed_harvest_credit": 0, "ca_errors": 0, "ca_min_wheat": 999}''')
    child = replace_once(parent, old_report, new_report, "report")

    old_need = block(b'''def _ca_feed_need(seat, step, days):
    need = 0
    for t in range(step, min(719, step + 24 * days) + 1):
        act = _ca_tape(seat, t)
        units = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
        need += sum(1 for c in units if c and c[0] == "FEED")
    return need
''')
    new_need = block(b'''def _ca_feed_need(seat, step, days):
    need = 0
    for t in range(step, min(719, step + 24 * days) + 1):
        act = _ca_tape(seat, t)
        units = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
        need += sum(1 for c in units if c and c[0] == "FEED")
    return need


def _ca_wheat_feed_safe(obs, action, seat, step, days):
    """Credit scheduled WHEAT harvests while preserving feed solvency.

    FEED is charged before same-step harvest credit, so this does not rely on
    Kaggriculture's intra-step HARVEST/FEED processing order.
    """
    horizon = min(719, step + 24 * days)
    stock = _ca_wheat_total(obs)
    farm = obs["farms"][seat]
    harvests = {}
    for y, row in enumerate(farm["tiles"]):
        for x, tile in enumerate(row):
            if not (isinstance(tile, dict) and tile.get("crop") == "WHEAT"):
                continue
            planted = int(tile.get("planted_day", -99))
            visits = _ca_visits(obs, action, (x, y), horizon)
            hu, _, _ = _ca_yield_path(
                "WHEAT", planted, visits,
                y0=int(tile.get("yield_units", 0)),
                fert_until=int(tile.get("fertilized_until_day", -1)),
                watered_day=step // 24 if tile.get("watered_today") else -1,
                now_step=step,
            )
            if hu <= 0:
                continue
            ht = next((t for t, _, op in visits if op == "HARVEST"), None)
            if ht is not None:
                harvests[ht] = harvests.get(ht, 0) + hu
    for t in range(step, horizon + 1):
        act = action if t == step else _ca_tape(seat, t)
        units = [act.get("farmer") or ["PASS"]] + list(act.get("hands") or [])
        feeds = sum(1 for c in units if c and c[0] == "FEED")
        if stock < feeds:
            return False
        stock -= feeds
        stock += harvests.get(t, 0)
    return True
''')
    child = replace_once(child, old_need, new_need, "feed helper")

    old_reset = block(b'''                _CA_REPORT.update(ca_swaps=0, ca_rescues=0, ca_harvested=0, ca_sold=0, ca_seed_bought=0,
                                  ca_wheat_seed_saved=0, ca_carrot_seed_saved=0, ca_feed_block=0,
                                  ca_errors=0, ca_min_wheat=999)''')
    new_reset = block(b'''                _CA_REPORT.update(ca_swaps=0, ca_rescues=0, ca_harvested=0, ca_sold=0, ca_seed_bought=0,
                                  ca_wheat_seed_saved=0, ca_carrot_seed_saved=0, ca_feed_block=0,
                                  ca_feed_harvest_credit=0, ca_errors=0, ca_min_wheat=999)''')
    child = replace_once(child, old_reset, new_reset, "report reset")

    old_gate = block(b'''                if wheat_ok is None:
                    wheat_ok = _ca_wheat_total(observation) >= _ca_feed_need(seat, step, _CA_FEED_DAYS)
                if not wheat_ok:
                    _CA_REPORT["ca_feed_block"] += 1
                    break''')
    new_gate = block(b'''                if wheat_ok is None:
                    wheat_now = _ca_wheat_total(observation)
                    wheat_need = _ca_feed_need(seat, step, _CA_FEED_DAYS)
                    wheat_ok = wheat_now >= wheat_need
                    if not wheat_ok and _CA_FEED_DAYS > 0:
                        wheat_ok = _ca_wheat_feed_safe(observation, action, seat, step, _CA_FEED_DAYS)
                        if wheat_ok:
                            _CA_REPORT["ca_feed_harvest_credit"] += 1
                if not wheat_ok:
                    _CA_REPORT["ca_feed_block"] += 1
                    break''')
    child = replace_once(child, old_gate, new_gate, "feed gate")

    child_sha = hashlib.sha256(child).hexdigest()
    if child_sha != CANDIDATE_SHA256:
        raise SystemExit(f"candidate sha mismatch: {child_sha}")
    out = Path(sys.argv[2])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(child)
    print(f"parent_sha256={got}")
    print(f"candidate_sha256={child_sha}")
    print(f"candidate_bytes={len(child)}")


if __name__ == "__main__":
    main()
