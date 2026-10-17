> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: SUPERSEDED / DO NOT FLASH.

# Exact B1.3 application-updater replay

**PROVEN within explicit offline seams:** the exact existing Phase43 candidate SYX is accepted by the authenticated B1.3 application updater, staged byte-exactly and installed by the authenticated bootloader. This does not substitute an SC35D8 application updater for the B1.3 updater.

B1.3 image SHA-256 `2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41`, length 435220 (`0x6A414`). The reference manifest authenticates the COPY/ADD reconstruction; the complete installed application is loaded before the first native updater call. Exact incoming SYX SHA-256 `59be0e5733c70783c278ff5f89e575d77eef4dd3f6389841eac4a488111df32b`; decoded image SHA-256 `9b29180ff7f88c9c982c60abdfd5e5b296e8f2240ad57580366a5a7f797930a6`, CRC `AC9987BA`.

## Actual code/data/selector provenance

Native `08024D2C` vendor dispatcher, `08038CFC`/`08039088` state methods, block decoder `08024E20`, request queue, worker `08024014` and native NOR program/erase address algorithms execute from B1.3. The runner records every executed application PC and a digest of those actual B1.3 halfwords. It does not assign acceptance from a host protocol simulation. The worker's flag 1→erase-first 0 conversion executes rather than being assumed.

The selector fixture is separately authenticated by native B1.3 scatter decompression `080596C4`, descriptor `0805B7C8`, with poisoned output and independent decoder equality. All 80 bytes at `20003C88–20003CD7`, including records/table, equal the running-RAM fixture. Initialized data hash `2db584abde65123402067c89720f5a10e12c40650b700d6af2f13ed93743e04f` (15618 bytes). This closes selector provenance without claiming complete reset/constructors.

| Selector | Native record | Base | Capacity |

|---:|---|---|---|

| 0 | `20003C88` | `0` | `80000` |

| 1 | `20003C98` | `D4000` | `1F2C000` |

| 2 | `20003CA8` | `82000` | `12000` |

| 3 | `20003CB8` | `94000` | `40000` |

All table values are hex NOR byte offsets/capacities. `20003CC8` holds the four record pointers. `080390B6–080390D4` bounds/loads the selector and `08038ECA–08038EDE` derives the selected staging address. Actual candidate selector=0, staging base=0, capacity=`0x80000`; the boot internal-application size bound is separately `0x70000`.

## Exact selected footprint

All intervals are half-open, NOR offsets in bytes unless explicitly internal flash.

- NOR erase union: [0x0,0x5c000), [0x80000,0x81000). Exact individual sector/page operations are in the operations JSON.

- NOR program union: [0x0,0x5bca0), [0x80000,0x80017). Staged bytes 375948, padded 375968 (`0x5BCA0`), including 20 FF bytes; final staged SHA-256 `9b29180ff7f88c9c982c60abdfd5e5b296e8f2240ad57580366a5a7f797930a6`.

- Metadata: erase[0x80000,0x81000), program[0x80000,0x80017), raw 23 bytes `00000000050702000000050b0c080c0a0c090908070b0a`.

- Internal effective erase sectors: [08010000,08018000), [08018000,08020000), [08020000,08040000), [08040000,08080000). The extra 08080000 erase-wrapper call is a native no-op.

- Internal programs: [08010000,0806BCA0), 93992 four-byte words. Logical image ends 0806BC8C. Final 375948 bytes equal the decoded candidate; bootloader unchanged.

| Guarded NOR region | Direct program overlaps | Erase overlaps | Nearest program | Gap | Nearest erase | Gap |

|---|---:|---:|---|---:|---|---:|

| [81000,81017) | 0 | 0 | [80000,80017) | 4073 | [80000,81000) | 0, adjacent |

| [82000,82200) | 0 | 0 | [80000,80017) | 8169 | [80000,81000) | 4096 |

Synthetic sentinels verify these two selected-path preservation claims; they are not authentic NOR contents.

## Is metadata address movable to 81000?

**PROVEN for the native updater finalizer:** `0803901A–0803901C` permits metadata publication for selector 0. `0803902C MOV.W r1,#0x80000` supplies the address directly, length 23 at 08039022, erase-first 1 at 08039020/28. The address is **hardcoded**, not selector-, argument- or table-derived. Table-derived staging bases do not shift this publication to 81000. Boot metadata read 08003B36 and recovery publication 08007D28 independently use 80000. Within these decoded finalizers no alternate branch substitutes 81000.

**PROVEN distinction:** identity setter 08005DB4/app 08025228 intentionally writes 81000; this is a separate feature, not relocated updater metadata. Factory chip erase/resource-selector update can affect other regions. **UNKNOWN:** arbitrary corruption/indirect clients and complete normal boot/background mutation closure; this report does not prove global NOR immutability.

## Corrected candidate follow-up

The existing candidate was replayed unchanged first. A later native test proved its quarantine-store race. The separately named N44ATM correction was then replayed through actual B1.3 as well, with the same footprint and zero overlaps; its different CRC/metadata/hash are recorded separately. Do not conflate original identity with corrected identity.

## Explicit seams

**UNKNOWN beyond this model:** reset-to-ready constructors, actual timing/task scheduling, preparatory timer/DSP/UI acknowledgements, CRC peripheral, array-read completion, boot object construction and physical internal-flash primitives. Native queue/worker/address/validator/installer decisions run; those peripheral/RTOS completions are supplied at named seams. Not hardware recovery proof or full cold-boot write census.

Evidence: [transition_replay.py](<../../../builds/phase44-preflash-redteam-closure/transition_replay.py>), b 13-to-candidate-summary.json (local-only reference: `builds/phase44-preflash-redteam-closure/b13-to-candidate-summary.json`; not distributed), b 13-to-candidate-operations.json (local-only reference: `builds/phase44-preflash-redteam-closure/b13-to-candidate-operations.json`; not distributed), [selector_provenance.py](<../../../builds/phase44-preflash-redteam-closure/selector_provenance.py>), b 13-selector-provenance.json (local-only reference: `builds/phase44-preflash-redteam-closure/b13-selector-provenance.json`; not distributed), b 13-08038c90.asm (local-only reference: `builds/phase44-preflash-redteam-closure/b13-08038c90.asm`; not distributed), atomic-b 13-to-candidate-summary.json (local-only reference: `builds/phase44-preflash-redteam-closure/atomic-b13-to-candidate-summary.json`; not distributed).
