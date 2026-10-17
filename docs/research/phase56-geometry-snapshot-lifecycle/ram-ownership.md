> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase56 — RAM ownership search

**PROVEN:** the new candidate census covers every halfword of the375948-byte exact corrected research application, every byte of initialized RAM for pointer candidates, and the authenticated captured RAM for pointers/names. It records37 direct candidates,18 literal candidates,14 consecutive MOVW/MOVT address constructions and32 pointer candidates. False positives/data decodes/stale captured words are labeled; this is not a complete computed-alias theorem. [census.py](<../../../builds/phase56-geometry-snapshot-lifecycle/census.py>), census.json (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/census.json`; not distributed).

|Address inclusive |Owner, initialization and known accessors |Lifetime / conclusion |

|---|---|---|

|20044D70..20044D7B |Phase42/44 private12-byte diagnostic record. Getter5DBCC→6B6CC reserves downward by changing[20002B44], writes magic at6B714 and zeros+4/+8 at6B708/70A. SysTick watch6B748, entry6B798, raw command6B850 and terminal patch6BC30 read/write it. |PROVEN owner and runtime reservation method; no unused byte. Selected for proposed union redesign, **not qualified for new content**. |

|20044D70..73 |Legacy magic4E4F5234, checked by getter/watch |PROVEN cannot simply substitute generation here while old readers remain. |

|20044D74..77 |Legacy state/session/chunk/owner bytes |PROVEN actively used; not padding. |

|20044D78..7B |Legacy start tick |PROVEN timeout uses full word; not spare until old lifecycle is replaced. |

|20044D7C..20044E57 |220-byte SC35D8 Master FX state, getter/init5DC06 and retained feature service |PROVEN live owner; no additional reservation or audio state borrowing. |

|20044DF4..20044E37 |Historical rdiag68-byte log atMasterFX+120 |PROVEN aliases live Master-FX LEDs; initialization/repaint can overwrite. Not a distinct diagnostic allocation. |

|20044DE4..20044E1B |probe35s14-word report atMasterFX+104 |PROVEN same live LED owner; not long-lived snapshot storage. |

|20044D68..20044D6F |Fixture heap headroom before existing limitD70 |PROVEN only8 bytes in that fixture; forbidden heap-tail strategy, not selected. |

|20044D3C..20044D6F |Proposed Phase55 extra52 reservation |PROVEN overlaps fixture demand by44; explicitly rejected and unused. |

|20002B44..20002B4B |Allocator limit/cursor |PROVEN live metadata, no unused fields. |

|20000AB5;20000ABE..ABF |FS padding candidates |UNKNOWN full semantic padding ownership; at most3 apparent bytes, inside excluded filesystem owner, insufficient and not used. |

|20005148..20005347 |DSP table staging/DMA-read destination |PROVEN reused by native table jobs; excluded. |

|20006868..2000687E |Identity cache, normalization/edit path |PROVEN live native state; excluded. |

|2000775C..20008357;20008D44..2000923F |Main/Storage stacks |PROVEN excluded; IRQ stack region also excluded. |

|Parser buffers;40024000..40024FFF |SysEx and MSD/DMA temporary ownership |PROVEN excluded; no retention claim. |

|Other initialized/BSS/zero gaps, split records |No complete owner/alias exclusion identified by census |UNKNOWN, not safe merely because fixture-zero or not directly addressed. |

Sources: [findings.md](<../phase42-exact-rdiag-integration/findings.md>), [heap-stack-status.md](<../phase45-nor-mutation-closure/heap-stack-status.md>), rdiag.py (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/rdiag.py`; not distributed), probe35s.py (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/probe35s.py`; not distributed), app-0806b6cc.asm (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/app-0806b6cc.asm`; not distributed), app-0806b850.asm (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/app-0806b850.asm`; not distributed), app-0806bc30.asm (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/app-0806bc30.asm`; not distributed).

**STRONG INFERENCE — proposed12-byte union:** control32 atD70 contains phase3 bits, sticky unqualified-history bit,28-bit generation;8 bytesD74..D7B contain canonical geometry until raw admission. After geometry export and atomic authorization, the payload can become raw-only bookkeeping: target mask, session, chunk, owner and32-bit start tick. Geometry may be released at this transition because it is no longer independently mutable/re-exportable; every needed raw ownership/timeout field remains representable. Terminal state rejects another raw capture.

**UNKNOWN:** re-laying out the record requires replacing all old getter/watch/admission/raw/terminal access contracts and reserving it before mount. Existing lazy initialization is too late if it clears a snapshot. Reusing the existing12-byte capacity creates0 additional heap demand, but does not prove early reservation timing or whole-boot demand. No new layout is installed, no52-byte reservation is attempted, and no location is declared qualified.

**UNKNOWN:** the requested complete RAM ownership proof across all indirect runtime writes has not been achieved. The scan is comprehensive in input coverage; unresolved computed aliases, boot initialization and new union compatibility remain explicit blockers rather than being hidden behind the scan counts.
