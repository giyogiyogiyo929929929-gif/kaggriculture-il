from pathlib import Path
import sys

OVERLAY = r'''
# ---- v151 safety wrapper: preserve v150 on all normal observations ----
_V151_PARENT = agent

def agent(observation, configuration=None):
    if observation is None:
        return {'farmer': ['PASS'], 'hands': [], 'market': []}
    return _V151_PARENT(observation, configuration)

kaggle_submission_agent_v151 = agent
'''

if __name__ == '__main__':
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    dst.write_bytes(src.read_bytes() + b'\n' + OVERLAY.lstrip('\n').encode('utf-8'))
