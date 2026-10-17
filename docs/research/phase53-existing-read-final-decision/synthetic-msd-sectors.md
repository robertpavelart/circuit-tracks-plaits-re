> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase53 — mode1 LBAs00..3F are NOR-backed

**PROVEN:** every one of the64 LBAs00..3F takes57E88's same valid-block branch, clears its response, and invokes raw NOR wrapper24130. There is no branch by LBA within this range selecting a virtual sector, flash template, RAM image, synthesizedMBR, or fixed zero response. Native isolated callback tests record every physical start/end and one4096-byte wrapper read per LBA. producer-cases.json (local-only reference: `builds/phase53-existing-read-final-decision/producer-cases.json`; not distributed) `mode1_LBAs_00_3F`; b13-08057e30.asm (local-only reference: `builds/phase53-existing-read-final-decision/b13-08057e30.asm`; not distributed).

For each LBA L in00..3F: `physical_start=94000+1000*L`, end=start+FFF. Thus00→94000..94FFF,01→95000..95FFF,...,3F→D3000..D3FFF. The JSON contains all64 individual rows, not only an inferred total. The range exactly covers the selected window's nominal94000..D3FFF backing. LBA40 beginsD4000, the separately mounted filesystem region. b13-08038c10.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-08038c10.asm`; not distributed).

**PROVEN classification for all64:** external serial NOR-backed; not SD, not DSP SDRAM, not RAM-backed or firmware-generated sectors. A preformatted or help/MBR-looking image could reside in that NOR region, but **UNKNOWN** actual current-unit contents. A sector containing zeroes still depends on a physical NOR read. Zeroes after a failed read are the caller's clear, not a qualified synthetic-sector command. The conditional serial-text substitution does not change that dependency.

**PROVEN:** capacity57E34 remains8192×4096 regardless of the nominal selected-window end, so a capacity response is not evidence of a512-byte synthetic façade or a generated filesystem. Every tested low LBA uses the physical path. No expected512-byte payload can be provided for those addresses without acquiring their NOR contents, which Phase53 does not do.

Tests inject no source bytes and stop at the raw wrapper seam; they prove routing, not physical sector values. No TARGET/CONTROL sequence from Phase52 was repeated. [producer_cases.py](<../../../builds/phase53-existing-read-final-decision/producer_cases.py>) `low_lba`.
