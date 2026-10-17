> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 16 — strict read-only, nonhalting observation assessment

## Phase 17 — documented OnCE fails the observation gate

**SOURCE-DERIVED:** candidate DSP56724/25 uses DSP56300 OnCE, not SC140 EOnCE.
AN2073 section5 explicitly requires Debug mode, stopping normal execution.
Documented memory inspection injects instructions; flow history contains
program addresses, not effective X/Y write data. No qualifying nonhalting
state-preserving read or sufficient write-trace facility was established.

**STRONG HYPOTHESIS:** DSPB56724AG, supported by first-party board research
and external-memory evidence. A conflicting56725AG public report and exact
unit/package remain **UNRESOLVED**. Public STM32 header references do not
establish DSP JTAG pads. Board access to a qualifying facility is unresolved.

Offline emulation is plausible for conditional targeted traces, but full initial
state, peripheral/event fidelity and every effective-write hook need validation.
No emulator build/run or firmware instrumentation occurred. PassiveSPI alone
cannot close internal-write exclusions. Keephardware disconnected and5E rejected.
X35F invariant/normalhigh-X availability stay **NOT-YET-DETERMINED**; service
robustness stays **NO**. No allocation or Plaits work.

See [dsp-debug-observation.md](<dsp-debug-observation.md>),
[board-debug-access.md](<board-debug-access.md>) and `builds/phase17/final/` for
citations/matrices/source witnesses. **Next:** static emulator coverage/readiness
specification for minimal1F97/203A replay; no broad alias census or live debug.
This supersedes historical next-step suggestions below without changing their
verified firmware findings.

2026-10-06. STILL STATIC ONLY. No Circuit Tracks access, port enumeration,
MIDI/SysEx transmission, service5E execution, firmware/DSP-memory writes,
binary patches, original changes, installation or Plaits implementation.
Existing Capstone collected targeted ARM windows; the DSP listing and previous
results were reused. Primary manuals were consulted as documents only.

**Result: request5E READ is not a strictly read-only observer.** Even a valid
single-word read updates DSP private X protocol state and Y interrupt-save RAM.
The values are not all restored on return. No hardware observation through
this service is justified under the current requirements. No compliant
alternative has been established. OnCE's general nonintrusive wording is not
proof that memory inspection is nonhalting or state-free.

Evidence: `builds/phase16/final/`; reusable OFFLINE audit:
`tools/ct_readonly_observation_audit.py`. No `ct_read_dsp.py` or other hardware
reader was created. A schema and conditional tool specification are exported;
they contain no executable device access or service packet construction.

## A–B. Exact recovered READ framing and packing

**VERIFIED logical service envelope**, excluding unresolved physical USB/DIN
assignment:

```text
F0 00 20 29 01 63 70 5E | packed body | F7
```

2484C checks prefixF0 00 20 29 01, byte5=63, byte6=70 and length>=9.
1F284 checks byte7=5E and calls269E4 via1F30A. The handler treats the last
byte as framing by subtracting9; it does not itself validate the finalF7 or
require enough decoded fields. A well-formed small READ has a12-byte decoded
header, padded to14 for two complete seven-byte groups, giving16 packed bytes
and25 logical frame bytes. This is a description, not a generated request.

| Decoded request offset | Width | Meaning |
|---|---:|---|
|+0|1|**operation1 READ**;0 WRITE; other values yield status4|
|+1|1|address/port selector, **not READ/WRITE or Selection0/1**|
|+2|4|opaque echoed cookie, little-endian|
|+6|4|DSP word starting address, little-endian|
|+A|2|unsigned word count, little-endian|
|+C onward|none for READ|WRITE-only input slots are not needed for READ|

Selectors0/1 mean port0 X/Y;2/3 mean port1 X/Y. Other byte values fall back
to port0 X; they are not rejected by firmware. A future specification should
reject them and support only independently verified ports. Private starts must
be<8000; Y sets the encoded8000 flag. Shared starts[30000,38000) choose295BA
extended reads regardless of the private space flag. Actual port/core/physical
map and safe reserved/peripheral access are not inferred from this envelope.

**READ branch:**26A58 selects1→26AA4. Private loop26ACE..ADE calls29344 for
each encoded16-bit address. Shared loop26AB0..AC0 calls295BA. WRITE branches
26A5E..AA2 are distinct and not called by a correctly decoded operation1.
READ count0 causes no DSP transfer and returns accepted status2, but observes
no word. The useful-observation assessment below concerns positive counts.

