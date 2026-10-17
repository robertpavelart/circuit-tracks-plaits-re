> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase67 — final safety disposition

**STRONG INFERENCE — B. Only hardware/model coverage uncertainty remains in the scoped controller-READY → host configuration → authorization → capture-entry path.** No concrete firmware defect or known offline software blocker was demonstrated. Further peripheral emulation has diminishing safety value. This disposition closes the requested safety-relevance triage; it does not assert physical enumeration, authenticated physical NOR contents, unlimited runtime coverage, or authorize hardware access.

## Evidence and method

**PROVEN:** unchanged Phase63 application SHA-256 `edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9`. No firmware was generated or modified. `audit.py` disassembles those exact bytes; `callbacks.py` creates a separate bounded call fixture from Phase66 `frontier-sram.bin`. This SRAM clone is **not** a restored CPU/peripheral checkpoint and is not described as uninterrupted startup continuity. The completed Phase66 prefix is preserved, not rerun.

**PROVEN in the declared fixture:** `callback-results.json` records native SET_ADDRESS(1), SET_CONFIGURATION(1), repeated configuration(1), deconfiguration(0), reconfiguration(1), geometry query, rejected wrong-session authorization, rejected wrong-geometry authorization, and accepted same-epoch authorization reaching `$08070B00`. All pass. Configuration never changes the 12-byte record or adjacent 220-byte Master FX allocation. There are zero calls to either observed allocator entry `$0801CFA4` or `$0801D7D8`; heap cursor remains `$20044D68`. NOR-mutation entry guards never fire.

**PROVEN model boundaries:** SET_ADDRESS hardware action `$08024738`, control-status `$0803B7D4`, endpoint open/close/flush `$08024668/$080246A8/$080246C4`, router output `$08020C90`, diagnostic output-drains `$08071D00/$08074700` return modeled success. A passive USB register shadow permits native receive-arm metadata/register writes; it generates no interrupts, packets, acknowledgements or completion. Configuration state is written by native standard-request code, not injected by the fixture. The raw function is stopped **at entry**, before its first instruction or physical-read submission. The earlier failed fixture access at `$08048730` is retained in `initial-usb-register-boundary.json`; it was an unmapped USB endpoint register in this new fixture, not a firmware defect. No DWT behavior was added.

## Local path and ownership

| Path/resource | Finding | Confidence |
|---|---|---|
|Configuration dispatch|`0803A784` handles standard requests; SET_ADDRESS body `0803A928` sets addressed state2. SET_CONFIGURATION body `0803A966` invokes `08037F30` → class Init; deconfiguration invokes `08037F46` → DeInit. Native state3 means configured.|PROVEN by exact listing and bounded execution|
|Registered objects|Boot-derived device `$20005558`, table pointer at device+`28C`, class wrapper `080228A8`; global `$20006A14` → composite `$200000CC`; children `$200000EC/$200000F8`, tables `$0805A444/$0805A480`. Config dispatch `0803649E` → `08047C88` uses those existing objects.|PROVEN|
|Class initialization|First child `0805B568` → `08020B98/08020E88` services existing port objects. Second child `08058EB0` → `08026DA8/08026D64` initializes BOT metadata/arms its existing command buffer. DeInit `08058EC2` clears BOT state. No heap request occurs in tested config/deconfig/reconfig closure.|PROVEN scoped execution|
|Data receive|`0803803C`, nonzero endpoint arm near `080380E0`, calls class+`14`; wrapper `080228D6` → `08036566` → `08047D64`. Endpoint ingress `0801E614/0801E624` and `0801E662` use existing endpoint/ring storage. `0801D82C` checks available ring space then copies length/data; no allocation. Parser `0801EB30` dispatches the diagnostic in Main.|PROVEN local code; full real bus-to-Main scheduling UNKNOWN|
|Diagnostic RAM|Record `$20044D70-$20044D7B` changes only as required in the tested query/authorization: `11` → session37 EXPORTED `4A000012` → ACTIVE `13`. Adjacent Master FX bytes remain equal. Native configuration leaves all 232 bytes equal.|PROVEN scoped execution|
|Geometry/lifecycle and session|Query exports existing geometry; wrong session/geometry do not advance state. Correct authorization at `08070500` stores mask2/session37/deadline and reaches raw entry. It deliberately overlays exported geometry with active-session fields; that is expected ownership, not corruption.|PROVEN scoped execution|
|Raw buffer|No USB configuration allocation supplies raw storage. `08070B00` uses its dedicated 260-byte Main frame, payload at R7+192..255. Phase63's fence holds that frame while DMA/request/backend ownership remains active. No USB packet aliases this buffer by the reviewed fixed layout.|PROVEN code and prior scoped tests; physical scheduling/headroom UNKNOWN|
|NOR write/erase|Configuration and diagnostic query/authorization add no mutation operation. Raw entry admits fixed reads only. Composite USB is not globally storage-free: its separate BOT/SCSI command surface can reach storage. Existing Phase46–61 mutation/geometry admission evidence remains applicable; no claim is made that arbitrary host storage commands are harmless.|PROVEN separation; no new corruption path found, STRONG INFERENCE for composed normal path|
|Bootloader/rollback|These local callbacks do not select firmware-update mode or program internal flash. Candidate files and historical install/rollback evidence remain byte-identical. Ordinary USB initialization is not itself rollback proof.|PROVEN local code/preservation; physical rollback UNKNOWN|

