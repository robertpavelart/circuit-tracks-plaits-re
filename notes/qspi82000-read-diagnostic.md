> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# QSPI $82000 fixed-range read diagnostic — offline design

**UNKNOWN — hardware admission remains unqualified.** The fixed-range ARM prototype and host receiver pass **197 offline checks**, including instruction execution of the original backend read, DMA setup and QSPI command construction. The selected QSPI transaction emits only read commands. Real DMA/interrupt delivery, scheduler/task headroom, complete output-device behavior and preservation of the original target bytes across a later firmware installation remain **UNKNOWN**. No hardware was accessed. No application image or firmware-update SYX was generated.

All working files are under phase27-qspi-read (local-only reference: `builds/phase27-qspi-read`; not distributed). [ARTIFACTS.md](<../docs/research/phase27-qspi-read/ARTIFACTS.md>) marks the fragment and synthetic transport evidence **NOT YET HARDWARE-APPROVED**. The synthetic test dump is not stock QSPI evidence and must not be used to advance phase26 or the P-memory qualification.

## Exact stock API and selected context

**PROVEN:** the initializer's original chain remains `$08035E28 → $08047C6C → $08024130 → $08023F68`, synchronous wrapper wait `$08023FD6`, worker `$08024014`, read branch `$0802408A–$08024096`, backend **`$08022F94`**, low read **`$08037430`**. The asynchronous wrapper queues operation1; the caller synchronously waits for the worker's status. This is the path established in [p0282-0386-reclaim-qualification.md](<p0282-0386-reclaim-qualification.md>), phase25.

**PROVEN:** the prototype reuses **the exact backend read method `$08022F94`** called by that worker. It does not call/drain the generic worker queue, because that queue also services unrelated writes. AAPCS arguments are:

| Register | Diagnostic value / meaning |
|---|---|
| R0 | Backend object = `[[ $20006968 ] +4]`; captured value `$20000378`, vtable `$0805B1AC` |
| R1 | Hardcoded absolute external-QSPI byte address `$00082000` |
| R2 | Dedicated 512-byte buffer in the diagnostic's own live stack frame |
| R3 | Hardcoded `$200` bytes |
| R0 on return | 0 successful driver return, 1 offset rejected, 2 backend busy |

**PROVEN:** backend+4 is the initialized controller context, captured at `$20000000`; controller/device pointers lead to QSPI register base `$A0001000`. Backend+`$C` holds capacity `$02000000`. `$08022F94` takes the byte semaphore at backend+8, calls `$08037430`, then releases it through `$0801BA12`. Busy returns without queueing or entering the read. The method tests start offset, not the complete end range; the diagnostic therefore does not expose caller-supplied address/size and fixes its end to `$821FF`.

**PROVEN:** `$08037430` configures receive DMA through `$0801C4D4/$0801C072`, builds the original read template from `$080376F4`, and calls `$0803769C → $08022746`. It writes 511 to QSPI DLR and `$82000` to AR. Its completion path `$08037596` obtains the current thread via `$0801CDB8/$0801CD82`, invokes the context's callback list through `$0801C894`, then checks the controller completion flag. The captured single callback is **`$08057650`**, stored as Thumb `$08057651`; it passes the current thread to **`$0801BE1A`** with flag mask `$100`. This is a synchronous driver wait requiring initialized controller/DMA/interrupt/RTOS state and a schedulable thread context, not an interrupt-safe raw-memory load.

**PROVEN:** the prototype checks IPSR=0, the backend vtable, callback count=1 and callback entry=`$08057651` before calling the backend. Null object/backend, changed type/callback, interrupt context and malformed commands are rejected without a read. The 512-byte stack buffer remains live until all replies return. It does not borrow the initializer's global `$20005148`, request-buffer slack, DSP state, mixer buffers or SD storage. It never initiates a DSP upload.

**UNKNOWN:** available headroom and DMA/cache suitability of the actual SysEx task's stack. The fixture deliberately uses its existing artificial stack at `$2006F000` and message scratch at `$20060000/$20060100`; these are emulator allocations, not proposed physical RAM ownership. Own maximum nested stack use is 616 bytes; the executed stock path reaches **724 bytes** with modeled OS-wait and output endpoints. That is not an upper bound on the real task's total stack or interrupt usage. No hardware allocation is claimed from it.

Exact authenticated instruction spans, hashes and calls are preserved in stock-audit.json (local-only reference: `builds/phase27-qspi-read/stock-audit.json`; not distributed) and stock-read-and-router.asm (local-only reference: `builds/phase27-qspi-read/stock-read-and-router.asm`; not distributed). The examined spans are byte-identical in official4486 and pinned B1.3.

## Read-only proof and its boundary

