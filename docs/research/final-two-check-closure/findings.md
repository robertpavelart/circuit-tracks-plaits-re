> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Final two-check closure

POST-READY ALLOCATION CENSUS: UNQUALIFIED

USB STORAGE JOINT PATH: PASS

**UNKNOWN — allocation conclusion D:** the conservative frozen-byte traversal encounters unresolved callback targets. In particular, resolving Main's outer Content completion callback to `08022E08` still leaves its inner payload callback at `08022E22` unbounded. Subscriber/timer registration writer closure is also incomplete. No allocation greater than eight bytes was demonstrated after READY, but absence and safe exhaustion handling are not proven. This remains software-reachability uncertainty, not merely physical enumeration uncertainty.

**PROVEN within the declared joint fixture:** all 36 new tests pass. Static control-path reasoning and the tests distinguish asynchronous USB packet reception from Main-context media submission. Both request orders, disconnect, timeout, missing/late completion, TEF, remount, BOT reset and class deconfiguration preserve the tested raw-frame/backend/DMA ownership invariants. See `usb-joint-closure.md` for exact addresses and model limits.

Evidence:

- `allocation-closure.md`, `reachability.py`, `reachability.json`, `indirect-sources.tsv`: 78 roots, 18 bounded switches, 206 encountered indirect sites, 189 unresolved; incomplete by explicit design at proof boundaries.
- `usb-joint-closure.md`, `joint_tests.py`, `joint-results.json`: 36 new native/model joint cases, all passing; declared USB/scheduler/clear-helper seams.
- `byte_audit.py`, focused `.asm` files, `service-xrefs.json`: frozen-candidate instruction evidence.
- `validation.json`: read-only package verification and saved-result consistency.

**PROVEN:** all 633 entries of the existing package hash manifest verify. The candidate, firmware/reference sources, package README, HASHES, gate and historical `final-cheap-checks.md` remain unchanged. The user's conditional package-update requirement was not triggered because both checks did not close. Existing passed tests were read, not restarted; only new focused joint cases were executed. No hardware, MIDI, firmware transmission or new firmware generation occurred.

Smallest next work is callback-producer/registration closure on the allocation side, starting with the inner Content completion callback `08022E22`; no new peripheral modeling is indicated. No concrete firmware defect was established. No live tool is unlocked or released by the joint-path result.

OPERATIONAL PREFLIGHT = UNQUALIFIED
