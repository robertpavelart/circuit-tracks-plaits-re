> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: SUPERSEDED / DO NOT FLASH.

# Phase44 — preflash red-team closure

2026-10-16. **UNKNOWN: complete preflash closure; no hardware action is justified by this phase.** The highest-value selected updater, rollback, recovery-intake, host and terminal-state questions now have native/offline evidence. Complete ordinary boot/background NOR mutation-producer reachability is still an offline technical blocker. It is not relabelled as a hardware-only timing unknown.

No hardware was accessed, no MIDI ports were opened, no live port inventory ran, and no firmware was transmitted. Phase43/reference/pinned artifacts remain unchanged. A new, separately named candidate was generated **only after an exact native test proved the original candidate's terminal-quarantine contract invalid**. The reason, minimal patch and separate identities are below. No Plaits code or unrelated firmware feature was changed.

## A — Exact B1.3 updater

**PROVEN within explicit model seams:** exact original candidate SYX `59be0e5733c70783c278ff5f89e575d77eef4dd3f6389841eac4a488111df32b` passes the actual authenticated B1.3 application updater. B1.3 image SHA-256 `2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41`, size 435220. Native B1.3 code, native queue/worker/flag conversion and authenticated selector data are used, not SC35D8 as the installed updater.

Selector 0, staging base 0, capacity 0x80000. NOR staging erase[0,5C000), padded program[0,5BCA0). Metadata erase[80000,81000), program[80000,80017), hardcoded at native 0803902C independently of selector-derived staging. Neither guarded region [81000,81017) nor [82000,82200) has any direct-program or erase overlap. Nearest actual program is metadata, gaps 4073/8169; nearest erase is metadata sector, gaps 0(adjacent)/4096.

The separately corrected candidate also passes the B1.3 updater byte-exactly with identical footprint. Exact sector/page lists, raw metadata, final staged hash, four internal erases, padded internal programming and limits are in [b 13-updater-replay.md](<b13-updater-replay.md>) and its linked JSON. Selector provenance (local-only reference: `builds/phase44-preflash-redteam-closure/b13-selector-provenance.json`; not distributed) authenticates the native scatter output, not just a guessed running-RAM table.

## B — Rollbacks and version decisions

**PROVEN scoped:** original B1.3→candidate, candidate→official 4486, candidate→B1.3 all accept and actually install their exact expected image hashes; no requested transition silently no-ops. All three are additionally repeated with the corrected candidate. See [rollback-transition-replay.md](<rollback-transition-replay.md>).

Native 08003B9A checks size, selector, compatible staged/boot header bytes and CRC. It then compares 38 staged/current header bytes at image offset 1C8–1ED; equality skips installation. It does not enforce numeric newer-version ordering on this branch. Native controls prove lower numeric metadata version is accepted and changed executable code with an unchanged compared header silently no-ops. N44ATM changes the six marker bytes within that compared header so the corrected image can install over the original. B1.3 rollback SYX is reconstructed only in memory and admitted only if its complete hash matches published manifest `6f07376b5983a5e0350d4883ae9ed57a69bc735320afde9f43ca75017b8e8736`; no new B1.3 SYX file was written.

## C — Bootloader's own recovery intake

**PROVEN scoped:** native 080059C4/080059FA and bootloader-owned 07B*/07C*/07D* state methods accept full original candidate and official streams independently of the application updater, starting with corrupted application/staging. Ten native validation/install cases cover all requested conditions plus same-header no-op and lower-version controls. Valid staged images install over garbage/erased current applications; bad CRC/partial metadata do not erase/program internally. Metadata is published at hardcoded 80000 after CRC success, remains through installation, and a later valid recovery upload can replace modeled corrupt prior state. The corrected final SYX separately passes own recovery intake and installs its exact final hash.

**UNKNOWN:** full reset-to-USB initialization, real key sampling/USB readiness, all power-loss boundaries and physical recovery. Boot objects/storage completions are explicitly modeled; no guarantee of hardware recovery follows. See [recovery-mode-model.md](<recovery-mode-model.md>) and corrected supplement (local-only reference: `builds/phase44-preflash-redteam-closure/atomic-supplement.json`; not distributed).

## D/E — Mutation census and original-evidence value

**PROVEN:** reviewed native page-program, sector-erase, chip-erase, worker/vtable and identity callbacks are catalogued for bootloader, B1.3 and original candidate. Fixed diagnostic additions only read. Identity setter 08005DB4/app 08025228 programs 23 bytes at 81000 and erases[81000,82000), ending exactly before coefficients. The corrected image changes only marker/terminal-state logic; every stock mutation body remains byte-identical.

**PROVEN conditional capability:** a stock resource-selector 2 update targets the bundle beginning 82000. Native boot recovery SysEx 77 with two magic endpoints can reach whole-chip erase (08005A40→08005940→08005410→080078E4); application has an equivalent path. Therefore “no boot/update/recovery path can erase 82000” would be false. The actual selected application SYX, recovery SYX and capture requests do not select those commands.

**STRONG INFERENCE:** intended selector 0 installation plus fixed read capture preserves the coefficient prefix more strongly than identity: neither normal metadata nor identity-sector erase reaches 82000, and the known initializer is read-only. A post-install identity capture is weaker because explicit setters can rewrite its normalized cache, including byte 14. Both must retain post-install provenance; neither is an unconditional pre-experiment snapshot.

