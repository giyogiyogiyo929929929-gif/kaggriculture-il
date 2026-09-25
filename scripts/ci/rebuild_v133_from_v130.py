#!/usr/bin/env python3
from __future__ import annotations
import base64,gzip,hashlib,shutil,subprocess,tempfile,os
from pathlib import Path
V133_SHA256='114d765d37875afb252466f25381dc3d44ee5c92466f96e638c365d26b691d40'
PATCH='H4sIAB9KtmoC/41TbWvbMBD+vPyKgzFsE9uxnZcuZikJa7fBBhtt2T4YIxT74pgqkivJacLYf59kd+toA919sCXd3XN3z90FQQCjHdejkmo6uqVVJeuiZbqVSHBP2WgfjyNSUF7WxgIJsx8t7jkpJb0nlbkmk7A5vkqiZBZE8yCZQvQ2jSbpdBLGk3E8jpNoAsPIyGA4HL4YbEwK5BolEZwdnwLP03GURuNwHs/m8XQ2mz4AL5cQjKezMz82ofpDAsvlAJ5KvYG78yhtGOUhbRrkpetqX2Rx7t95Xm//GvZxMk+h5SVKoMCorBBs4dC0a1YXUFC1BYa09KEUwIU2CsaMqSq2WLYMS1CU4R84WkihlFFb3oJCcNXuGl0LDroubmEjJOgt1VBr3IXwGbEBauCE3pr4Fghouae8QBUOgocqlMbmfDE9OwPTGiCri+/ky+rmklxcrX6Qj+YUVqhdU+cRpf+BMoVeOhiedLa3d7P57P+ROkt3wwTVrlirzNlQuVNOnvVWeebsBMejk3vBCaM4eGZmkjFtDCOT499WEbUVjVrotmHoWoQuD8dy6Pg/f3lgaDO//rXlTBS3WPZOjp/lnd78HgFL3EA/tWs0nCMpW3Qt5745/BvZim1KCzUHSXmFruXolNkDoe2bZLJYRCeUViSaCedwI1vs+/fM2zp3pFJ+7FKykcnV6v0luf709dt1V6TyXc/rElOduivVJBS8FPOUomvko8YuxCI7dOgHi24fbG52uJ+RdrD7csii3MsfVyZOUtiYnal5FdB7Ks22SKGx6AbdLrOFNSNt5o2uGXZjF8Swq6U0QSVW9Q7DwW/UCNUVkAQAAA=='
def main():
    src=Path('eval_agents/v130/v130_candidate_late_town_draw_gate24.py'); dst=Path('eval_agents/v130/v133_candidate_center_only.py')
    shutil.copyfile(src,dst); raw=gzip.decompress(base64.b64decode(PATCH))
    with tempfile.NamedTemporaryFile(suffix='.patch',delete=False) as f: f.write(raw); name=f.name
    try: subprocess.run(['patch','--batch','--silent',str(dst),name],check=True)
    finally:
        try: os.unlink(name)
        except OSError: pass
    got=hashlib.sha256(dst.read_bytes()).hexdigest()
    if got!=V133_SHA256: raise RuntimeError(f'v133 sha mismatch: {got}')
    compile(dst.read_text(encoding='utf-8'),str(dst),'exec'); print(got)
if __name__=='__main__': main()
