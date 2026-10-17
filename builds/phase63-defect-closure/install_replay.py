from pathlib import Path
import sys
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
s=(R/'builds/phase62-final-preflight/corrected_install_replay.py').read_text().replace("frozen-candidate-identity.json","development-identity.json")
exec(compile(s,str(O/'selected-install-replay.py'),'exec'),dict(__file__=str(O/'install_replay.py'),__name__='__main__'))
