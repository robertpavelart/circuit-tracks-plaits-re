> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# NOT YET HARDWARE-APPROVED

All files here are offline design/test evidence. No flash-ready application image or firmware-update SYX is present.

- `arm-diagnostic.fragment.bin`: ARM code fragment only; not a firmware image. `patch-plan.json` contains the exact additional byte changes proposed for a future separately reviewed package.
- `synthetic-transcript.syx`: SYNTHETIC DEVICE-REPLY TRANSPORT DATA; DO NOT TRANSMIT TO A DEVICE. This is not an update stream or an authenticated dump.
- `synthetic-host-output/received.syx`: SYNTHETIC DEVICE-REPLY TRANSPORT DATA; DO NOT TRANSMIT TO A DEVICE.
- `synthetic-data.bin` and `synthetic-host-output/qspi_00082000_000821ff.bin`: synthetic test bytes only. Their companion metadata explicitly identifies their synthetic origin. Never use these as stock coefficients or phase26 provenance evidence.
- `receiver.py`: `request` and `receive` operate on local files. Only the explicit `live` command imports the existing WinMM connector and opens ports. Live mode was not invoked. It is for a later separately approved hardware phase.
- `test_offline.py`: uses authenticated stock code/RAM plus synthetic bytes and explicit peripheral/RTOS/output models; never calls `ctremote.Link` or WinMM.
