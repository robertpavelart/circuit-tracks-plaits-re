> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: FAILED / SUPERSEDED / DO NOT FLASH.

# Phase61 candidate — offline qualification complete

**FINAL PRE-FLASH HARDWARE-TEST CANDIDATE — NOT YET HARDWARE-TESTED.**

|Artifact|Bytes|SHA-256|

|---|---:|---|

|circuittracks-final-geometry-gated-nor-test.syx| raw instruction bytes omitted |`fe36e18bc83448b0e25cc21b8323e0e64e153f6e04abc042546f4a20e83731d3`|

|circuittracks-final-geometry-gated-nor-test.bin| raw instruction bytes omitted |`af5b62e371c1f9e6972b573e766088e54da6fadfcba911e62f25bd0edb0c763f`|

CRC-32/MPEG-2: **6ECE2ED4**. Application `[08010000,08075100)`; exclusive end **08075100**; image headroom **44,800 bytes** to08080000. Protocol product64/version572; distinct compared-header marker **N61GEO**. InitialSP20050000/reset0805C00D are unchanged. No Plaits code is present.

Only this exact Phase61 pair is designated. All older diagnostic candidates/fragments are **SUPERSEDED — DO NOT FLASH**. This does not supersede official stock rollback firmware. Historical candidate files and reports remain unchanged as evidence.

Read [findings.md](<findings.md>) and [schema-and-protocol.md](<schema-and-protocol.md>). Detailed exact diffs and all three install/rollback summaries are local. SHA256SUMS.txt authenticates this package. The host.py module implements the geometry/authorization/one-shot receiver with injected transport; it opens no ports. Tests and sample outputs are synthetic. Old Phase43/44 host tools use incompatible0D start and must not be used with this candidate.

H4 remains FAIL for in-session recovery. After any failed or uncertain attempt: **CAPTURE FAILED — DO NOT RETRY — POWER-CYCLE DEVICE BEFORE ANOTHER ATTEMPT**. No forced storage cleanup or retry is permitted. A new Python Session object alone is not evidence of a physical power cycle.

No installation or capture command is run or authorized here. STOP and await explicit user decision. Physical installation, capture and rollback remain untested.
