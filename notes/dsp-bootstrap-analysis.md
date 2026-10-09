# Phase 19B-HANDOFF — original bootstrap

2026-10-06. **VERIFIED static analysis only. Bootstrap/main/worker execution: 0
instructions.** No image modification, hardware, transmissions or Plaits.

The ARM sends a **30-byte SHI boot record**, not 30 executable bytes. Original
record SHA256 `299c99e05eca2ba35dc44904dcf754c2026e4a73caa069f300562e82f0776e97`;
its 24-byte payload SHA256
`216c68a557b0e4a124d115fadf65835eecfd6c206d1184ab44400fec0865e945`.
BIN offset196E0, runtime ARM address080296E0. Header words are count8 and load0.
The eight payload words load P[0,8); there are seven instructions because the
last JMP has an extension word. The two header words are not executable P words.

| P address | Word(s) | Instruction | Explicit effect |
|---|---|---|---|
|0|0444BA|MOVEC OMR,X0|X0=OMR incoming|
|1|0AC467|BSET #7,X0|C=oldX0.bit7; X0.bit7=1|
|2|0AC476|BSET #22,X0|C=oldX0.bit22; X0.bit22=1|
|3|0AC455|BCLR #21,X0|C=oldX0.bit21; X0.bit21=0|
|4|04C4BA|MOVEC X0,OMR|Write modified OMR|
|5|000000|NOP|No explicit state definition|
|6–7|0AF080 FFFFFE|JMP FFFFFE|Transfer to documented device ROM reset entry|

**VERIFIED instruction effects:** `OMR_out=(OMR_in | 0x400080) & ~0x200000`;
X0 holds the same value. Final C equals incoming OMR bit21. Other SR bits are
not explicitly changed by this bootstrap. Therefore it does **not** clear LF,
set an entire known SR, restore reset masks, or initialize GPIO/ICC.
Bit-operation carry semantics are corroborated by the pinned interpreter and
the [DSP56300 instruction manual](https://www.nxp.com/docs/en/reference-manual/DSP56300FM.pdf).

No explicit bootstrap accesses to SP/SC, SSH/SSL, R/N/M registers, LA/LC,
accumulators, GPIO, SHI, ICC or shared RAM occur. This is a statement about this
decoded body, conditional on straight-line execution without inherited loop or
interrupt diversion; it is not a statement about the preceding/following ROM.
Changing OMR does change chip memory configuration. The candidate profile maps
bits7/22/21 to MS/MSW1/MSW0; exact physical part remains unresolved.

**VERIFIED ARM call order:** bootstrap08029284 → main08029294 → worker080292A6.
Calls0802928A/0802929A introduce delay between uploads. The reset/control helper
08023438 sets GPIO objects and performs a low/high control transition with
two100-unit waits. It does not write DSP CPU registers. Named physical reset
wiring and mode-pin levels remain conditional; numeric delays are not assumed
to be measured chip boot times.

**DOCUMENTED candidate boot operation:** reset enters PFFFFFE; mode0 uses SHI
SPI slave24 and consumes count/load/payload. ROM transfers to the record's load
address. First record enters bootstrapP0; bootstrap explicitly returns to ROM;
second record replaces the same low P memory with the main program and enters
mainP0. Its JMP100 performs the final transfer to startup. The ARM supplies
bytes; it does not send a separate command to set PC100.
[DSP56724RM tables5-3/5-5](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf#page=102).

**UNRESOLVED:** full ROM exit state on either pass, survival of pre-ROM OMR
values, authentic ROM revision/source, and hardware mode straps. It would be
incorrect to execute the bootstrap with constructor defaults and call the
result a reconstructed stock handoff. No bootstrap was executed in this phase.

Reproducible byte-checked evidence: `builds/phase19b-handoff/final/bootstrap.asm`,
`bootstrap-analysis.json`, `arm-ordering.json`; tool `tools/ct_handoff_contract.py`.

## Phase19B-ROM comparison — 2026-10-06

The shim remains the only recovered executable bootstrap body, not an authentic
ROM loader. Official56720/21 and56724/25 manuals share the reviewed SHI mapping
and boot contract but have different memory capacities. Candidate56724/core0
defaultP1000 cannot hold the main2A5E-word image; configuredmode110P4000 can.
This supports the OMRmode setter/ROMreentry role, without proving post-ROM mode
preservation. No ROMexit opcodes can be shown side-by-side while source is missing.
The shim is sent only tochannel0; worker cannot inherit its OMRwrites by assumption.
No shim/main/worker execution occurred.
