> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Changed header / stale staging / installation no-op

**PROVEN in the saved native transition scopes:** B1.3→corrected diagnostic, corrected diagnostic→official4486, and corrected diagnostic→B1.3 are accepted and actually install their intended image. No named transition silently succeeds without installation. Their compared38-byte headers are all distinct.

The persisted [update_dependency_review.py](<../../../builds/phase45-nor-mutation-closure/update_dependency_review.py>) and result (local-only reference: `builds/phase45-nor-mutation-closure/update-dependency-review.json`; not distributed) were recovered complete and not rerun. The result pins each exact Phase44 operation trace by SHA-256 and records all compared headers.

## Native decision, not a numeric downgrade assumption

Boot08003B9A checks metadata size≤70000, selector0 and non-FFFFFFFF CRC. Staged/boot compatibility header bytes+4/+5 must agree; staged CRC must pass. Native03BE4–03BF6 then compares38 bytes at application offset1C8–1ED. Equality skips internal installation; differing compatible headers install. This branch does not require a numerically higher version/build.

Saved native controls prove that numeric metadata version000000 still installs official4486, equal headers skip writes, and changed executable bytes with an equal compared header also silently no-op. The six-byte `N44ATM` marker at offset1E8 is within that comparison and prevents the original→corrected no-op. These controls do not demonstrate a failure of the three named distinct-header transitions.

| Transition | Actual selected model result | Final installed BIN SHA-256 |
|---|---|---|
| B1.3→corrected | Accepted; erased/programmed; byte-exact | `0e597f01e4af071bf2e96f3811b8edac1c1563960ba79b0fb32573d0fdae6738` |
| Corrected→official4486 | Accepted; erased/programmed; byte-exact | `b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da` |
| Corrected→B1.3 | Accepted; erased/programmed; byte-exact | `2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41` |

## Can an old staged image influence these completed transfers?

**PROVEN selected-trace dependency result:** every array READ in each completed transfer/install trace is dominated by a prior recorded erase/program covering all read bytes. Read counts are11845,9920 and13712 respectively; prior-array-byte dependency lists are empty. Final staged/installed hashes match. Thus the supplied array-read values in those traces do not depend on pre-existing staging/metadata content. Metadata at80000 is replaced only after successful CRC; a complete accepted new transfer does not accidentally install old staged bytes in these models.

This is not a universal theorem for interrupted uploads, torn erases, unsolicited intervening commands or corrupted callbacks. Before an upload completes, old metadata may remain; an automatic next boot can evaluate whatever valid staged/header/CRC state exists then. Such interruption is not a silently successful completion of the tested named transitions. No guarantee about every power-cut boundary is made.

## Recovery versus application intake

Application uses native24D2C/state38*/39* and its live RTOS queue/worker under explicit peripheral seams. Recovery uses the bootloader's own59C4/59FA/7B*/7C*/7D* logic and modeled boot storage objects. They are not equivalent replays. Saved own-recovery tests accept official and original streams from corrupt application/staging; corrected-SYX own-recovery intake also passes. Application validity is not an intake prerequisite in those paths. Both ultimately use03B9A/03C24 for internal installation.

**PROVEN user-reported hardware observation:** bootloader/recovery mode can be entered, and the unit can exit recovery and boot B1.3 normally. **UNKNOWN:** rollback flashing on that physical unit; the user did not report testing it. This observation does not replace the offline model's explicit seams.

Evidence: [Phase44 transition report](<../phase44-preflash-redteam-closure/rollback-transition-replay.md>), header no-op control (local-only reference: `builds/phase44-preflash-redteam-closure/header-noop-control.json`; not distributed), [own recovery model](<../phase44-preflash-redteam-closure/recovery-mode-model.md>), corrected own-recovery supplement (local-only reference: `builds/phase44-preflash-redteam-closure/atomic-supplement.json`; not distributed).
