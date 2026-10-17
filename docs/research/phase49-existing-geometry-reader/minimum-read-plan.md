> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase49 — minimum evidence plan, no acquisition command

**UNKNOWN:** a supported existing CURRENT B1.3 interface able to export these fields. There is no executable read plan for the installed firmware qualified by this phase. Stop here; no live tool, port enumeration, packet transmitter or new diagnostic is created.

**PROVEN metadata definition:** `20000A98`8 bytes, `20000AB0`14 bytes, `20000AD0`24 bytes, concatenated in that order into46 raw little-endian bytes. [live-geometry-structure.md](<live-geometry-structure.md>). One contiguous enclosing read would be80 bytes at20000A98, not46; it exceeds historical rdiag's64-byte cap. Three reads minimize disclosed bytes; two reads could cover it with extra bytes. No reason to broaden to a RAM dump.

For comparison only, **PROVEN ABI in SC35D8**, not B1.3: cmd2, request address encoded as8 high-to-low nibbles plus one length byte, padded request232 bytes; response `F0 7D 43 54 42 seq`, status8 nibbles followed by2 nibbles per byte, terminalF7. Require correct signature/command/sequence, zero status, expected decoded length, valid nibbles, coherent mount interval and unit/firmware provenance. No request bytes or acquisition script are emitted. Router08020C90; SC35D8 manifest labels c_rdin0806B9F4 / c_rdcmd0806BA9C; these are not B1.3 handler addresses. rdiag.py (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/rdiag.py`; not distributed); ctremote.py (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/ctremote.py`; not distributed); manifest.json (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/firmware/sc35d8/manifest.json`; not distributed).

**PROVEN offline parser:** [geometry_parser.py](<../../../builds/phase49-existing-geometry-reader/geometry_parser.py>) accepts an already captured compact record, not a MIDI response and not an arbitrary RAM image. Invocation: Python with `-B`, parser path, and the local46-byte record path. It prints JSON; it does not modify the input or create a binary. Authentication/acquisition provenance must accompany the record externally; a valid tuple cannot establish its own source. No current-unit file exists to parse.

Validation checks exact46-byte length, mounted FATclass, internal drive0, baseD4000, stride/sector4096, power-of-two csize1..128, FATcount1/2, clean cache/FSInfo flags, nonzero mountID policy, sufficient FAT capacity, correct FAT/root/data equations and bounded32MiB physical end with wide host arithmetic. Zero mountID is conservatively rejected as ambiguous, not proof of invalid stock state (16-bit ID can wrap). Dirty snapshots and alternate partitions are rejected under this narrow evidence contract, not declared globally invalid. Firstcluster2/last=n_fatent-1; reserved=fat-vol. Exact total is printed only when derivable; otherwise null plus possible range. A BPB total from an already available VBR/status export is required to remove that ambiguity, not to bound the normal write domains.

**PROVEN tests:** parser-tests.json (local-only reference: `builds/phase49-existing-geometry-reader/parser-tests.json`; not distributed) accepts public reference RAM plus all4 prior normal bounded mount tuples and rejects24 malformed/inconsistent/unsupported records. The reference yields both target ranges outside normal FAT/root/data write domains. These are offline tests, not current-unit closure or a boot-state proof.

Next options, least invasive first:

1. **UNKNOWN:** an already available public/status report from this unit that includes these scalar fields. None found in Phase48 or documented as B1.3-supported here.

2. **UNKNOWN:** host-side read-only inspection of an already acquired authentic internal-volume VBR/image plus backing/mount provenance. SD files, Components file exports and fixed MSC capacity alone do not supply this.

3. **PROVEN historical capability, UNKNOWN current availability:** the existing hardware-tested CIRCUITS-HACKS rdiag mem command could expose the record on a diagnostic image that already includes it. Current B1.3 does not. This is not a recommendation or authorization to install SC35D8.

4. **UNKNOWN / separate future decision:** only if existing evidence/readers cannot suffice, a separately reviewed temporary diagnostic would be a firmware change. None is designed, generated, selected or scheduled here.
