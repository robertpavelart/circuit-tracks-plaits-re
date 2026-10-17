# Repository Policy

## Commit

- user-authored analysis code
- project-authored emulator instrumentation/tests
- integration/test harnesses
- redistributable Plaits-derived code
- reports and exports that do not embed proprietary firmware
- documentation

## Keep local

Do not commit:
- Novation `.syx` / firmware binaries
- extracted DSP payloads
- vendor ROM dumps
- NXP manuals/PDFs
- Components caches
- user projects / patches / samples
- device dumps
- generated firmware images derived from proprietary firmware

The local working tree is:

`C:\Proj SSD\CODEX\CIRCUIT`

Do not bulk-push the original local working tree. This packaged snapshot contains the reviewed subset intended for the repository.

## Selective publication boundary

Only individually reviewed project-authored text source may be tracked from historical build directories; their generated outputs remain excluded/ignored. Do not replace this allowlist process with a bulk copy or git add of the original research workspace. Hashes, addresses and narrative findings are metadata, not permission to distribute firmware bytes, disassembly payloads or device snapshots. Required derivative-source license notices must remain. HARDWARE-ATTEMPT.json, credentials, caches and user content must never be staged. See SOURCE_IMPORT.md for the current subset and omitted-input limits.
