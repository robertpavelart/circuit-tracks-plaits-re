> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase52 — all513 target prefix lengths

**PROVEN:** new native coupled runner independently executes T1 complete→C1 complete→T2 n-byte-prefix/completion for every n=0..512 inclusive. Exact same physical buffer is reused within each triple. All513 cases assert native full clear, op1 only, backend release,4096-byte TX and GOOD CSW. Full512 outputs,4096 hashes and all command traces are saved. [experiment.py](<../../../builds/phase52-read-authentication/experiment.py>); [native_sequence.py](<../../../builds/phase52-read-authentication/native_sequence.py>); authentication-experiment.json (local-only reference: `builds/phase52-read-authentication/authentication-experiment.json`; not distributed) `partial_T2_exhaustive`.

| n refreshed into T2 | Full512 comparison + BPB gate | Full4096 comparison + control gate |

|---|---|---|

|0..511 (512 cases)|reject all |reject all |

|512 (one case)|accept |accept for this zero-tailed4096-byte source |

**PROVEN narrow positive result:** in a contiguous forward-prefix model, every accepted T2 refreshed all512 BPB bytes. Offset511 must beAA after a zero clear; reaching that offset requires writing the entire prefix under this model. No stale-control suffix remains, and no target prefix shorter than512 is falsely accepted. This is not merely testing one or two differing signatures: exact full512/4096 equality is evaluated, and the nonzero footer explains the exhaustive boundary.

**PROVEN limit:** atn512 only512 of4096 physical-block bytes were refreshed. Full4096 equality still passes because the expected tail is zero. This does not violate the 'all512 metadata bytes refreshed' condition, but it cannot certify a complete4096-byte physical transfer. Likewise partial controls can match their full sectors. Neither example demonstrates an incorrect BPB.

**UNKNOWN remaining contract:** native lower execution must guarantee that delivered bytes are a contiguous correctly addressed prefix of the current command, and that old DMA/USB activity cannot supply them after clear. The experiment deliberately models this boundary; it cannot prove its own premise.

**PROVEN new native setup check:**1C072 branches at1C112 past address/count programming if DMA EN already1, and still returns0 at1C13C. Two native helper tests show EN0 programs M0AR40024000/NDTR4096; EN1 preserves old M0AR20025000/NDTR123 and returns0. These are modeled register-memory states, not evidence EN remains1 after a real completed read.37430 does not check this setup result or independently compare NDTR after37596. b13-0801c100.asm (local-only reference: `builds/phase52-read-authentication/b13-0801c100.asm`; not distributed); DMA-setup-cases.json (local-only reference: `builds/phase52-read-authentication/DMA-setup-cases.json`; not distributed); b13-08037430.asm (local-only reference: `builds/phase51-msd-read-safety/b13-08037430.asm`; not distributed).

Thus an EN0/current-command/quiescence invariant remains necessary before extending the prefix-model proof to real B1.3. No completion bit or malformed peripheral state is assumed to occur physically. No unsafe retry follows a modeled timeout.
