> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase55 — smallest defensible hook design

**STRONG INFERENCE:** replace the4-byte BL at**0801AE02** with a BL to a wrapper. Execute the original19A92 call exactly once with unchanged arguments and ownership. After its return, before native1AE06 MOVS/ITEE, perform only the geometry copy/validity work if this is the first NOR startup mount. Continue at1AE06 with original registers/flags/SP/control flow. This relocates the existing mount call; it adds no mount or other filesystem operation. Acquisition work after successful return has no calls to Storage, NOR, SD, filesystem or allocator. app-0801addc.asm (local-only reference: `builds/phase55-precleanup-geometry-snapshot/app-0801addc.asm`; not distributed), app-0801f0a8.asm (local-only reference: `builds/phase55-precleanup-geometry-snapshot/app-0801f0a8.asm`; not distributed).

**PROVEN:** replacing1AE06 MOVS plus1AE08 ITEE as a naive four-byte hook would displace the beginning of an IT block. Returning by a branch from a replayed ITEE would consume a conditional instruction slot incorrectly. The call-site wrapper avoids that hazard. The common mount epilogue19A4C also includes failure/fast-return paths and is not an unconditional success site. No bytes are patched in this phase.

**STRONG INFERENCE — required sequence:** initial volatile EMPTY; invoke original mount; reject nonzeroR0, wrong disk/FS pointer/drive/binding or unexpected lifecycle; copy A98:8,AB0:14,AD0:24 to owned retention; publish GEOMETRY_VALID last. Error gives terminal FAILED for that boot. No acquisition retry through later lazy mounts. Distinct reset initialization and remount/backing-change invalidators are needed for same-boot lifetime claims. Subsequent SD mount is ignored; it cannot overwrite the NOR snapshot.

|Impact |Estimate / limit |

|---|---|

|Call-site replacement |PROVEN4 ARM bytes at1AE02 |

|Added ARM code |UNKNOWN exact wrapper/copy/validation/invalidation/export bytes and safe flash pool; no fragment assembled |

|Fixed RAM |PROVEN46 payload, minimum47 with one-byte validity; aligned simple record52; extra epoch/version/CRC increases this |

|Stack |UNKNOWN actual delta until wrapper ABI is emitted; preserve LR, caller-visible scratch registers and flags, maintain8-byte call alignment. No payload stack buffer required. Do not claim zero. |

|Cycles |UNKNOWN exact modeled cycles. A simple6-instruction byte-copy loop entails276 payload-loop instructions for46 bytes, plus setup, checks and save/restore; this is an illustrative instruction calculation, not measured DSP/ARM cycles. |

|Interrupt masking |STRONG INFERENCE no mask over copy/storage/mount; publish last. Any brief epoch/state atomic update must preserve caller PRIMASK and be separately bounded. |

|Storage/NOR/SD operations added |PROVEN0 by the proposed call graph; not an implementation replay result |

**PROVEN:** the eight native tests preserve supported callee registers in the unmodified mount paths. **UNKNOWN:** before/after register/flag equivalence, retention canaries and timing of a future patched hook. This architecture-only phase does not claim those tests already cover emitted hook code. mount-cases.json (local-only reference: `builds/phase55-precleanup-geometry-snapshot/mount-cases.json`; not distributed), [audit.py](<../../../builds/phase55-precleanup-geometry-snapshot/audit.py>).