**UNKNOWN — offline blocker:** direct-call candidate enumeration is not full indirect/queue-producer reachability. Normal boot/background/persistent client address/predicate closure remains open. Selected replays with zero overlaps cannot close the unexecuted ordinary boot suffix. See [nor-write-erase-census.md](<nor-write-erase-census.md>) and [evidence-preservation.md](<evidence-preservation.md>).

## F — Host one-shot correction

**PROVEN offline:** Phase44 copies now select/open/prepare ports before permanently committing the one-shot marker immediately before send. No-match, ambiguity, permission/open/setup failures send zero requests, leave no marker and require no device power cycle for that unsent attempt. A new read-only `ports` command is mock-tested to open no ports/send no bytes. Nothing live was invoked.

Once sending may begin, including ambiguous delivery failure, the marker remains burned; no retry/second request/Storage cleanup occurs, partial output is rejected, and the tool prints FULL POWER CYCLE REQUIRED. Complete 535-byte acceptance, 5-second tail observation and atomic two-file publication remain. All 25 inherited host cases and 17 new mocked cases pass. See [host-one-shot-audit.md](<host-one-shot-audit.md>). Archived Phase43 host code is unchanged and does not contain this fix.

## G — Atomicity failure and smallest correction

**PROVEN:** after 0806B9E4 reads ACTIVE, SysTick can quarantine the native latch; stale-register execution at 0806B9EC then overwrites it with SUCCESS. Earlier coarse final-TX injection missed this exact instruction boundary. This is a success/quarantine classification defect, not a reproduced extra request or corrupted sample payload: both terminal states reject admission. It nevertheless violates the promised monotonic quarantine contract.

**PROVEN correction:**32-byte PRIMASK-preserving fragment in existing FF slack[0806BC30,0806BC50), one branch at 0806B9DC, markerN 44ATM. Six original boundary cases preserve the failing evidence; 25 corrected mask/boundary/terminal checks pass. All 25 inherited coupled native cases, 512 final-file opcode/port cases, 20-tick dormancy, native USB→revised-host capture, native boot intake and all three corrected transition replays pass. See [success-quarantine-atomicity.md](<success-quarantine-atomicity.md>).

## Artifact identities and disposition

The original Phase43 candidate remains unchanged as evidence; it is superseded for terminal-quarantine correctness. The corrected **offline research artifact is not hardware-approved** while D/E remains open.

| Artifact | Bytes | SHA-256 | BIN CRC-32/MPEG-2 |

|---|---:|---|---|

| Original Phase43 SYX | raw instruction bytes omitted | `59be0e5733c70783c278ff5f89e575d77eef4dd3f6389841eac4a488111df32b` | AC 9987BA |

| Original Phase43 BIN | raw instruction bytes omitted | `9b29180ff7f88c9c982c60abdfd5e5b296e8f2240ad57580366a5a7f797930a6` | AC 9987BA |

| Phase44 circuittracks-4486-nor-evidence-atomic-test.syx | raw instruction bytes omitted | `1fc80908552cd1901e52559cf8117e9fbf5c878b258c79c6cdea2572ceb031af` | DDED2621 |

| Phase44 circuittracks-4486-nor-evidence-atomic-test.bin | raw instruction bytes omitted | `0e597f01e4af071bf2e96f3811b8edac1c1563960ba79b0fb32573d0fdae6738` | DDED2621 |

39 changed bytes total versus original, solely branch/fragment/marker; zero image growth, zero additional heap/data allocation, vectors/DSP unchanged. Bootloader/option bytes are not changed. Phase43's existing 12-byte latch reservation and H4 FAIL remain. No Plaits or musical feature is added.

## BLOCKERS REMAINING

- **UNKNOWN:** close actual ordinary boot-to-capture NOR mutating-request producers, address bounds and predicates across queue/vtable/indirect clients, especially resource selector 2 and chip erase. This is an offline E 2/E 3 original-evidence-preservation blocker. Do not use unchanged physical timing as a substitute for this proof.

- **UNKNOWN:** unconditional identity/pre-experiment coefficient equality across the entire first boot. Required next offline work is the smallest bounded producer/address proof for the intended normal boot-to-capture schedule, excluding unintended maintenance/resource-update input explicitly. If the closure depends on missing data, retain that dependency rather than fabricate NOR values.

## SHOULD VERIFY

- Independently review the changed-code/same-header no-op control, N44ATM marker and PRIMASK fragment/diff before promoting any corrected candidate.

- Use Phase44 revised host, not archived Phase43 host, in any later separately chosen test; verify hashes and preserve attempt-marker policy.

- Keep the two evidence regions' provenance separate and archive only complete accepted captures. No inference from synthetic bytes or reset cache zeroes.

- Preserve exact selected-model boundaries, reference/source hashes and H4 no-unwind policy. A general factory erase is not a recovery procedure for this project.

## ACCEPTABLE HARDWARE-ONLY UNKNOWN

**UNKNOWN:** physical oscillator/IRQ/DMA/USB/WinMM timing, actual fresh-boot heap headroom, actual NOR part/fault behavior and unit-specific button/recovery behavior remain physical observations, not offline proofs. Those do not excuse the still-open offline write-producer closure above. There is no claim of absolute safety or recovery guarantee.

No hardware action follows. Stop at the offline blocker and its documented next experiment.

PREFLASH REDTEAM CLOSURE = UNQUALIFIED
