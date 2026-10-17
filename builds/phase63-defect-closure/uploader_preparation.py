"""Hash-bound OFFLINE-LOCKED review copy; never opens a browser or MIDI."""
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
c=json.loads((O/'development-identity.json').read_text());raw=(O/'rollback/ct_uploader-reference-pinned.html').read_bytes();assert sha(raw)=='c5d6bb67cd92720eac89d609ebaafc803902d28356840ae61691dd5987b43a6f'
s=raw.decode('utf-8');start=s.index('const KNOWN = {');end=s.index('\n};',start)+3
allowed={c['SYX_sha256']:'Phase63 DEVELOPMENT ONLY — OFFLINE LOCKED'}
for n in ['circuittracks-firmware-4486-STOCK.syx','circuittracks-B1.3-manifest-matched.syx']:allowed[sha((O/'rollback'/n).read_bytes())]=n
s=s[:start]+'const PREFLIGHT_QUALIFIED = false;\nconst KNOWN = '+json.dumps(allowed,ensure_ascii=False,indent=2)+';'+s[end:]
for anchor in ['$("btnMidi").onclick = async () => {','$("btnId").onclick = () => {','$("btnSend").onclick = () => {']:
 assert anchor in s;s=s.replace(anchor,anchor+'\n  if (!PREFLIGHT_QUALIFIED) throw Error("OFFLINE LOCK: candidate not qualified");',1)
s=s.replace('<h1>Circuit Tracks Uploader</h1>','<h1>Phase63 OFFLINE REVIEW ONLY — MIDI LOCKED</h1>')
name='ct_uploader-phase63-offline-locked.html';(O/name).write_text(s,encoding='utf-8')
(O/'uploader-binding.json').write_text(json.dumps(dict(confidence='PROVEN',candidate_SYX_sha256=c['SYX_sha256'],uploader=name,uploader_sha256=sha((O/name).read_bytes()),upstream_filename='ct_uploader.html',upstream_version='no explicit semantic version; exact file SHA pinned',upstream_sha256=sha(raw),allowlist=allowed,live_enabled=False,hardware_test_eligible=False,product=[1,100],manufacturer_header=[240,0,32,41,0],command_order=['0x71','0x7c','0x72 repeated','0x73'],header_marker='N63DEV',header_native_comparison=['0x080101c8','0x080101ee'],image_bytes=c['BIN_bytes'],CRC=c['CRC'],requires_new_reviewed_uploader_hash_before_any_future_hardware_action=True),indent=2)+'\n')
print('Uploader identity bound; all MIDI/identify/send handlers locked')
