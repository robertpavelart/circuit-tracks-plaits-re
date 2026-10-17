> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Circuit Tracks build 4486 — static firmware map

Phase-3 follow-up: see `dsp-memory-map.md` and `dsp-command-map.md` for validated
DSP decoding, SHI handlers, runtime protocol, partial DSP memory reconstruction
and selection logic. The architecture conclusion below records phase-2 evidence;
phase 3 adds stronger DSP audio/synthesis evidence with explicit remaining limits.

Status: 2026-10-05, static analysis only. Function names below are analyst labels.
**VERIFIED** means supported by local bytes, reviewed instructions or an explicit
reference mapping; it does not mean observed on hardware. **HYPOTHESIS** and
**UNRESOLVED** identify deductions still needing evidence.

## Image and vectors

**VERIFIED:** BIN occupies `[0x08010000, 0x0805CDDC)`, length 314844 / 0x4CDDC.
SHA256: `b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da`.
Little-endian vector words and Thumb code are internally consistent.

The table has 114 entries (16 core + 98 external), ending at file offset 0x1C8;
this matches the STM32F745 interrupt layout. All 105 nonzero handler entries are
odd and resolve inside the image. Core reserved zeros are indices 7–10 and 13;
external reserved zeros are indices 95, 104 and 105. There are 76 external
four-byte self-branch defaults and 19 other external handlers. Exact MCU model,
package and silicon revision remain **UNRESOLVED**.

| Core entry | Code address |
|---|---|
| Initial MSP (value, not code) | 0x20050000 |
| Reset | 0x0805C00C |
| NMI | 0x0805995E |
| HardFault | 0x08059960 |
| MemManage | 0x08059962 |
| BusFault | 0x08059964 |
| UsageFault | 0x08059978 |
| SVCall | 0x0801D9B0 |
| DebugMonitor | 0x0805998A |
| PendSV | 0x0801D954 |
| SysTick | 0x0805998C |

The reset veneer loads `0x0801BC79` from 0x0805C014 and calls it, then loads
`0x0805C19D` from 0x0805C018 and branches to it. At 0x0805C19C the runtime calls
0x0805B790 (FPU setup) and 0x0805B990. The latter reaches 0x0805B590 (data setup)
and 0x0801D3C8 (application initialization). This is a partial startup graph;
names such as SystemInit/main are not recovered symbols.

### Non-default external handlers

Addresses and bodies are **VERIFIED**. IRQ names below are the documented
STM32F745 mapping, conditional on that MCU identification, rather than proof
of the physical chip. Full entries and classifications are in `builds/repro/evidence.json`.

| IRQ | Conditional name | Code address |
|---:|---|---|
| 14 | DMA1_Stream3 | 0x08057532 |
| 15 | DMA1_Stream4 | 0x08057508 |
| 18 | ADC | 0x080574D6 |
| 24 | TIM1_BRK_TIM9 | 0x080575A0 |
| 28 | TIM2 | 0x0805744A |
| 30 | TIM4 | 0x080574B4 |
| 37 | USART1 | 0x080574FC |
| 38 | USART2 | 0x08057502 |
| 40 | EXTI15_10 | 0x080573D8 |
| 41 | RTC_Alarm | 0x080573DC |
| 49 | SDMMC1 | 0x08057562 |
| 50 | TIM5 | 0x08057498 |
| 56 | DMA2_Stream0 | 0x080574E8 |
| 59 | DMA2_Stream3 | 0x08057430 |
| 60 | DMA2_Stream4 | 0x0805740E |
| 69 | DMA2_Stream6 | 0x08057578 |
| 70 | DMA2_Stream7 | 0x080573EE |
| 77 | OTG_HS | 0x080574D0 |
| 92 | QUADSPI | 0x080573E0 |

DMA1 stream handlers use DMA1 status/clear registers and pass the object at
0x2000016C to 0x08037852 (receive completion) and 0x0803784E (transmit completion).
The SPI2 vector itself points to a self-loop default at 0x0805C30C; transfer
completion is serviced through DMA handlers, not that SPI interrupt.

## Strings

**VERIFIED:** these bytes occur at the following offsets and image addresses.
The regex survey lists 3298 printable runs; many are incidental code/data.

