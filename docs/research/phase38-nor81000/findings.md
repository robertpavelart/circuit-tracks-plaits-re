> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase38 — exact NOR $81000 Storage read, provenance gate

**PROVEN:** the blocked request is exactly a23-byte read of physical external NOR `$81000,$81017)` into SRAM `$2000546C`. The native caller, queue copy, Storage dequeue and DMA/controller setup are traced in both stock and diagnostic without changing the phase37 CPU/SRAM endpoint. **UNKNOWN:** no existing source establishes the original23 NOR bytes with a proven file-offset mapping. Consequently no payload is extracted or supplied, and no read completion is manufactured. The result is UNQUALIFIED because input provenance is missing, not because the native architecture was disproved.

## Exact request and ownership

**PROVEN:** [stock-request.json (local-only reference: `builds/phase38-nor81000/stock-request.json`; not distributed) `read_events` follows actual reset→Main→UI→Storage execution. `request_trace.py` only observes the already-qualified phase37 runner. Its four exception/runner support files are byte-exact copies; bounded peripheral hooks are retained and no RAM access hook is added.

| Item | Native evidence |
|---|---|
| requesting Main routine | `$08003A42 BL $08005D98` |
| read arguments at `$08005DAC` | wrapper=`$20007A44`, source=`$81000`, destination=`$2000546C`, length=`$17` |
| wrapper vtable / read slot | `$08009598`, +$0C → `$08005881` (entry `$08005880`) |
| original request lifetime |24-byte Main-stack record at `$20006410`, retained while synchronous call waits |
| submission | `$080058A4 → $080056B8`; queue operation `$080056C8 → $08007A64` |
| queue / backing storage | `$20007A60 / $20007A6C` |
| notifying object | wrapper+$14=`$20006E64`, the native Storage task argument/object; submit calls `$0800469C` with flag1 |
| Main wait | wrapper vtable+$18 → `$08005726`; native sync word wrapper+$10 is1 while waiting |
| Storage entry | `$08009202`, TCB `$20007470`; native loop invokes `$08005764` |
| dequeue | `$080057AC → $08007A8E`, local Storage-stack request `$2000742C` |
| dispatch | `$080057BA–$080057E6`, read operation1 selects backend vtable+$0C |
| backend object / vtable / method | `$200003DC / $080095C0 / $08005338` |
| physical NOR driver | backend+$4=`$20000010`; `$0800536A → $080076CC` |
| source / destination / bytes | `$81000 / $2000546C / 23`, also verified in DMA/controller registers |

**PROVEN:** the original Main record and the dequeued Storage copy match all24bytes, including null callbacks:

| Offset | Field value |
|---|---|
| +0, uint16 | operation1 (read) |
| +2, uint16 | option0 |
| +4, uint32 | source `$00081000` |
| +8, uint32 | destination `$2000546C` |
| +$0C, uint32 | length23 |
| +$10, uint32 | callback0 |
| +$14, uint32 | callback context0 |

The raw request is `01000000001008006c540020170000000000000000000000`. `original_request_address` records the actual Main stack location; `$2000742C` is the dequeued copy, not a request pointer borrowed from another task. The destination is a static global record; no raw NOR bytes are yet present there. Its fresh zero contents are **not** accepted as evidence that NOR contains zeros.

**PROVEN:** backend semaphore byte `$200003E4` changes1→0 in the native acquisition path `$08005346–$08005364`. At the boundary it remains held. Controller setup issues opcode `$EC`, AR=`$81000`, DLR=22, CCR=`$07183FEC`, stopping at `$080051C2` immediately after native `$080051C0` writes AR. DMA stream registers prove NDTR=23, PAR=`$A0001020`, M0AR=`$2000546C`, and EN=1. Wrapper sync remains1, request/caller frames remain live, and no release, retry or destination injection occurs.

## Consumer and meaning

**PROVEN by native code:** 08003a10.asm (local-only reference: `builds/phase38-nor81000/08003a10.asm`; not distributed) calls this read before constructing a protocol/identity object and registering the returned record pointer. 08005d78.asm (local-only reference: `builds/phase38-nor81000/08005d78.asm`; not distributed) shows `$08005D98` and the separate writer `$08005DB4` using exactly the same23-byte range. The writer dispatches a write-with-erase option for the record; it is **not executed** in this experiment.

**PROVEN static post-read behavior:** `$08005DB0 STRB` overwrites record byte14 (`$2000547A`) with zero immediately after the synchronous read returns. `$08003A5A → $08005DD8` stores the record pointer in object+$8 and examines up to14 alphanumeric bytes. The protocol handler `$08005E10` can return14 bytes from that pointer (`$08005E7A–$08005E82`); update helper `$08005E88` validates/copies14 characters then invokes the registered writer callback. `$08003A66 → $08005F9A` registers this record pointer via global `$20000984`; `$08005F2C` uses it in the string-descriptor path and has a chip-ID fallback when no pointer is registered. See 08005dd8.asm (local-only reference: `builds/phase38-nor81000/08005dd8.asm`; not distributed), 08005edc.asm (local-only reference: `builds/phase38-nor81000/08005edc.asm`; not distributed) and 08005f4c.asm (local-only reference: `builds/phase38-nor81000/08005f4c.asm`; not distributed).

**STRONG INFERENCE:** the record's first14 bytes are the device's alphanumeric identity/serial string; byte14 becomes its terminator in RAM. **UNKNOWN:** exact semantic purpose of bytes15–22 and their original contents. This focused boot path does not establish a checksum/version/install format for them. The normal updater's distinct23-byte record at `$80000` is not this identity record.

**UNKNOWN dynamic consumer result:** none of those post-completion consumers is executed with a substituted record. Static interpretation does not establish the raw NOR contents or the historical origin of a RAM snapshot.

## Candidate sources and mapping decision

**PROVEN file census:** candidate-catalog.json (local-only reference: `builds/phase38-nor81000/candidate-catalog.json`; not distributed) reassesses the existing1858-candidate project census for **$81000**, rather than repeating unrelated investigations. It preserves every full path, file SHA-256, documented base/address-space, provenance and rejection decision. The prior33-container archive catalog is referenced by hash. A fresh `rg --files` delta scan of the project/reference roots finds only five additional generated diagnostic/test/code artifacts, none a physical capture. Twenty-two relevant capture/update files are rehashed and match the old census. [candidate-sources.md](<candidate-sources.md>) lists each focused candidate's full path, full hash, mapping evidence and decision.

**PROVEN / UNKNOWN distinction:** a verified file/Git hash proves byte identity; it does not prove external NOR origin. Mappings below come from existing loader/producer code, never filenames:

- Internal flash dump `.../ctre/Firmware-Analysis/dumpCT_flash_0x08000000.bin`, SHA-256 `f3d85d64c9ead9205e5336dff49bb51f21d270ffa29b47c6f6971125d6d848a8`: loader assigns CPU flash base `$08000000`; not external NOR. `$81000` has no accepted NOR offset in it.
- Firmware RAM dump `.../ctre/Firmware-Analysis/ram_dump_firmware_0x08037988.bin`, SHA-256 `26a29670c0c1918217b7eadf8f89fe6df97994d3cc6e1c0ed65ac522e161094c`: loader assigns SRAM base `$20000000`; no historical original-NOR mapping is established.
- RAM dump `.../ctre/Firmware-Analysis/dumpCT_ram_0x20000000.bin`, SHA-256 `ebd902ba8a653748fea720af567cc95bcd893f3920f3a2fae5932bdff213efa2`: separate loader proves SRAM base, not NOR source. Even a later identity cache cannot prove the original byte14 because the reader destroys that byte.
- `.../ctre/Firmware-Analysis/ram_dump_boorloader_0x08003bc6.bin`, SHA-256 `9eaa992876ff323a76d81bb1d7b86cdc57b005d00bb460081584b1e1b92bba86`: file identity is verified, but capture base/timing is not proved by the existing loader evidence. The address in its name is not accepted as capture metadata.
- `.../ctre/Firmware-Analysis/ram_before_main.bin`, SHA-256 `593b2df87e1b8e12bbcd9cfca8af94687f6e007d2df87187f6e2159d5be8b969`: `decodeSramInitData.py` explicitly generates it from reset initialization data; it is not a storage-read capture.
- Stock application BIN copies, SHA-256 `b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da`: `Cold.__init__` assigns CPU application base `$08010000`. Official SysEx is encoded update transport, not a flat NOR image. The published B1.3 COPY/ADD image has the same application role, not an independently captured identity sector.
- Prior installation evidence `builds/phase33-preservation-powercycle/installation.json` and `address-and-reachability.json`: source paths/hashes and explicit modeled NOR spans are recorded in `modeled_installation_sources`. Selected writes cover staging `$0,$6BD00)` and updater metadata `[$80000,$80017)`, not original identity bytes at `$81000`. Preserved/unwritten modeled space is not an authenticated acquired value.

The abbreviated `...` above is the reference project root; the companion candidate table gives **full absolute paths** for every file. `ctre` resolves to `ext/circuittracksreverseengineering`; alias paths and matching-byte copies are not independent authenticated captures. No pair of independently authenticated, physically mapped original `$81000` copies is established.

**UNKNOWN — exact missing evidence:** original file/capture offset N→physical external NOR `$81000`, with23 consecutive original bytes through `$81016`, including byte14, and a documented acquisition/mapping lineage. A post-normalization cache, numerical file offset, plausible serial string, updater metadata from a different sector, default zero/FF fill or duplicate hash cannot supply this evidence.

## Extraction and completion admission

**UNKNOWN:** [payload-admission.json (local-only reference: `builds/phase38-nor81000/payload-admission.json`; not distributed) records source file=null, file offset=null, accepted slice hex=null and slice SHA-256=null. No NOR slice file is created. No source is promoted on STRONG INFERENCE. The premise for native payload replay has not passed.

**PROVEN static expected completion path:** 080076cc.asm (local-only reference: `builds/phase38-nor81000/080076cc.asm`; not distributed) configures the DMA destination via `$0800653A`, issues the controller command, then calls `$08007832`, which waits on controller-state bit0. QSPI exception108 vector is `$080090B5`; 080090b4.asm (local-only reference: `builds/phase38-nor81000/080090b4.asm`; not distributed) calls `$080051C6`, which tests SR.TCF, acknowledges it and sets that native controller-state bit. Its notification path goes through `$080091EA`. DMA exception86 vector is `$080090CB`; that stub acknowledges DMA status and reaches `$08005228` (a return stub). A DMA flag alone is not substituted for QSPI completion.

**PROVEN static ownership unwind:** after a successful real read returns, backend `$08005374 → $08006350` releases the semaphore, Storage `$08005814` stores the request status, optional request callbacks are tested at `$08005820` (both null here), and `$0800582E–$08005846` clear wrapper sync bit0 after draining work. Main's `$08005726` wait may then return to `$080058B0`, unwind its local request, and reach the identity consumer `$08005DAE`. These are expected instruction paths, not executed completion claims.

**UNKNOWN:** IRQ/DMA service for this payload, actual request-complete transition, semaphore release, Main resumption and a stable post-consumption checkpoint. The prior native mode-command IRQ/prefix models do not qualify this DMA array-data transfer. No IRQ status, notification, callback, sync word or destination bytes are fabricated to bypass the missing provenance gate.

## Controls and final boundary

**PROVEN:** both observed controls exactly match their corresponding phase37 full SRAM/code endpoint and stop at `$080051C2`, opcode `$EC`, AR `$81000`, DLR22. Request structs, queue/ownership state and DMA registers agree between stock and diagnostic. The added observer does not change execution. These are **prefix controls**, not successful completed-read controls.

**PROVEN observed-prefix target `$82000–$821FF` counts:** reads0, writes0, erase overlaps0. There is no new post-read prefix to count. **UNKNOWN:** post-completion/full-boot target counts, H1/H2/P2/P3. P1 remains PROVEN within prior diagnostic scope; P4 remains PROVEN for unchanged bootloader code. Host containment remains PASS; H4 remains FAIL for same-session recovery. Application startup/SDMMC and target `$82000` data are not investigated.

**UNKNOWN — minimum prerequisite:** locate existing acquisition/mapping evidence and original23 bytes for precisely `$81000–$81016`, including the byte destroyed in the RAM cache. Only after that gate passes can the native DMA/QSPI completion and caller-consumption experiment be admitted. No new hardware operation or inferred payload is proposed.

NOR81000 STORAGE READ = UNQUALIFIED
