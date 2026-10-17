> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: SUPERSEDED / DO NOT FLASH.

# Static NOR mutation census

**PROVEN:** this audit reads the authenticated B1.3 published COPY/ADD spans, the unchanged 64-KiB boot dump, and the existing Phase43 BIN. No firmware image is generated. [nor_census.py](<../../../builds/phase44-preflash-redteam-closure/nor_census.py>) verifies B1.3 against its published manifest and Phase43 against SHA-256 `9b29180ff7f88c9c982c60abdfd5e5b296e8f2240ad57580366a5a7f797930a6`. Exact image hashes, immediate call candidates and aligned function-pointer candidates are in nor-census.json (local-only reference: `builds/phase44-preflash-redteam-closure/nor-census.json`; not distributed). Byte-derived listings are bootloader (local-only reference: `builds/phase44-preflash-redteam-closure/nor-bootloader.asm`; not distributed), B1.3 (local-only reference: `builds/phase44-preflash-redteam-closure/nor-B13.asm`; not distributed) and candidate (local-only reference: `builds/phase44-preflash-redteam-closure/nor-candidate.asm`; not distributed).

**UNKNOWN:** complete indirect-call/queue-producer reachability for every stock storage client. Exhaustive halfword decoding finds *candidates*, including data that can decode as instructions; it cannot certify all reachable functions or rule out computed pointers. The following is the complete direct mutation-helper call census found by that scan, augmented by reviewed queue dispatch and identity callback paths. It is not a claim that the whole asynchronous cold-boot graph has been executed.

## Physical primitives and direct callers

All ranges are external NOR byte offsets, half-open. App addresses below are identical in authenticated B1.3 and Phase43; their listed code-body hashes are in the ASM evidence.

| Helper / call site | Caller / trigger | Address and length source | Boot | Normal idle | SysEx | Recovery | Fixed diagnostic |

|---|---|---|---|---|---|---|---|

| Boot page program `$08007770`, call `$080053F6` | Backend write `$08005380` | Arguments `r1=start,r2=buffer,r3=count`; loops in pages at most `$100` bytes | CONDITIONAL storage job | Not application | YES updater | YES updater | NO |

| Boot sector erase `$08007730`, call `$08005474` | Backend erase `$08005410` | `r1=start,r2=end`; `$1000` stride | CONDITIONAL storage job | Not application | YES updater | YES updater | NO |

| Boot chip erase `$080078E4`, call `$0800545E` | Backend erase `$08005410` | **Both** endpoints equal `$CF525EB4`; whole array | No spontaneous boot call identified | Not application | YES command `$77` with two magic values | YES same intake | NO |

| App page program `$080374D4`, call `$0802305E` | Backend write `$08022FDC` | Arguments `r1=start,r2=buffer,r3=count`; pages at most `$100` | CONDITIONAL queued job | CONDITIONAL queued job | YES updater | App not running | NO |

| App sector erase `$08037494`, call `$080230DC` | Backend erase `$08023078` | `r1=start,r2=end`; `$1000` stride | CONDITIONAL queued job | CONDITIONAL queued job | YES updater | App not running | NO |

| App chip erase `$08037648`, call `$080230C6` | Backend erase `$08023078` | **Both** endpoints `$CF525EB4`; whole array | No spontaneous call identified | No spontaneous call identified | YES factory/maintenance `$77` path | App not running | NO |

**PROVEN:** the reviewed NOR erase backends implement sector stepping and whole-chip erase, not a separate 32/64-KiB block-erase branch. Sector descriptors select `$20/$21`, program `$02/$12`, with WREN `$06`. **UNKNOWN:** no claim that arbitrary raw controller clients or unclosed indirect code cannot issue another opcode. Merely finding `$D8` or `$52` bytes somewhere in an image would not establish a block-erase API.

## Indirect and queued mutation edges

| Site / function | Exact edge / trigger | Address/length source and bounds | Reachability classification |

|---|---|---|---|

| Boot `$080053A4` in backend write | Optional pre-program erase through backend vtable `+0x14` | `[start,start+count)`; fifth write argument controls erase-first | PROVEN conditional boot updater/identity write; generic callers UNKNOWN |

| App `$08022FDC` write backend | Optional pre-program erase through backend vtable `+0x18` | `[start,start+count)`; fifth argument controls erase-first | PROVEN conditional queued write; generic client closure UNKNOWN |

| Boot Storage worker / descriptor layer | Wrapper `$080058B4` copies WRITE record, `$08005908` synchronous ERASE, `$08005940` asynchronous ERASE; submit `$080056B8` | Request start/buffer/count, erase end converted to length | PROVEN interfaces; individual queue producers beyond selected updater UNKNOWN |

| App `$080240B2` in worker `$08024014` | Backend vtable `+0x10`, WRITE case | Descriptor `+4=start,+8=buffer,+0xC=count`; record flag 1 maps to erase-first **0** | PROVEN Storage-thread edge; boot/idle conditional on request, updater YES, diagnostic NO |

