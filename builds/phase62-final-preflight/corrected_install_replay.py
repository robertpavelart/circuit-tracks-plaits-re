"""Exact frozen corrected SYX through selected native installed updater.
Checks every staging instruction against CURRENT, not a stock updater proxy.
"""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];c=json.loads((O/'frozen-candidate-identity.json').read_text());name=c['candidate']
src=(R/'builds/phase44-preflash-redteam-closure/transition_replay.py').read_text()
src=src.replace("candidate = ((O/'circuittracks-4486-nor-evidence-atomic-test.bin') if atomic else (S/'circuittracks-4486-nor-evidence-test.bin')).read_bytes()",f"candidate = (O/'{name}.bin').read_bytes()")
src=src.replace("stream = ((O/'circuittracks-4486-nor-evidence-atomic-test.syx') if atomic else (S/'circuittracks-4486-nor-evidence-test.syx')).read_bytes()",f"stream = (O/'{name}.syx').read_bytes()")
src=src.replace("stream = (S/'rollback/circuittracks-firmware-4486-STOCK.syx').read_bytes()","stream = (O/'rollback/circuittracks-firmware-4486-STOCK.syx').read_bytes()")
src=src.replace('stream = ct_fw.encode(b13)',"stream = (O/'rollback/circuittracks-B1.3-manifest-matched.syx').read_bytes()")
src=src.replace('executed=set();version_decisions=[]','executed=set();version_decisions=[];selector_witness=[]')
src=src.replace('executed.add(pc)',"executed.add(pc)\\n if phase=='application staging' and pc==0x080390d0:selector_witness.append(dict(pc=hex(pc),index=reg(0),table_address=hex(reg(2)),selected_pointer=hex(e.r32(reg(2)+4*reg(0))),selector_record_bytes=bytes(u.mem_read(0x20003c88,0x50)).hex()))\\n if phase=='application staging' and 0x08010000<=pc<0x08010000+len(CURRENT):assert bytes(u.mem_read(pc,n))==CURRENT[pc-0x08010000:pc-0x08010000+n],('wrong installed updater instruction',hex(pc))")
src=src.replace("table = ns['u'].mem_read(0x08039180,0x100)","table = current[0x29180:0x29280]")
src=src.replace("selector=0,staging_base='0x0',capacity='0x80000',","selector=0,staging_base='0x0',capacity='0x80000',actual_installed_instruction_bytes_checked=True,updater_code_window_source_image_sha256=hashlib.sha256(current).hexdigest(),updater_code_window_address='0x08039180',updater_code_window_sha256=hashlib.sha256(table).hexdigest(),actual_RAM_selector_witness=ns['selector_witness'],")
exec(compile(src,str(O/'selected-corrected-install-runner.py'),'exec'),dict(__file__=str(O/'corrected_install_replay.py'),__name__='__main__'))
