from pathlib import Path
import hashlib
import sys

PARENT_SHA = "127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652"
CANDIDATE_SHA = "e2d48abbfff9c885cefe80d6b746ec54870341284117e1f8d5436a3393b7c490"


def crlf(s: str) -> bytes:
    return s.replace("\n", "\r\n").encode("utf-8")


def once(data: bytes, old: str, new: str) -> bytes:
    ob, nb = crlf(old), crlf(new)
    n = data.count(ob)
    if n != 1:
        raise RuntimeError(f"expected one exact replacement, got {n}: {old[:60]!r}")
    return data.replace(ob, nb)


def build(src: Path, dst: Path) -> None:
    data = src.read_bytes()
    got = hashlib.sha256(data).hexdigest()
    if got != PARENT_SHA:
        raise RuntimeError(f"parent sha mismatch: {got}")

    data = once(data, '''def _mpx_draw_units(item, step):
    # town draw cadence: shops every 4 steps, center every 24
    draw = 0
    if step % 4 == 0:
        draw += 1
    if step % 24 == 0:
        draw += 1
    return draw
''', '''def _mpx_draw_units(item, step, shops):
    # Reuse the proven v9 item/shop-specific town-consumption model.
    # This distinguishes shop type and multiplicity (e.g. two YARN_STORE instances).
    return int(_v9_town_draw(list(shops or ()), step).get(item, 0))
''')

    data = once(data,
'''            d = inv_now[i] - prev["inv"][i] + _mpx_draw_units(i, step - 1) - prev["own"].get(i, 0)
''',
'''            d = inv_now[i] - prev["inv"][i] + _mpx_draw_units(i, step - 1, prev.get("shops", ())) - prev["own"].get(i, 0)
''')

    data = once(data,
'''    hist["prev"] = {"step": step, "inv": inv_now, "own": {}}
''',
'''    hist["prev"] = {"step": step, "inv": inv_now, "own": {},
                    "shops": list(observation["town"]["unlocked_shops"])}
''')

    data = once(data,
'''            inv_next = inv + rival_avg + planned - _mpx_draw_units(item, step)
''',
'''            inv_next = inv + rival_avg + planned - _mpx_draw_units(item, step, observation["town"]["unlocked_shops"])
''')

    got = hashlib.sha256(data).hexdigest()
    if got != CANDIDATE_SHA:
        raise RuntimeError(f"candidate sha mismatch: {got}")
    dst.write_bytes(data)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: build_uploaded_127ed3_mpx_shopdraw.py PARENT OUT")
    build(Path(sys.argv[1]), Path(sys.argv[2]))
