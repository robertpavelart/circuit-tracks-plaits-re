> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: SUPERSEDED / DO NOT FLASH.

# Rollback transition replay

**PROVEN within the native offline application-updater/boot-installer model:** all three requested transitions accept and actually erase/program the destination. None silently no-ops. Original Phase43 and corrected N44ATM cases are kept separate. All sizes/addresses below are byte units and half-open.

## Original exact Phase43 candidate

| Transition | Incoming bytes | NOR staging erase | NOR staging program (padded) | Internal program | Final installed SHA-256 |

|---|---:|---|---|---|---|

| b 13-to-candidate | 375948 | [0x0,0x5c000) | [0x0,0x5bca0) | [0x8010000,0x806bca0) | `9b29180ff7f88c9c982c60abdfd5e5b296e8f2240ad57580366a5a7f797930a6` |

| candidate-to-official | 314844 | [0x0,0x4d000) | [0x0,0x4cde0) | [0x8010000,0x805cde0) | `b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da` |

| candidate-to-b 13 | 435220 | [0x0,0x6b000) | [0x0,0x6a420) | [0x8010000,0x807a420) | `2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41` |

Every row uses selector 0/base 0/capacity 80000. Every row additionally erases metadata [80000,81000), programs 23 bytes [80000,80017), and performs the same four internal erase sectors [08010000,08018000), [08018000,08020000), [08020000,08040000), [08040000,08080000). Application code does not execute after handoff in this model. Every target direct-program/erase overlap is zero; nearest mutations to both targets are the same metadata ranges/gaps as b 13-updater-replay.md.

B1.3 rollback SYX was not found as a standalone file locally. The existing published B1.3 image was encoded **only in memory**, and the resulting complete stream must match manifest SHA-256 `6f07376b5983a5e0350d4883ae9ed57a69bc735320afde9f43ca75017b8e8736` before replay. No new B1.3 firmware/SYX file was produced. This is exact authenticated-stream reconstruction, not a guessed substitute.

## Version/build and silent no-op decisions

**PROVEN:** application header handling admits protocol/header values and selects the storage record; actual complete transfers reach CRC success/publication. In boot 08003B9A: size must be≤70000, selector 0, CRC!=FFFFFFFF. Staged header compatibility bytes+4/+5 must match boot header 080001C8+4/+5; CRC must pass. Then 08003BE4–08003BF6 compares 38 staged/current header bytes at image offset 1C8 through 1ED. Equal headers skip 08003C24 installation; different compatible headers install. There is no numeric “newer than current build” comparison on this executed branch.

**PROVEN controls:** same valid image/header does zero internal writes; numeric metadata version 000000 still installs official 4486; changed executable code with an unchanged compared header also silently no-ops. Changing only the six-byte N44ATM marker inside that header makes the corrected image install over original Phase43. Therefore future binary edits must change that compared identity, not just CRC.

Metadata remains present after native validator/installer; it is not cleared there. A subsequent valid upload replaces it only after successful staging/CRC publication. Exact raw metadata per transition is in its summary JSON. It must not be described as an authenticated device metadata capture.

## Corrected N44ATM candidate follow-up

Corrected BIN `0e597f01e4af071bf2e96f3811b8edac1c1563960ba79b0fb32573d0fdae6738`, SYX `1fc80908552cd1901e52559cf8117e9fbf5c878b258c79c6cdea2572ceb031af`, CRC `0xdded2621`.

| Transition | Acceptance/install | Final installed SHA-256 |

|---|---|---|

| b 13-to-candidate | Accepted; actual install; no no-op | `0e597f01e4af071bf2e96f3811b8edac1c1563960ba79b0fb32573d0fdae6738` |

| candidate-to-official | Accepted; actual install; no no-op | `b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da` |

| candidate-to-b 13 | Accepted; actual install; no no-op | `2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41` |

All corrected-case footprints and target overlaps match their original-case counterparts; only the candidate payload/CRC/metadata/identity changes. The corrected B1.3-to-candidate install is separately asserted byte-exact, not inferred from header compatibility. Own bootloader recovery intake is covered in recovery-mode-model.md and atomic-supplement.json, separately from these application-updater transitions.

**UNKNOWN:** hardware timing, actual physical flash/NOR faults, complete boot-to-capture mutation exclusion, every torn-install boundary and unit recovery. No hardware action occurred.

Evidence: [transition_replay.py](<../../../builds/phase44-preflash-redteam-closure/transition_replay.py>), header-noop-control.json (local-only reference: `builds/phase44-preflash-redteam-closure/header-noop-control.json`; not distributed), recovery-results.json (local-only reference: `builds/phase44-preflash-redteam-closure/recovery-results.json`; not distributed), atomic-candidate-identity.json (local-only reference: `builds/phase44-preflash-redteam-closure/atomic-candidate-identity.json`; not distributed), b 13-to-candidate-summary.json (local-only reference: `builds/phase44-preflash-redteam-closure/b13-to-candidate-summary.json`; not distributed), candidate-to-official-summary.json (local-only reference: `builds/phase44-preflash-redteam-closure/candidate-to-official-summary.json`; not distributed), candidate-to-b 13-summary.json (local-only reference: `builds/phase44-preflash-redteam-closure/candidate-to-b13-summary.json`; not distributed), atomic-b 13-to-candidate-summary.json (local-only reference: `builds/phase44-preflash-redteam-closure/atomic-b13-to-candidate-summary.json`; not distributed), atomic-candidate-to-official-summary.json (local-only reference: `builds/phase44-preflash-redteam-closure/atomic-candidate-to-official-summary.json`; not distributed), atomic-candidate-to-b 13-summary.json (local-only reference: `builds/phase44-preflash-redteam-closure/atomic-candidate-to-b13-summary.json`; not distributed).
