> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: FAILED / SUPERSEDED / DO NOT FLASH.

# Reservation-negative test — reproduced failure and focused correction

**PROVEN:** exact original Phase61 SYX decodes to BIN SHA-256`af5b62e371c1f9e6972b573e766088e54da6fadfcba911e62f25bd0edb0c763f`. Its hook at0801AE06 enters snapshot0806D500, which checks control16 (MOUNTING) but not allocator ownership. At limit20044E58 (not reduced), cursor20044D68, and record`16000000A5A5A5A5A5A5A5A5`, valid synthetic mounted metadata causes:

| Store PC | Address | Value |

|---|---|---|

|0806D686|20044D74|34008001|

|0806D688|20044D78|018F9080|

|0806D690|20044D70|00000011 (VALID)|

Output record:`110000000180003480908F01`. It wrongly writes all12 bytes and publishes validity without a reservation. The wrong-limit and overlapping-cursor variants also reproduce the missing check. This is an adversarial native entry-state counterexample, **not** evidence that ordinary hardware boot has already encountered that state. Native initialization normally reserves earlier; that does not satisfy the specifically requested defensive negative gate.

**PROVEN correction:** at0806D510, branch to a36-byte leaf guard at0806D800. Before any record access, require `[20002B44]==20044D70` and `[20002B48]<=20044D70`. Failure takes the existing restore tail0806D698, preserving the caller and making zero record reads/stores in the guarded snapshot path. Success setsR4 to the record base and resumes0806D518. The existing PRIMASK-masked save/restore envelope surrounds the guard; it adds no stack frame. No schema, raw-read protocol, transport or allocation architecture changes.

The corrected full7-case matrix passes: absent zero, absent garbage, absent partial MOUNTING, absent reservation with cursor beyond the record, wrong limit, reserved limit with cursor overlap, and correctly reserved positive first mount. Every negative case has0 private-record write intents, byte-identical input/output, geometry_valid=false, allocator unchanged and neighbor guards preserved. The positive case writes geometry and VALID normally. All cases execute the installed0801AE06 hook and original0801AE14 mount return tail; the stock logging sink alone is modeled. ReturnSP is callerSP+16 after the original frame pop. This proves safe bounded continuation through that tail, **not a complete boot-to-USB replay**.

The corrected bytes also pass the existing28 native boundary regressions, emitted to this Phase62 directory. No old result file was overwritten. The new candidate changed42 bytes:4 differing marker bytes,4-byte guard branch and34 differing bytes in a36-byte formerlyFF gap. Serialization was independently decoded/CRC-checked and BIN equality verified. It has **not** passed full new-image startup/coupled/install/rollback qualification.

Fixture correction disclosed: an initial corrected-image run replaced code after the old fixture had executed it, leaving Unicorn translated code cached. That result is retained as `corrected-reservation-tests-before-fixture-cache-fix.json` and is invalidated as corrected-code evidence. The runner now installs selected bytes before the fixture executes any instruction. The original Phase61 failure remains valid and reproduces with this corrected fixture ordering. Initial six-case evidence is also preserved separately.

Evidence: [reservation_negative_test.py](<../../../builds/phase62-final-preflight/reservation_negative_test.py>), original-reservation-tests.json (local-only reference: `builds/phase62-final-preflight/original-reservation-tests.json`; not distributed), corrected-reservation-tests.json (local-only reference: `builds/phase62-final-preflight/corrected-reservation-tests.json`; not distributed), native-tests.json (local-only reference: `builds/phase62-final-preflight/native-tests.json`; not distributed), reservation-guard.asm (local-only reference: `builds/phase62-final-preflight/reservation-guard.asm`; not distributed), [fix_reservation_guard.py](<../../../builds/phase62-final-preflight/fix_reservation_guard.py>), correction-identity.json (local-only reference: `builds/phase62-final-preflight/correction-identity.json`; not distributed).

**PROVEN stop rule:** the requested negative gate failed on Phase61, so only this issue was fixed; the remaining preflight work was not started.