**PROVEN, selected transaction:** **QSPI READ PATH = READ ONLY** for the admitted fixed request and initialized stock controller. The original read template's command bytes are `$EB/$EC`; the adapter only changes address/lane flags. The executed CCR is `$07183FEC` in the captured mode: FMODE=1 (indirect read), opcode `$EC`, AR=`$82000`, DLR=511. All four tested lane/address-mode combinations preserve read direction and exact host output. There is no write-enable, program, erase, SD-content or internal-flash operation in the selected transaction.

| Routine(s) | QSPI read | QSPI program / erase | SD write / internal-flash write |
|---|---|---|---|
| New `entry/command/p32/pbytes/crc` | Calls only fixed backend read | **PROVEN:** no write/erase command, selector or argument | **PROVEN:** no such API call; stores target live frame/request buffer only |
| `$08022F94` | **PROVEN:** calls `$08037430` | **PROVEN:** no branch/fallthrough to adjacent writer `$08022FDC`; every exit returns | **PROVEN:** no such selected operation |
| `$08037430` | **PROVEN:** immutable read template | **PROVEN:** returns at `$08037490`; no fallthrough into erase `$08037494` or program `$080374D4` | **PROVEN:** no selected content/flash writer |
| `$0803769C/$08022746` | **PROVEN:** emit supplied read template | **PROVEN:** generic routines can emit other commands for other callers; they are not globally read-only. Here arguments come only from the stock read template. | **PROVEN:** selected stores configure QSPI registers, not SD/flash programming |
| `$0801C4D4/$0801C072` | **PROVEN:** stock receive-DMA setup executes | **PROVEN:** controller/register writes are not NOR program/erase operations | **PROVEN:** no SD/flash programmer call in these instruction spans |
| `$0801BA12`, thread queries, callback `$08057650` | **PROVEN:** semaphore/current-thread/flag-wait support | **PROVEN:** no selected NOR command | **UNKNOWN:** complete scheduler/preemption behavior outside the modeled endpoint |
| `$0801C894` | **PROVEN:** admitted callback is checked | **UNKNOWN** for arbitrary additional callbacks; prototype refuses them | **UNKNOWN** for arbitrary callbacks; not accepted by this design |
| `$08020C90` output router | **PROVEN:** validates SysEx and copies caller packet to its buffer via `$0801AA14` | **PROVEN:** selected purpose is MIDI output | **UNKNOWN:** full closure of port-vtable implementations and scheduler/device callbacks has not been qualified |

**PROVEN:** storage-mutating entry points `$08022FDC/$08037494/$080374D4` are not targets of the matched diagnostic command. All other 127 command numbers in its private namespace are refused. Arbitrary address/length inputs cannot be decoded into storage arguments because the handler compares every fixed request field against constants. The original prologue/continuation is retained for foreign SysEx; unrelated stock commands retain their original behavior. This is not a claim that all B1.3 firmware, normal UI tasks or foreign update commands are globally read-only.

**UNKNOWN:** the requested *whole runtime* reachability/side-effect proof through the real scheduler, DMA IRQ path and MIDI port-vtable implementations. These boundaries are explicitly modeled in the offline test. Consequently the selected NOR command sequence is read-only, but this report does **not** admit the design for hardware on that fact alone. The end-to-end read-only/hardware gate remains unqualified.

## ARM changes and packaging

**PROVEN:** [build_patch.py](<../builds/phase27-qspi-read/build_patch.py>) builds only an ARM fragment and patch-plan.json (local-only reference: `builds/phase27-qspi-read/patch-plan.json`; not distributed). It does not export a modified application or call an updater. It authenticates published B1.3 COPY/ADD spans in memory against manifest SHA-256 `2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41`, original length435,220. Proposed changes are:

| ARM range | Exact change |
|---|---|
| `$0801EB30–$0801EB33` | Original `2D E9 F0 41` → `5B F0 70 BC`, `b.w $0807A414` |
| `$080101E8–$080101EB` | Future installation marker `42 31 2E 33` (`B1.3`) → `51 32 37 52` (`Q27R`); plan only |
| `$0807A414–$0807A735` | **802-byte** appended diagnostic ARM fragment |
| `$0807A736–$0807A737` | Two `$FF` alignment bytes needed if later packaging an application; not part of executable fragment |

**PROVEN:** encoded code/hook/marker changes total **810 bytes**, plus two packaging-alignment bytes. The future aligned application would occupy436,024 bytes, end-exclusive `$0807A738`, below physical `$08080000`. DSP modifications=0; bootloader modifications=0. The normal audio/synth code is not replaced. This is the bounded prototype's size, not a proof that no smaller encoding exists.

**PROVEN:** fragment SHA-256 **`7cc4fe6ac3a031da839df2f45ae9cf69453ff12a4de32678527e752da28c5696`**. **UNKNOWN / not generated:** candidate application/SYX SHA-256. The `.syx` files in this evidence directory are explicitly marked **synthetic device-reply transport data**, not firmware or real coefficients.

