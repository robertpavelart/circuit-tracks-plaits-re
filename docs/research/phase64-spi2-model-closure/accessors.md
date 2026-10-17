> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Authenticated startup SPI2 accessors

Candidate BIN SHA-256 `edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9`. **PROVEN** observed accesses, not global whole-program or post-frontier completeness.

| Instruction | Access | Register | Observed values | Count |

|---|---|---|---|---:|

|`0x8048166`|R|CR1 `0x40003800`|`0`|1|

|`0x804816e`|R|CR1 `0x40003800`|`0`|1|

|`0x8048196`|W|CR1 `0x40003800`|`314`|1|

|`0x8048198`|R|CR2 `0x40003804`|`0`|1|

|`0x80481a6`|W|CR2 `0x40003804`|`700`|1|

|`0x80481b6`|R|I2SCFGR `0x4000381c`|`0`|1|

|`0x80481bc`|W|I2SCFGR `0x4000381c`|`0`|1|

|`0x80378d4`|R|CR2 `0x40003804`|`700`|1|

|`0x80378da`|W|CR2 `0x40003804`|`1700`|1|

|`0x80378e6`|R|CR2 `0x40003804`|`1700`|1|

|`0x80378ec`|W|CR2 `0x40003804`|`1701`|1|

|`0x80378f8`|R|CR2 `0x40003804`|`1701`|1|

|`0x80378fe`|W|CR2 `0x40003804`|`1703`|1|

|`0x8037940`|R|CR1 `0x40003800`|`314`|1|

|`0x8037946`|W|CR1 `0x40003800`|`354`|1|

|`0x80379a4`|R|CR1 `0x40003800`|`354`, `365`|2|

|`0x80379ac`|W|CR1 `0x40003800`|`364`, `345`|2|

|`0x80379b8`|R|CR1 `0x40003800`|`364`, `345`|2|

|`0x80379be`|W|CR1 `0x40003800`|`324`, `305`|2|

|`0x80379c6`|R|CR1 `0x40003800`|`324`, `305`|2|

|`0x80379cc`|W|CR1 `0x40003800`|`325`, `305`|2|

|`0x80379f2`|R|CR1 `0x40003800`|`325`|1|

|`0x80379f8`|W|CR1 `0x40003800`|`325`|1|

|`0x80379fe`|R|CR1 `0x40003800`|`325`, `307`|2|

|`0x8037a04`|W|CR1 `0x40003800`|`365`, `347`|2|

|`0x80379e4`|R|CR1 `0x40003800`|`305`|1|

|`0x80379ea`|W|CR1 `0x40003800`|`307`|1|

|`0x8037970`|R|SR `0x40003808`|`2`, `882`|9024|

|`0x803797c`|W|DR `0x4000380c`|`0`, `C`, `7F`, `FF`, `40`, `2A`, `AA`, `20`, `19`, `99`, `15`, `55`, `12`, `49`, `24`, `10`|9024|

|`0x8037986`|R|SR `0x40003808`|`882`, `A83`, `203`|15039|

|`0x803798c`|R|DR `0x4000380c`|`0`, `1`, `80`, `8`, `2`, `9`, `44`, `3`, `A`, `88`, `4`, `B`, `CC`, `5`|9023|

**PROVEN branch semantics:**37970 reads SR,37972 shifts bit1 to sign,37974 BPL skips transmit when TXE=0;3797C STRB enqueues DR.37986 reads SR,37988 shifts bit0 to sign,3798A BPL retries when RXNE=0;3798C LDRB consumes DR.37994/37998 compare byte counters with requested length; only all bytes sent and received permit3799C/3799E return.

CR1 mode/SPE and CR2 DS/FRXTH/DMA configuration are executed at48164 and37858/379A0/379B0. I2SCFGR is read/written by481B6/481BC to keep SPI mode. DMA programming and IRQ helpers are listed separately; modeled DMA transactions are not miscounted as CPU DR instructions.

Relevant authenticated listings: candidate-08037770.asm, candidate-08037960.asm, candidate-08048164.asm, candidate-080291b8.asm, candidate-0803b9d8.asm, candidate-08057532.asm. accessor-audit.json records direct BL/literal candidates. Empty short contexts caused by starting disassembly inside a32-bit instruction are not independently authenticated boundaries; use complete function listings.

**UNKNOWN:** accessors reachable only after the deferred DSP task frontier have not executed. The table is complete for instrumented block accesses in this prefix, not a claim that the rest of normal boot has no other accessors.
