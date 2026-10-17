"""Append qualified facts and explicit provenance blockage, retaining old notes."""
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[1]
SECTION='''

## Phase38 — NOR81000 read identified; original payload not qualified

**PROVEN:** Main `$08003A42 → $08005D98` requests exactly23 bytes at external NOR `$81000–$81016`, destination `$2000546C`. Native synchronous wrapper `$08005880` submits a24-byte operation1 record through queue `$20007A60`; Storage TCB `$20007470` dequeues the copy at `$2000742C` and dispatches backend `$08005338 → $080076CC`. DMA has NDTR23, PAR `$A0001020`, M0AR `$2000546C`; native command is `$EC`, AR `$81000`, DLR22. Stock/diagnostic prefix observers preserve the phase37 CPU/SRAM endpoint exactly.

**PROVEN static consumer:** after return, `$08005DB0` overwrites identity-cache byte14 with zero. The later constructor/protocol paths inspect/copy14 alphanumeric identity bytes and register the record pointer for string formatting. **STRONG INFERENCE:** the first14 bytes are a serial/identity string. **UNKNOWN:** exact trailing bytes15–22 semantics and original record contents. Post-read RAM cannot establish the destroyed original byte14.

**PROVEN census; UNKNOWN NOR provenance:** reused1858 existing candidates and33 archive-container records, rehashed22 relevant capture/update files and checked the current project/reference file delta. No candidate proves file offset→physical NOR `$81000` mapping for all23 original bytes. Internal flash/application images, SRAM snapshots, generated reset/diagnostic data and updater metadata at `$80000` are not admitted substitutes. Full source paths, SHA-256 values, address spaces and rejections are recorded in [candidate sources](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase38-nor81000/candidate-sources.md>) and [catalog](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase38-nor81000/candidate-catalog.json>).

**UNKNOWN:** no accepted source/offset/23-byte hex/slice SHA exists. No payload is extracted or injected, no IRQ/completion success is asserted, and no post-consumption checkpoint is claimed. The native DMA/QSPI completion, semaphore release, sync clear and caller-return paths are documented statically but remain unexecuted for this read. The semaphore remains held and Main/request ownership remains retained at the original `$080051C2` boundary.

**PROVEN observed-prefix target `$82000–$821FF` counts:**0 reads /0 writes /0 erase overlaps. **UNKNOWN:** post-read/full-boot counts and H1/H2/P2/P3. P1 remains PROVEN in its previous scope; P4 remains PROVEN unchanged code. H4 remains FAIL in-session; host containment remains PASS. No target data investigation, SDMMC work, firmware generation, hardware access or reference/pinned-source edit occurred.

**UNKNOWN — minimum missing prerequisite:** existing original bytes and acquisition metadata proving exact file-offset mapping to `$81000–$81016`, including byte14. Only then can the native Storage completion experiment proceed. See [phase38 findings](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase38-nor81000/findings.md>), [payload admission](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase38-nor81000/payload-admission.json>) and [validation](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase38-nor81000/validation.json>).

NOR81000 STORAGE READ = UNQUALIFIED
'''
if __name__=='__main__':
 for label,name in (('preservation','qspi82000-preservation-powercycle.md'),('readiness','qspi82000-hardware-readiness.md')):
  before=(O/f'phase37-{label}-before.md').read_bytes();p=R/'notes'/name;after=before+SECTION.encode('utf8')
  assert p.read_bytes() in (before,after),'independent note changes detected';p.write_bytes(after)
 print('Both prior notes retained byte-exact; phase38 provenance gate appended')