| Offset | Address | String / qualification |
|---|---|---|
| 0x1CE | 0x080101CE | `GB1.1.5143.4486` |
| 0xD790 | 0x0801D790 | second `GB1.1.5143.4486` |
| 0xF5F0 | 0x0801F5F0 | `>> DSP Uploading...`, then LF and NUL |
| 0xF608 | 0x0801F608 | `<< DSP Uploaded`, then LF and NUL |
| 0x15A54 | 0x08025A54 | `Circuit Tracks` |
| 0x4B6C0 | 0x0805B6C0 | run containing `NovationCircuit` and `Sample Memory Exceeded 0x%X + 0x%X` |
| 0x4C058 | 0x0805C058 | `_PCM.wav` |
| 0x4C064 | 0x0805C064 | `_META.ncm` |
| 0x4C070 | 0x0805C070 | `_GRIDFX.ncg` |

The first version string is preceded by printable metadata byte 0x64 at 0x1CD,
so a naive ASCII-run scanner reports `dGB...` starting one byte earlier. The
version string's actual supplied start is independently verified at 0x1CE.

## DSP upload graph

**VERIFIED:** neither DSP string address exists as a raw 32-bit pointer.
The wrapper at 0x0801F554 constructs them using ADR:

- 0x0801F560: ADR r0 -> 0x0801F5F0; call 0x0801B3B8 at 0x0801F562.
- 0x0801F566: r0 = 0; call upload selector 0x08029260 at 0x0801F568.
- 0x0801F56C: ADR r0 -> 0x0801F608; call 0x0801B3B8 at 0x0801F56E.
- It then calls 0x08029710, 0x0802108C and 0x080297A8 before configuring callbacks.

`0x0801B3B8` is labelled diagnostic output based on its call-site arguments;
the ultimate logging destination is **UNRESOLVED**.

```text
0x0801D4B0 application path
  0x0801D582 -> 0x0801F51E mode dispatcher (zeroed mode argument)
    mode 0: 0x0801F536 -> 0x0801F554 upload wrapper
      0x0801F568 -> 0x08029260 upload selector (selection 0)
    mode 1: 0x0801F544 -> 0x08029260 (selection 1)

0x08029260
  -> 0x0803BADA transport mode setter
  -> 0x08023438 reset/control sequencing, with two 100-unit delays
  -> 0x08029200 bootstrap at 0x080296E0, channel 0
  -> 0x08029200 table[selection], channel 0
  -> 0x08029200 table[selection+2], channel 1
  -> 0x0803BAD6 transport mode setter
  -> poll channel-0 third GPIO until zero (0x080292B4–0x080292BE)
  -> selection 0 tail-calls 0x08029492 post-upload tables
```

Selection is not bounds-checked inside the uploader; the two reviewed caller
paths pass 0 or 1. Unknown indirect callers remain possible.

| Address | Analyst label | Verified behavior |
|---|---|---|
| 0x08029200 | send_boot_stream | derives total count from header; sends source bytes in chunks |
| 0x080291B8 / 0x080291CA | channel_select_low/high | drives first channel GPIO low/high |
| 0x0803BA96 | bulk_send | forwards source and byte count to 0x080377DE |
| 0x080377DE | spi_dma_send | starts RX DMA into discard byte and TX DMA from source |
| 0x0801C072 | dma_transfer_start | writes memory address/count, controls increment, enables stream |
| 0x0803B9D8 / 0x08023414 | wait_transfer | waits on receive-completion flag |
| 0x0803BAA2 | transfer_24bit | packs three bytes; calls polling SPI transfer at 0x08037960 |
| 0x08037960 | spi_poll_transfer | polls SR bits 1/0, writes/reads byte DR at peripheral +0xC |
| 0x080292F8 | write_dsp_register | maintains register-address cache and sends 24-bit values |
| 0x08029344 | read_dsp_register | transmits command bytes and returns received 24-bit value |
| 0x08029492 | post_upload_tables | calls 0x08029382, 0x080293BC, 0x080293F0, 0x08029434 |

The post-upload routines generate/send numeric tables: 0x080293BC sends 512
values starting at register 0x2000; 0x080293F0 sends 512 at 0x2200;
0x08029434 sends 832 values from flash 0x08052BB4 at register 0x1600.
Their synthesis meaning is **UNRESOLVED**. Register labels are inferred from
the common address/data transfer behavior, not a recovered DSP memory map.

## SPI2 interface and initialized-data evidence

**VERIFIED by static reconstruction:** startup routine 0x080596C4 decodes the
data record at 0x0805B7C8. Its source is 0x0805C3C4, compressed length 2582
bytes, destination 0x20000000. Python translation consumes all 2582 bytes and
produces 15618 bytes, ending at 0x20003D02. Two bytes before the next zero-init
region at 0x20003D04 are not synthesized. Reconstructed-data SHA256:
`2db584abde65123402067c89720f5a10e12c40650b700d6af2f13ed93743e04f`.
This is a derived offline data view, not a captured RAM dump.

