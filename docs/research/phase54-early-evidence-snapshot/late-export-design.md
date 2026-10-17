> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase54 — volatile snapshot state and RAM-only export

**STRONG INFERENCE — proposed contract, not firmware:** reserve two immutable payload areas plus state initialized EMPTY before either acquisition. State encoding may be0 EMPTY,1 81000_VALID,2 82000_VALID,3 BOTH_VALID,4 FAILED. Copies commit their corresponding valid bit only after qualified completion and full copy. Either order is representable even though the known Main path reads A first. A failure from any nonterminal state moves to FAILED; FAILED is absorbing until reset, never a retry admission. BOTH payloads remain immutable. Duplicate stock table initialization must not replace an accepted snapshot; it is not another acquisition. An export request never triggers a missing acquisition.

| State/event | Required action |

|---|---|

|EMPTY + authenticatedA |Copy23; publish81000_VALID |

|EMPTY + authenticatedB |Copy512; publish82000_VALID |

|81000_VALID + authenticatedB / reverse |Copy missing region; publishBOTH_VALID last |

|Any incomplete, failed or unverifiable read |FAILED, no export; if stock wait never returns, post-hook cannot set FAILED—completion observer remains required |

|Already accepted region read again |Do not update snapshot; no diagnostic retry or NOR submission |

|FAILED + any host request |Reject, no rearm, no storage cleanup |

|NotBOTH + export |Reject, no payload completion |

|BOTH + integrity/guard failure |FAILED, no accepted output |

|Reset/power loss |Old validity lost; new acquisition starts EMPTY, never trust SRAM residue |

**STRONG INFERENCE:** store metadata and integrity value before an atomic final publish. FAILED must dominate any competing commit, including IRQ observer versus Main copy and host export. Preserve caller interrupt state; no interrupt masking across copies, waits or USB sends. Prior terminal-publication review supplies a method, not proof of this unimplemented state machine. [atomicity-patch-review.md](<../phase45-nor-mutation-closure/atomicity-patch-review.md>).

**PROVEN reusable transport:** the prior fixed evidence protocol already carries23 bytes, eight64-byte pieces, and one whole535-byte completion CRC, with session/index/address/length/frameCRC validation. No new535-byte USB frame or whole-payload stack buffer is needed. Source: [evidence_protocol.py](<../../../builds/phase41-fixed-nor-diagnostic/evidence_protocol.py>) (`REGIONS`, `synthetic_packets`, `Receiver.accept/result/captures`); native routing, asynchronous source ownership and one-shot admission evidence: [findings.md](<../phase42-exact-rdiag-integration/findings.md>). Hardware-tested historical rdiag framing and offline-qualified NOR-command integration remain different scopes; an early-snapshot firmware has not been tested on hardware.

**STRONG INFERENCE:** replace the existing command's per-chunk NOR requests with reads of the immutable retention buffers, retaining checked framing, TX buffer ownership until USB completion, strict one-shot admission and host all-or-nothing acceptance. Host accepts both named files only after the single valid whole535-byte completion, then computes SHA-256 and publishes atomically using the prior publication contract. Do not retain a second fallback source that silently initiates NOR or filesystem access. Packet addresses label the original evidence addresses; a new version/source marker should distinguish boot snapshot from late live read without pretending snapshot time is request time. New exporter/parser/native regressions are still required before adoption.

| Failure | Diagnostic behavior / recovery boundary | Confidence |

|---|---|---|

|81000 read rejects or incomplete |No A validity, FAILED if observer runs; no export, no new diagnostic read |STRONG INFERENCE design; UNKNOWN observer qualification |

|82000 read rejects or incomplete |Same, no BOTH; previous A never accepted alone |STRONG INFERENCE design |

|Retention unavailable/corrupt |Fail closed, no payload; guards/CRC detect only covered corruption, not all memory faults |STRONG INFERENCE design; UNKNOWN address |

|USB never enumerates / host never asks |Keep volatile snapshots if valid; add no Storage work and no cleanup writes |STRONG INFERENCE design |

|Malformed request / interrupted export |Reject/discard; no acquisition or persistent cleanup; preserve one-shot latch/no automatic retry |STRONG INFERENCE design |

|Power cycle before export |Evidence is lost; new boot acquires a new pair, cannot claim old bytes retained |PROVEN volatile-memory consequence |

|Stock read deadlock / failed boot |No **diagnostic** Storage request was submitted; original stock wait/failure remains |PROVEN separation; UNKNOWN complete reboot/recovery safety |

**UNKNOWN:** a successful recovery or preservation guarantee across a power cycle. No persistent diagnostic cleanup is needed, but the stock boot itself may already have issued persistence/installer operations. RAM-only export removes the additional late diagnostic H4 exposure, not original stock-read failure. Host timeout/no-valid-file containment remains required for export failure. No hardware action is authorized by this design.
