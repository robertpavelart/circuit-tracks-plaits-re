> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# SPI2's role in this startup

**PROVEN functional role:** this path is the external DSP host/boot/control link. It is not the raw NOR/QSPI, SD or display peripheral. ARM29260→29200 loads the two DSP bootstrap blocks selected by table08029700;3BA96→377DE uses SPI2 DMA1 RX3/TX4;3BAA2→37960 performs24-bit polled word exchanges. Register pointer chain20000264→20003414→40003800 is observed in native startup. ARM29344 sends read-address command then400000 to clock the pipelined DSP word back.

**PROVEN:** extracted **unchanged** candidate core0 image has13072 words, SHA896b2bc39c4273795e812374ab265fa88efb982bae884273dca2c5531e033495; core1 has364 words. The actual receiving program contains the corresponding DSP SHI protocol and readiness producer P2601→Y2B. This association uses both sides of the code, not the SPI instance name. See peer-ready-static.json (local-only reference: `builds/phase64-spi2-model-closure/peer-ready-static.json`; not distributed), candidate-080291b8.asm, candidate-0803b9d8.asm and loaded-core0.asm. Existing [DSP command map](<../../../notes/dsp-command-map.md>) records the matching HRX/HTX and GPIO-qualified protocol.

**PROVEN:** SPI2 and DSP-host routines inspected here equal clean SC35D8 byte-for-byte (identity-preservation.json (local-only reference: `builds/phase64-spi2-model-closure/identity-preservation.json`; not distributed)). Do not assume later B1.3 background features exist in this diagnostic. SPI2 can carry DSP resources that were first read through the separate NOR path; that does not make SPI2 a NOR reader. Display SPI4 and external NOR QUADSPI are separate retained paths.

**UNKNOWN:** exact physical board-net/pin attribution is not established by this code-only audit. No device was inspected or used. The functional DSP endpoint is established independently of that wiring detail.