**Codec391C6/3924E:** eight seven-bit bytes encode seven full bytes as a
contiguous MSB-first bit stream, rather than a separate MSB-prefix byte. For
one group, `d[i]=((e[i]<<(i+1))+(e[i+1]>>(6-i)))&255`, i0..6.
Conversely e0=d0>>1, e7=d6&7F, with intervening bit slices. Field endianness
remains little-endian after unpacking. SPI words are sent MSB-first;29344's
return is left-aligned, so each response slot isLE32 `(DSP24<<8)`. Parse with
`slot>>8`, retaining the unsigned24-bit word; no sign extension is implied.

**VERIFIED response:**37B0C copies six bytes fromP37B70 containing
F0 00 20 29 01 64, then **overwrites byte5 with63**, byte6 with70 and byte7
with5E. It appends packed data andF7. Thus the final response envelope is the
same as the request, with these decoded fields:

| Response offset | Width | Meaning |
|---|---:|---|
|+0|1|status2 accepted;3 invalid starting address;4 unsupported operation|
|+1|1|echoed selector|
|+2|4|echoed cookie,LE|
|+6|4|echoed requested start,LE|
|+A|2|echoed requested count,LE|
|+C+4*i|4|READ return slot,LE32 DSP24<<8|

Success does not certify timing, safety or count capacity. For N words, nominal
response body length is12+4N. In the small valid range it packs to
`8*ceil((12+4N)/7)` bytes. **The encoder reads complete groups without zeroing
tail padding.** Count1 has16 meaningful bytes,21 source bytes rounded for
encoding,24 packed bytes and33 total frame bytes: five raw tail bytes are
unspecified ARM scratch contents. Trim to the declared meaningful length;
error paths do not fill read slots, so discard their data. No5E checksum field
was recovered. Transport integrity is separate.

## C. READ side effects — the decisive failure

For a valid private read in the assumed24-bit SHI mode,29344 issues an
address-read followed by read-next. The DSP44→156 ISR executes twice:

| State | Evidence | Classification |
|---|---|---|
|X10: saved SHI pointer|190/1AC|**PERSISTENT SIDE EFFECT**; leftadvanced, not restored|
|X11: address/space flags|189|**PERSISTENT SIDE EFFECT**; read command/flags retained|
|Y2000..2002|156/158/15A|**PERSISTENT SIDE EFFECT** to private save RAM, even though CPU registers are restored|
|Y2003..2005|168/16A/16C|**PERSISTENT SIDE EFFECT** to A-save RAM on address commands|
|R0/M0/X0/A and interrupt context|191..1B3|**TRANSIENT INTERNAL STATE ONLY** under reviewed save/restore;M0 temporarilyFFFF|
|SHI FIFO/status/HTX|15E,18C/18F,1A5/1AA|**TRANSIENT INTERNAL STATE ONLY**, with real ISR/preemption and prefetched-data effects|
|requested data words|18C/18F,1A4/1A9|**VERIFIED NO SIDE EFFECT** as direct stores to those targets on this well-formed local path|
|scheduler, voice, effect, mailbox and DSP DMA fields|local READ branch|no direct setters recovered; **UNRESOLVED** global noninterference through dispatcher/context/cache effects|
|Selection0/1|269E4/29344|**VERIFIED NO SIDE EFFECT locally**; noSelection1 prerequisite or utility mode switch|
|audio continuity/end-to-end latency|polls/SHI ISR|**UNRESOLVED**, no glitch-free claim|
|explicit software interrupt masking/debug halt|reviewed handlers/helpers|noCPSID/PRIMASK/STOP/WAIT/debug-halt instruction on the valid local path; full transitive behavior **UNRESOLVED**|
|ARM reply/scratch/queues/GPIO/SPI state|269E4,37B0C,20C90,291xx,37960|state is modified; reply buffer20006180 survives the call; complete downstream queue side effects remain **UNRESOLVED**|

Persistent here means surviving handler return until overwritten later, **not
nonvolatile storage**. These RAM writes suffice to answer the strict question
negatively without pretending all transitive effects have been enumerated.
The dispatcher can also fan out through1F30E and24884 after the utility;
their global noninterference is not silently assumed.

**Single word at addressa:** requested read returnsa, read-next additionally
fetchesa+1, andX10 is lefta+2. X11 retains the address-read command flags.
For bounded contiguousN, desired[A,A+N), actual read union[A,A+N+1), saved
cursorA+N+1. There are2N target-memory reads,2N SHI IRQs,9N Y-save-word writes
and3N X-protocol-state writes. CPU-register restoration does not restore the
previous contents of the scratch/private protocol words.

**UNRESOLVED cache-coherence hazard, with a verified conditional model:**
292F8 compares requested destination to the cached halfword20003D00 and skips
292DC address setup when equal;29340 updates cache to requested+1. Scalar
29344/29504..26 has no explicit cache invalidation. Bulk29528, by contrast,
explicitly storesFFFF at295A4. If cacheC is still the next normal-write address,
a service read of highX5F00 leaves DSPX10=5F02; a subsequent cache-hit write
to logicalC could then use5F02 without new address setup. Actual normal
interleaving, hidden aliases and post-dispatch invalidation are unproved;
this is not an observed stock bug. It makes active sampling a possible
confounder of high-X ownership, even if the client never emits WRITE operation0.