**PROVEN:** the unchanged stock codec `ct_fw.py:crc32_mpeg2` reproduces both official4486 CRC `$4E74DA9E` and B1.3 `$247DE840`. Firmware packaging uses CRC-32/MPEG-2 over application bytes, variable-length header, 32-byte update blocks and `$FF` padding. No CRC algorithm or persistent format change is proposed. A future package would require a freshly computed CRC; none has been represented as an approved artifact here.

## Fixed-range SysEx transport

**PROVEN:** [protocol.py](<../builds/phase27-qspi-read/protocol.py>) and independent compiled ARM encoder agree exactly. Reuses reference `rdiag.py`'s `F0 7D 43 54` private prefix, nibble encoding, 232-byte request allocation and output router `$08020C90`; it does **not** install the general `rdiag` read/write handlers. It uses command `$0D`, response `$4D`. All interior bytes are MIDI-safe (<128).

| Packet | Bytes / fields |
|---|---|
| Host request, 232 bytes | raw instruction bytes omitted |
| Data response, 162 bytes each | Prefix +`4D token`, kind0, index0–7, packet address as8 nibbles, total512 as8 nibbles, raw payload length64, 64 bytes as128 nibbles, packet CRC32 as8 nibbles, `F7`. Address=`$82000+64*index`. |
| Completion response, 42 bytes | Same prefix/token, kind1, index8, address=`$82000`, total512, payload length4, whole512-byte CRC as8 nibbles, packet CRC as8 nibbles, `F7`. |

**PROVEN:** packet CRC is CRC-32/MPEG-2 over the transmitted bytes from command through the last payload nibble, excluding prefix, CRC suffix and F7. Completion carries CRC-32/MPEG-2 over the original512 raw bytes, encoded big-endian as four payload bytes. The host rejects token, address, size, nibble, ordering, duplication, missing-packet, packet-CRC and whole-data-CRC errors; it writes the final file only after exact completion. CRC establishes transport integrity, not source authenticity.

**PROVEN:** success sends eight chunks from **one** 512-byte stock read, not eight rereads or a synthesized response. On invalid input, busy/bounds/type/callback rejection, no data/completion success is sent; the host times out without saving. Missing driver completion may block the device task: there is no added firmware timeout or forced acknowledgement. No automatic host retry is used.

**STRONG INFERENCE:** consecutive replies can reuse the request buffer because `$08020D46–$08020D5A` copies it into router-owned storage, and prior-output handling appears at `$08020D0E–$08020D28`. Full hardware buffer ownership/port completion and latency remain **UNKNOWN**; the test captures the router boundary without transmitting. Runtime buffer slack is not borrowed for the512-byte raw read; it is used only for the shorter162-byte encoded reply, within the existing232-byte allocation.

## Host receiver and offline results

**PROVEN:** [receiver.py](<../builds/phase27-qspi-read/receiver.py>) offers local `request` and `receive` commands and an explicit future `live` command. Only `live` lazily imports the existing WinMM `ctremote.Link`, enumerates ports and opens a uniquely matching input/output. This phase never called it. No new USB driver/protocol is introduced. `WinMMTransport` handles fragmented/coalesced callback chunks; `protocol.acquire` sends exactly one fixed request and consumes nine frames.

**PROVEN:** a successful receiver writes `qspi_00082000_000821ff.bin`, its SHA-256/address/token/origin metadata, and the received SysEx transcript into the selected **host computer directory**. File overwrite is refused. Unknown or synthetic source provenance remains explicitly marked; successful reception alone does not authenticate which firmware/device was used.

**PROVEN, bounded:** offline-test-result.json (local-only reference: `builds/phase27-qspi-read/offline-test-result.json`; not distributed) records **197 checks**. Six successful ARM cases cover ports0/1 and all four stock lane/address-mode combinations. Tests execute the actual new handler and stock backend, DMA setup, command adapter, QSPI register writes, semaphore release, thread queries, callback dispatcher and selected callback. They verify independent Python/ARM CRC/frame equality, 512-byte reconstruction, packet sequencing, source/destination handling, caller callee-saved registers, request/raw-buffer canaries, backend semaphore preservation, all other command IDs, every address/size nibble, short/long/padded malformed packets, wrong callback/type, busy/bounds rejection, exception-context rejection and modeled missing completion without success. A fake WinMM queue tests fragmentation/coalescing without WinMM or devices.

**PROVEN:** the synthetic peripheral supplies only documented test bytes at the DMA completion boundary after observing the real AR/DLR/CCR writes. The test models the controller completion flag and OS wait `$0801BE1A`, and captures output at `$08020C90`. It does not fake the read-method return or preload DSP memory. **UNKNOWN:** actual DMA execution, cache coherency, interrupts, real OS-wait behavior and physical MIDI delivery. No original QSPI bytes were used or recovered.

