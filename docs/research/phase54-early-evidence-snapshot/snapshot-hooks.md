> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase54 — proposed minimal hooks, not an implemented patch

| Item | Exact candidate / requirement | Confidence |

|---|---|---|

|81000 application hook |Replace25222 MOVS r2,#0 and25224 STRB [r4,#E] with a4-byte B.W to private ARM code; inspect R0 before clobber; copy23 from r4; replay both displaced instructions and return25226 |PROVEN instruction boundary; UNKNOWN final patch qualification |

|82000 hook |Replace35EE6 LDR r0,literal and35EE8 LSRS r2,r7,#16 with4-byte B.W; inspect R0, verify first expected descriptor/length/offset and first-capture state; copy512 from[20006A00]; replay displaced instructions, including flags; return35EEA |PROVEN instruction boundary; UNKNOWN final patch qualification |

| Reset initialization |Set EMPTY once before first application read; never reinitialize on later engine/table reload |UNKNOWN site/all reset-path coverage |

| Completion observer |If required, latch DMA/QSPI request generation, target/count/error/completion before flags disappear |UNKNOWN extra hook sites and bytes; a two-copy-hook design alone is insufficient |

| Code site replacement |Two4-byte branches =8 replaced ARM bytes |PROVEN arithmetic, conditional proposal |

| Added code/flash placement |Copy/state/check helpers, reset and completion observers, export change and veneers |UNKNOWN exact bytes and safe code pool; no assembled patch |

| Fixed RAM |535 payload + minimum1-byte five-valued state =536 logical bytes; word-aligned23-byte area padded24 +512 +4-byte state =540 bytes before any guards/checksum/completion metadata |PROVEN arithmetic; UNKNOWN owned address |

| Stack delta |A leaf design can avoid a payload stack buffer; register/flags preservation still needs a specified ABI and scratch storage |UNKNOWN actual maximum; not claimed zero |

| Boot cycles |Exactly535 payload bytes must be copied once; instruction count/wait states, cache/IRQ stalls and integrity work depend on implementation |UNKNOWN; no cycle number inferred from byte count |

| Interrupt masking |Do not mask around the535-byte copy or any Storage wait; publish only after full copy; brief atomic metadata update may be required |STRONG INFERENCE design; UNKNOWN exact masking count |

Sources: app-0802520c.asm (local-only reference: `builds/phase54-early-evidence-snapshot/app-0802520c.asm`; not distributed), app-08035e28.asm (local-only reference: `builds/phase54-early-evidence-snapshot/app-08035e28.asm`; not distributed), reader-boundaries.json (local-only reference: `builds/phase54-early-evidence-snapshot/reader-boundaries.json`; not distributed), [completion-authentication.md](<completion-authentication.md>).

**STRONG INFERENCE:** inserting a leaf copy after the synchronous wrapper has returned can preserve original request/semaphore/DMA ownership: it submits nothing, releases nothing, does not edit descriptors, does not clear hardware flags and leaves the stock source unchanged. Preserve all native-visible registers/SP/LR and condition flags at continuation, including displaced flag-setting operations. Keep all original stock control flow and byte14 normalization. Failure only suppresses diagnostic validity; it must not attempt a forced Storage unwind or a new NOR read. These invariants require native before/after tests of the eventual patch; the boundary tests are not such a patch test.

**UNKNOWN:** a safe validated implementation of the copy hook if another task can recycle the staging buffer between return and copy, or if the first read is incomplete but returns0. Completion and liveness gates must close first. No branch bytes, firmware, SYX or hardware candidate are produced in this phase.