The upload transport follows this pointer chain in that data:

```text
state 0x20000314 + 0xC -> transport 0x2000016C
transport + 4 -> SPI object 0x20000264
SPI object -> config 0x20003414 -> peripheral 0x40003800 (SPI2)
transport + 0xC -> RX object 0x2000024C -> config 0x200031F4
  -> DMA stream 0x40026058 (DMA1 stream 3), peripheral 0x4000380C (SPI2 DR)
transport + 0x10 -> TX object 0x20000250 -> config 0x20003238
  -> DMA stream 0x40026070 (DMA1 stream 4), peripheral 0x4000380C (SPI2 DR)
```

Channel 0's GPIO group is 0x200002F4: PD9 select, PD0 auxiliary output,
PD7 polled input. Channel 1's group is 0x20000300: PD8 select, PD1 auxiliary
output, PD4 input. GPIO configuration base is 0x40020C00 with corresponding
pin masks. The first GPIO is toggled around transfer; the third is read for
readiness. Mapping these channels to DSP cores/SHI instances and identifying
physical pin wiring are **HYPOTHESES**, not established by the ARM tables alone.

## Extracted DSP upload streams

**VERIFIED:** uploader pointer table at 0x08029700 contains, in order:
0x080101F0, 0x08054EFC, 0x08018110, 0x0805587C.
The bootstrap comes from a separate PC-relative address at 0x080296E0.

| Block | File offset | Image address | Word count | Stream bytes | Exclusive end |
|---|---|---|---:|---:|---|
| bootstrap | 0x196E0 | 0x080296E0 | 8 | 30 | 0x080296FE |
| selection0-channel0 | 0x1F0 | 0x080101F0 | 10846 | 32544 | 0x08018110 |
| selection0-channel1 | 0x8110 | 0x08018110 | 364 | 1098 | 0x0801855A |
| selection1-channel0 | 0x44EFC | 0x08054EFC | 808 | 2430 | 0x0805587A |
| selection1-channel1 | 0x4587C | 0x0805587C | 360 | 1086 | 0x08055CBA |

Each stream starts with a big-endian 24-bit word count and a big-endian 24-bit
load address, then exactly that many 24-bit words. All load addresses are zero.
The ARM sender reads count bytes at offsets 1/2, adds two header words and
sends `(count+2)*3` bytes directly from flash. Chunks are at most 170 words /
510 bytes. Transfer completion is awaited between chunks and before deasserting
the selector. There is no ARM-side decompression of these streams.

Header-inclusive streams, payload-only files, word listings and all SHA256
hashes are in `firmware/dsp/build-4486/manifest.json`. This extraction excludes
alignment padding and preserves both headers in `.boot24.bin` files. Internal
DSP loading, code/data boundaries, and subsequent self-modification are not
analyzed yet; these files are not claimed to be complete DSP memory images.

## Architecture conclusion and next step

**VERIFIED:** the ARM image contains an explicit DSP-labelled boot path that
uploads multiple 24-bit streams over SPI2 and sends additional tables afterward.
**HYPOTHESIS:** two channels correspond to the two DSP56724-family cores; the
larger normal-selection payload contains synthesis processing.
**UNRESOLVED:** exact DSP silicon, Nova synth ownership, voice algorithms,
audio routing and whether Plaits can replace/augment any engine. UI/sequencer
versus audio responsibility is not proven or disproven by the upload alone.

The single best next step is to statically disassemble the normal-selection
channel-0 payload as DSP56300-family 24-bit code at program word address zero,
validate its entry/interrupt vectors, and trace its host-command dispatch toward
voice/sample processing. This directly tests the synth-on-DSP hypothesis.

## Evidence and references

Reproduce with `tools/run_recon.ps1` into a fresh directory; details in
`tools/README.md`. Canonical reviewed outputs are `builds/repro/`; the older
top-level `builds/*.txt` are exploratory sweeps and may contain data decoded as
instructions. In particular, `builds/data-decoder.txt` is a rejected candidate,
not the startup decompressor.

- [ST STM32F745 CMSIS header](https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-f7/master/Include/stm32f745xx.h): IRQ numbers, peripheral/register addresses.
- [ST RM0385](https://www.st.com/resource/en/reference_manual/dm00124865-stm32f75xxx-andstm32f74xxx-advanced-armbased-32bit-mcus-stmicroelectronics.pdf): reference manual for STM32F74xx/F75xx.
- [NXP DSP56724 reference manual, Table 5-5, printed page 5-7](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf#page=103): SHI SPI boot expects count, load address, program words; correspondence supports family identification but does not prove board silicon.