## Recovery and deployment limits

**PROVEN:** bootloader-evidence.asm (local-only reference: `builds/phase27-qspi-read/bootloader-evidence.asm`; not distributed) is disassembled from the pinned full internal-flash dump, SHA-256 `f3d85d64c9ead9205e5336dff49bb51f21d270ffa29b47c6f6971125d6d848a8`; its untouched first64KiB hash is `09fcb71d6583a5714cb96d496ffb423c0d7049754a4cb4413f588d6f54148643`. Proposed patch addresses lie entirely in the application. Main `$08002FDE` performs its button poll `$08003B66` before optional apply/app launch `$08003B9A`; nonzero poll result bypasses that branch and enters the bootloader service loop. `$08003AB0` tests logical IDs `$12/$08/$09`. Version comparison `$08003BE4–$08003BF6` skips identical26-byte version blocks, explaining the separate `Q27R` marker change. CRC/product/size checks and normal application-sector update remain bootloader code, not modified routines.

**PROVEN as a local report:** reference `docs/NOTAS.md`, lines29–48, reports uploader hardware testing on2026-10-03, the button names **Scales + Preset + Note**, and describes normal update/restore behavior. `tools/ct_uploader.html` line36 and `rc_uploader.html` line45 document the same normal external bootloader entry. **STRONG INFERENCE:** a normal official4486 rollback path remains architecturally available if this bootloader, its button scan, storage and USB service initialize successfully. **UNKNOWN:** recovery of this particular unit after this diagnostic's specific failures or interrupted installation. The existing [firmware recovery gate](<firmware-recovery-gate.md>) is not closed by these observations.

**PROVEN:** diagnostic runtime has no persistent-format change. **UNKNOWN:** unchanged bytes at `$82000` across deployment. The normal firmware updater itself stages data in external storage and changes internal application flash. Boot code `$08003B36` reads staging metadata at `$80000`; that does not prove the updater's entire program/erase footprint excludes `$82000`. This experiment did not qualify that footprint or the original target's survival. Therefore a future installation cannot be represented as end-to-end “no QSPI writes,” and no newly installed capture can automatically be asserted to preserve pre-installation coefficient provenance. Under a strict no-QSPI-writes deployment constraint, no installation procedure for this new handler is qualified.

**UNKNOWN — remaining hardware risks:** real SysEx task stack and DMA/cache accessibility, schedulability and wait completion, ISR/output-router behavior under active audio, updater erase/staging footprint near the requested original data, and unit-specific rollback. No hardware experiment is authorized by this report. This phase does not claim a read-only runtime guarantee for every unrelated B1.3 task.

## Procedure that would be used later

**UNKNOWN / conditional:** there is no currently qualified installation step satisfying the strict no-QSPI-writes constraint. Before any separately authorized deployment, finish the offline task-stack/DMA/output closure and prove the normal updater's erase/program footprint preserves the target's original bytes; produce and review a concrete package with its own SHA/CRC. Nothing here directs an installation now.

If a separately approved handler were already resident and its installation/source provenance established, the acquisition procedure would be:

1. Use the normal USB-MIDI connection, a uniquely identified main input/output pair, and stop other host applications holding those ports. Leave storage-editing operations inactive. No stock DSP upload or other diagnostic command is needed.
2. Invoke the host receiver's **future live mode** once, using a fresh token and fresh host output directory. For example, with a uniquely matching port selector chosen from the actual port names:

   ```powershell
   & 'C:\Users\rober\AppData\Local\Python\pythoncore-3.14-64\python.exe' -B 'C:\Proj SSD\CODEX\CIRCUIT\builds\phase27-qspi-read\receiver.py' live --port '<unique main-port selector>' --token 37 --outdir 'C:\Proj SSD\CODEX\CIRCUIT\builds\phase27-qspi-read\future-capture'
   ```

3. Require eight ordered packets and the completion packet, both CRC checks, exactly512 bytes and a printed SHA-256. On timeout/error stop; the utility does not retry automatically or save a partial dump. Preserve the transcript, firmware hash/version, unit/port identification and installation history alongside the capture before calling its mapping PROVEN.
4. Any later rollback would use the preserved official4486 file and the ordinary documented USB/SysEx bootloader/update route, subject to the independent recovery gate. The local report of a bootloader button combination is not an unconditional recovery guarantee.

**PROVEN:** all work in this phase was source/design/offline validation. No firmware image, firmware-update SYX, bootloader change, option-byte change, device command or hardware access was performed. P:$0282–$0386 remains unqualified; no reclaimed words were added.

QSPI82000 READ DIAGNOSTIC = UNQUALIFIED