## Postboot allocation disposition

**PROVEN:** Phase66 completed 3,186 allocator returns across two layers, with zero failures/overlaps. Phase67 adds zero allocations for the actual registered class Init/DeInit callbacks, repeated configuration, native query and authorization through raw entry. RX ring/parser/endpoint buffers already exist in the saved boot-derived RAM. New diagnostic capture workspace is stack-local, not another bump allocation. Configuration, query and authorization therefore introduce no later heap-allocation class in this scoped fixture.

**PROVEN local allocator constraint:** `0801D7D8` rounds the request to four bytes, compares the prospective cursor with the cap loaded through `$20002B44`, updates `$20002B48` only on admitted size, and otherwise hits BKPT/returns `FFFFFFFF`. This is a bounded allocator, not a guarantee of future successful requests. The eight-byte observed cursor/cap gap is not free stack space or evidence that arbitrary later feature allocations succeed. No arbitrary-size/wrapped request theorem is asserted.

**STRONG INFERENCE:** the remaining real enumeration timing does not create a new overlapping allocation class on the reviewed one-shot path: native configuration callbacks reuse existing objects; ingress uses bounded existing rings; diagnostic code requests no heap storage. This is sufficient for safety-relevance disposition, not a proof of every possible postboot feature lifetime.

**UNKNOWN — MODEL COVERAGE LIMITATION / HARDWARE-ONLY UNKNOWN:** real host enumeration/USB IRQ and Main interleavings, real device stack high-water mark, PHY/cache/bus timing, physical completion/error behavior, and authenticated current-unit NOR contents. Synthetic startup coefficient bytes remain synthetic. The native continuity run still stops at DWT; Phase67 does not replace that fact with a fabricated continuous trace.

## Decision and remaining boundary

**STRONG INFERENCE — B:** no identified software mechanism in the remaining scoped gap plausibly overwrites reserved diagnostic state or invalidates the existing ownership design before authorized capture. Configuration and authorization legitimately affect their own metadata/state, as enumerated above. Actual timing and physical success remain UNKNOWN. Further peripheral emulation has diminishing safety value; no full USB or DWT model is warranted by these findings.

**PROVEN:** the prior no-bounded-unwind limitation remains: failure means no retry, no forced semaphore release, retained ownership/quarantine until power cycle. This was not repaired or reclassified as bounded recovery. Existing Phase63 31 DMA ownership, 32 host containment, 13 lifecycle/status, 28 native, seven reservation and three install/rollback cases are preserved evidence, not newly rerun tests.

**PROVEN:** no hardware, MIDI ports, transmission, reference modifications or candidate changes in this phase. Historical reports retain their original verdicts. This report supersedes only their remaining USB/postboot *safety-relevance disposition*, not their missing physical/continuous-execution coverage or publication permissions. No hardware action follows this result.

FINAL PREFLIGHT CLOSURE = PASS