## D–E. Transport and scheduling

**VERIFIED:** this is a framed MIDI SysEx/service path, installed at boot.
1EC92..96 registers1EB31 via251E8 into200008F0.1EB30 accepts ingress IDs0/1
and forwards to2484C.51968/51974 provides a static callback bridge into that
same collection. Responses pass37B0C→20C90, which validatesF0/F7 and seven-bit
interior bytes and routes through a mask to MIDI sender objects.

**UNRESOLVED:** complete mapping from those logical IDs/objects to USB MIDI,
DIN MIDI or a particular endpoint/driver in the stock unit. No proprietary
USB endpoint was proved for5E. **HYPOTHESIS:** a vendor service application
such as Components may use it; the frame itself does not identify the client.
No port enumeration, traffic capture or active identity probe was performed.

The utility is callable with Selection0 active: it runs before the late
enable-bit guard and does not require a diagnostic firmware selection.
That does not prove safe real-time operation or physical transport reachability.

**VERIFIED blocking behavior:**26ACE loops synchronously;37960 polls SPI
TX/RX conditions until three bytes complete;3B9D8→23414 waits for a completion
flag without a local timeout/yield. This blocks the calling ARM execution
context. It is not proved that context is the entire ARM scheduler. DSP SHI
interrupts suspend foreground work while servicing commands andRTI resumes it;
there is no explicit DSP debug halt in the reviewed read path. Scheduling
headroom, priorities, contention, response freshness and uninterrupted audio
are **UNRESOLVED**. No wall-clock safe rate is inferred from six SPI bytes.

The READ handler does **not** establish24-bit SHI width before using29344.
Width preservation and possible interleaving with16-bit jobs need proof.
STM32 transfer completion is not evidence the DSP HTX contains a fresh word
from the intended sample epoch. Large malformed counts can also corrupt ARM
scratch, so conclusions about valid small reads must not cover those requests.

## F. Granularity and prefetch boundaries

**No positive count is certified safe under the strict requirements.**
The smallest structural request is one word; it still has the above effects.
The count field accepts0..65535 with no local cap or final-address check.
Only32 words fit the reviewed128-byte read scratch SP[10,90) and160-byte
encoder output SP[90,130). N32 gives140 raw response bytes→160 packed→169
frame bytes without padding. This is conditional local capacity, **not an
enforced or global safe maximum**. N33 already overlaps scratch/encoding
areas.37B40 also truncates packed_length+9 to8 bits for response framing.

**VERIFIED extra-access concern:** reading X5FFF fetches X6000 as well.
6000 lies outside the conditional DSP56724/core0 private-X RAM boundary.
Its behavior is **UNRESOLVED**; therefore a full256-word high-X scan via these
helpers cannot be certified by merely splitting into small chunks. Reading
X5FFE instead fetches5FFF without a6000 read. Reading35F fetches360; cursor
table reads similarly fetch the following scalar/state word. A future
specification must validate the extra access, not only requested endpoints.

## G–J. Future observation design — blocked, not executed

These are logical targets/scenarios for a future compliant observer. They
are **not a recommendation to issue5E** under this failed gate.

| Priority | Targets | Expected/concern |
|---|---|---|
|1|X35F, one word|expected0; any nonzero is a stop-and-log concern|
|2|Y1820..182F;Y1A10..1A1F|alternating2CCC/2CEC and2C02/2C24|
|3|X5F00,5F40,5F80,5FC0,5FFE|boot-derived zeros; nonzero/change merits investigation|

Minimal future matrix: idle; Synth1 notes; Synth2 notes; both active;
polyphony; patch/preset; Macro; filter/resonance; envelope; effects; transport
start/stop; scene/session/project. MIDI input is included only if separately
authorized in that future scope. None executed. A truly passive facility might
observe existing stock activity without generating any test traffic.

For35F, log raw result, echoed cookie/address/space/count, status, host monotonic
request/reply times and surrounding user action. On nonzero, stop sampling
and allocation work; preserve evidence, do not clear/reset/write or automatically
retry.5E samples occur in the SHI ISR, **not at203A**. Nonzero after an active
service may reflect observer effects or stale/incorrect replies; do not promote
it to a proved normal203A violation without independent attribution.
All-zero finite samples cannot establish every203A entry.

For highX, no sentinels: zeros staying zero are empirical observations only.
Changes/nonzero words can reveal activity under observed conditions; unchanged
values miss writes of0/the same value, short transients and unsampled words.
Sparse reads do not establish the whole256-word range is free, and chunks are
not an atomic snapshot. An active service's protocol/cache effects would
confound a claim about unobserved pure normal operation.

