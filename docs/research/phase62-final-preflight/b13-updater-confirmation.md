> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: FAILED / SUPERSEDED / DO NOT FLASH.

# Actual B1.3 updater and selector — PROVEN scoped

The new B1.3→frozen-corrected replay loads installed image SHA-256`2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41`, not SC35D8 or4486. Every executed application staging instruction is checked byte-for-byte against that actual installed image. The incoming SYX is the frozen corrected file, and exact installed hash is`7d3964aabbba6e7dfe0cfa8b95b89294346bbeac49fcb20dd529609d6d507cd6`.

At executed native080390D0, actual registers give index0,R2=20003CC8 and selected pointer20003C88. The actual80 bytes at20003C88..3CD7 equal independently decoded B1.3 initialized data. Selected record gives NOR interface-pointer address20006968, service20003CD8, base0,capacity80000. This is an actual RAM selector witness, not a table assumed from stock names. The previously saved native B1.3 decompressor evidence independently authenticates the initialized-data source.

An instrumentation metadata mistake was caught during review:08039180 is **updater code**, not the selector table. The initial witness-less summary labeled a code-window hash as a selector-table hash. That initial summary is preserved with`code-window-mislabeled` in its filename and must not be used for selector proof. The updated B1.3 replay names it an updater code window and supplies the actual20003CC8 witness. The initial two rollback summaries retain the old helper field names; those fields are explicitly ignored for selector proof. Their exact-image/overlap results remain valid.

Evidence: b13-selector-confirmation.json (local-only reference: `builds/phase62-final-preflight/b13-selector-confirmation.json`; not distributed), b13-to-candidate-summary.json (local-only reference: `builds/phase62-final-preflight/b13-to-candidate-summary.json`; not distributed), [corrected_install_replay.py](<../../../builds/phase62-final-preflight/corrected_install_replay.py>), corrected-install-validation.json (local-only reference: `builds/phase62-final-preflight/corrected-install-validation.json`; not distributed). Peripheral/RTOS/UI/CRC/flash completion seams remain modeled; this is not a physical update.
