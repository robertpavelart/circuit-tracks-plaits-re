"""Runtime bindings for the exact integrated image; no code patching here."""
from environment import *
L={k:int(v,16) for k,v in json.loads((O/'integration.json').read_text())['layout'].items()}
COMMAND=L['command'];CRC_UPDATE=L['crc'];DRAIN=L['drain'];TEMPLATE=L['template']
FRAME=188;RAW=32;PACKET=16;GUARDS=(12,180)
def load(u):return dict(exact_image=True,frame_bytes=FRAME,payload_offset=RAW,packet_offset=PACKET)