| App `$080240C2` in worker | Backend vtable `+0x18`, ERASE case | Descriptor start at `+4`; end=`start+[+0xC]` | PROVEN Storage-thread edge; boot/idle conditional on request, updater YES, diagnostic NO |

| App queue submit `$08023F68` | Immediate candidate sites `$0802411C,$08024154,$08024196,$080241AC,$080241DC,$08026C10` | Templates / caller fields; not all are write records | PROVEN call candidates; generic template/client closure UNKNOWN |

| Boot identity setter `$08005DB4`, indirect call `$08005DCA` | Callback pointer `$08003A8C=08005DB5`; installed by constructor `$08003A32–38` | Hardcoded `$81000`, RAM `$2000546C`, 23 bytes, erase-first=1 | PROVEN identity SysEx callback; ordinary boot constructor reads and stores callback, not invokes it; complete indirect closure UNKNOWN |

| App identity setter `$08025228`, indirect call `$0802523E` | Callback pointer `$0801EDEC=08025229`; installed `$0801ECA4–AA` | Hardcoded `$81000`, RAM `$20006868`, 23 bytes, erase-first=1 | PROVEN identity SysEx callback; ordinary constructor reads, not writes; boot/idle non-command invocation UNKNOWN |

| Boot `$08005EBC` callback invocation | Identity handler `$08005E88`, vendor `$70`/subcommand `$6C` path | 14 ASCII alphanumeric bytes validated, copied into 23-byte cache, invokes setter callback | PROVEN recovery maintenance mutation path; not the capture command |

| App `$08025338` callback invocation | `$0802527C` dispatch: vendor `$70`, subcommand `$6C`, enable bit `$10`, exact 14-byte payload | `$080252F8`: new 14 bytes valid, old cached 14 bytes invalid, then copy 14 and callback | PROVEN conditional identity mutation; no automatic constructor write in this body |

| Boot `$08005A40` | SysEx `$77`, two packed arguments decoded by `$08007E28`, both equal literal `$CF525EB4` at `$08005CE8` | Async erase `$08005940` receives magic endpoints | PROVEN whole-chip erase route; not needed by normal app installation |

| App `$08024DB0` | SysEx `$77`, decoder `$0803913C`, both arguments `$CF525EB4` literal `$08025018` | Async erase `$080241F0` receives magic endpoints | PROVEN whole-chip erase route in both B1.3 and candidate; not fixed diagnostic |

**PROVEN:** indirect targets are real, not made unreachable merely by absence of `BL` instructions. Boot vtables contain write `$080058B5` at `$080095A8`, backend write `$08005381` at `$080095D0`, erase `$08005411` at `$080095D4`. B1.3/candidate backend write pointer `$08022FDD` occurs at `$0805B1BC`, erase `$08023079` at `$0805B1C4`. Function-pointer relationships require the object/vtable context as well as the pointer value.

## Target-region consequences

| Region | Selected purpose / mutation source | Effect |

|---|---|---|

| `[$80000,$80017)` | Updater metadata publication | Program 23; erase sector `[$80000,$81000)`; no overlap with either evidence region |

| `[$81000,$81017)` | Identity/settings setter above | Program 23; erase `[$81000,$82000)`; destroys previous identity sector contents, **ends exactly at** coefficient region |

| `[$82000,$82200)` | First 512 bytes of resource bundle selector 2 (`[$82000,$94000)`) | A selector 2 resource update can erase/program it; generic chip erase destroys it; normal selected app selector 0 update does not require either operation |

**PROVEN:** the answer to “can ANY boot/update/recovery path write or erase `$82000–$821FF`?” is **yes, conditionally**: the explicit native recovery `$77` maintenance command reaches whole-chip erase. The application has the equivalent route. A statement that no such code exists would be false. This does **not** mean the exact candidate SYX contains that command, or that ordinary boot issues it.

**STRONG INFERENCE:** the intended candidate installation and fixed diagnostic capture do not require or select those mutation routes. **UNKNOWN:** complete first-boot/background NOR write exclusion remains a separate predicate/queue-producer closure problem. Selected full transfer replays and bounded diagnostic operation guards cannot, by themselves, settle every possible persistent stock client.

**PROVEN:** fixed diagnostic additions choose only operation 1 READ, addresses `$81000` and `$82000+64*k`, length 23 or 64; no write/erase command is added. The exact Phase43 native replay sweeps all 256 opcodes over USB/DIN and guards mutation entries ([Phase43 findings](<../phase43-hardware-test-candidate/findings.md>), [Phase42 replay](<../../../builds/phase42-exact-rdiag-integration/replay.py>)). Inherited stock maintenance/updater facilities are separate.

## Remaining closure

**UNKNOWN:** there is not yet an exhaustive computed-target/queue-producer proof that every ordinary cold-boot/persistent B1.3 client is incapable of selector 2 or chip erase. Minimum remaining offline work is a bounded producer/address proof for the actual normal boot-to-capture schedule, with mutating worker record addresses instrumented, and explicit exclusion of maintenance input `$77` and resource-selector uploads. A raw literal scan is insufficient. Preserve this limitation even if every selected update/recovery replay has zero overlap.