| Option | Work/coverage | Decision |
|---|---|---|
|A: one256-word read occasionally|exceeds local32-word capacity; includes6000 prefetch|reject for this mechanism|
|B: five sparse single words|30 SPI bytes,10 SHI IRQs,290 logical MIDI request+reply bytes; misses unsampled activity|preferred **conditional design** for lowest load, but blocked now|
|C: chunks over time|16x16 implies1536 SPI bytes,512 IRQs,1952 logical frame bytes; wider non-atomic coverage; final6000 prefetch remains|defer until mechanism/boundaries qualified|

No validated polling rate exists. Future design would start manually with
one word and one outstanding operation. A hypothetical total ceiling of one
request per two seconds is only a conservative **estimate**, not evidence
of safety; no automatic polling or rate was enabled. Reading all256 continuously
is neither necessary for initial evidence nor justified.

## K. Tool architecture, not an implementation

The service failed the precondition for a live read utility, so no
`tools/ct_read_dsp.py` was created. Exported `tool-spec-only.json` describes:

- immutable READ operation1, no WRITE constructor/API/raw-command escape;
- explicit X/Y and validated port, address and count; reject unknown selectors,
  shared/peripheral/reserved ranges and any unsafe prefetched address;
- initial allowlist/count1, upper limit32 only after separate capacity proof;
- independently confirmed unit/firmware/version binding; name/prefix alone
  is insufficient; no active identity probe added;
- default offline dry-run summaries, timestamps, unique cookie, one outstanding
  request, strict reply validation and trimming, no fast polling/retries;
- no update, bootloader, firmware instrumentation or client write functionality.

Even such a tool cannot make the stock READ handler private-RAM-write-free,
remove ISR timing, restore undocumented state safely or establish freshness
by construction. Omitting service WRITE is not the same as preventing DSP
internal writes or subsequent normal-write redirection.

## L–N. Safety gate and alternative-path limit

| Gate | Answer | Scope |
|---|---|---|
|A: READ distinct from WRITE?|**YES**|correctly decodedoperation1 versus0|
|B: useful read without modifying DSP private RAM?|**NO**|X10/X11 andY save RAM are written|
|C: persistent effects excluded?|**NO**|private protocol/save values survive return; other effects open|
|D: Selection0 allowed?|**YES**|noSelection1 prerequisite on recovered branch|
|E: external stock transport established?|**NOT-YET-DETERMINED**|logical installed SysEx path proved, physical driver/port chain incomplete|
|F: tool can make service WRITE impossible?|**YES**|client can omitop0; does not prevent internal DSP RAM writes|
|G: passive observation via5E justified?|**NO**|active state-changing service failsB/C|

**M. No hardware observation is justified through this mechanism under the
stated requirements.** No allocation/invariant upgrade follows.

NXP's DSP56724RM section4.3.5 describes an OnCE/JTAG interface, but its
general nonintrusive wording does not resolve the strict gate.
[DSP56724RM](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf).
The documented DSP56300 memory-inspection path forces an instruction to place
data inOGDBR, and the serial debug procedure waits for Debug-mode acknowledgement.
Its trace buffer stores program-flow addresses, not the required private-RAM
data events; reading it advances its internal pointer. These documented
operations are **not a proved nonhalting, state-free alternative**.
[DSP56300FM, sections7.2.4–7.2.6](https://www.nxp.com/docs/en/reference-manual/DSP56300FM.pdf).
Actual chip/core/board-access details and any other facility remain UNRESOLVED.
No JTAG activity, breakpoint, instruction injection or debug configuration.

**N. Single best next step:** establish the exact chip/board debug topology
from documentation and determine whether an alternative genuinely passive
data-observation facility exists. Keep5E rejected, invariant/allocation
UNRESOLVED and hardware untouched; do not substitute OnCE peek/poke or relax
the user's safety rules implicitly.

## Reproduction

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_readonly_observation_audit.py --output-dir builds/phase16/final
```

Fresh paths required. The tool exports schemas, state effects, prefetch/capacity
arithmetic, blocked plans and byte-checked ARM/DSP witnesses. It does not
construct/transmit a service packet or access a device. Both baseline hashes,
all five extraction pairs, decoded-BIN equality and codec roundtrip are checked.

**VERIFIED final checks:** `builds/phase16/final/` and independent `repeat/`
contain14 byte-identical reports; hashes are recorded in
`builds/phase16/reproducibility.json`. Baseline SHA256 values remain exactly
the supplied SYX/BIN values, all five extraction pairs retain their hashes,
decoded BIN equality and exact SYX roundtrip pass, and256 codec-group fixtures
pass. Reusing an existing output directory was rejected without overwriting
its files. No hardware utility was created or executed.
