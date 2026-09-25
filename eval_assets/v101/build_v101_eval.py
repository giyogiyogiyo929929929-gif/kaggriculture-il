#!/usr/bin/env python3
from __future__ import annotations
import argparse,base64,gzip,hashlib,shutil
from pathlib import Path
V96_SHA256='dc0938fa82952e6599b04725f1e397ac1f317a0ddffaefbae204e265171b0a22'
V101_SHA256='d3bf7fb94bad629e4b053f5abbe60039fdc741eec8833c4f2418e197d67ade74'
OVERLAY_GZ_B64='H4sIAAAAAAAC/4VUTW/bMAy951dw2MHW5gTJLgO6ZUBRuFiBoi3SoIcZRqDKTCrMkQJJyZr9+lKS54903XyxRD5Sj08UR6P3MKYPDrPpDARXlay4wzMwKPQBDSju5AHhNxo9PkqsK+BKbnkN388XD/n9EpQe650NSUarB8qyujtf5DdLmAPfoHKNcZHf3S68sZLCpeIJxU87n2Z0zi8jHYY1GqMNrdiownWMTvWjRXMgElplILRay83ehO38RitkZyOgjwtvoex9Bv+IZSHKmWMM9591uKMEcnjmZIMuTbwvyWDK2BewyN1buF3Nj2gisk0s103uOUy74/zXV2ay33nh/6vMadZvc/g8+wSabko7kFYq67gSmEZJsqA3G55r0O2NakRrPWtutlRYr6gi8TablIUvumyRO22l91uCFx4SgVR5mcEHv4xyPFE7WVKjKFkXvFfShcBaWtewjPAmB/PFFMnd+f19UjJKGJGC+Zp7BYrM2xlgbbHFw5qCBd0ODFJHJjEzkenYCPJssCI+l5zydGIQUvo0xvvTrVRpjSoN5ImTX7cqMHaiL/EMwEKW8I4qTZq3kpRDXCCglZNqj282RpHElqDaPs5hNsA9Z8emFVsydGYx9bK9ss5KNgh2skaKjvfnN/6ij2XxXJ4Wk/ZU98CmqWgSVCFL1DjOhSSYX5Xp2XTQMEhWQaP4WOArPY6TfGs0tJE0eVb8wGXNH2tMTqVuO8pr7aW+uL2+zi+Wq8t8sby6vvqRL5LyVcRQ3z8P7W8KD3tkaXoXRcI0niGldhaFSRd3NDfionspBIjEp2XnjH3a+WZnkTw+C9w5yMOPkN2Jw1LinOgXMnzrYaZOHNa4RZp+7cCM8aMX2Ms3XA4GAAA='
def sha256(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--v96',required=True);ap.add_argument('--out-dir',default='eval_agents/v101');args=ap.parse_args()
 src=Path(args.v96);out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)
 if sha256(src)!=V96_SHA256:raise RuntimeError(f'v96 sha mismatch {sha256(src)}')
 dst=out/'v101_candidate_zero_yield_harvest_fertilizer.py';shutil.copyfile(src,dst)
 with dst.open('ab') as f:f.write(gzip.decompress(base64.b64decode(OVERLAY_GZ_B64)))
 if sha256(dst)!=V101_SHA256:raise RuntimeError(f'v101 sha mismatch {sha256(dst)}')
 compile(dst.read_text(encoding='utf-8'),str(dst),'exec');print('v101',sha256(dst));return 0
if __name__=='__main__':raise SystemExit(main())
