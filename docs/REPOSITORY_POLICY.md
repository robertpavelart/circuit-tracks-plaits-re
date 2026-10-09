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
