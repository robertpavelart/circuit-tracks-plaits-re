> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase50 — mode entry is not a filesystem read

**PROVEN startup route:**29DDC constructs a setting observer,29E30 reads setting record2 bit17 and calls38C54 with packed101hex (MIDI+MSD1) or1 (MIDI only). Initialized mode1 is not proof the user's active setting enables MSD. Bit17 is called 'probably Easy Start' in reference notes, not conclusively named by code. b13-08029ddc.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-08029ddc.asm`; not distributed); NOTAS.md (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/docs/NOTAS.md`; not distributed) lines86,1014.

**PROVEN UI code:** Setup object advanced flag+24 !=0, method47016, button ID9→47070 toggles setting record2 bit17 then commits353C0 via470C8/470EA. Other advanced IDs15/24 are different functions; B1.3's patched button24 branch must not be conflated with button9. **UNKNOWN:** fully authenticated physical-button label and gesture entering this advanced view from the current unit. No user action is prescribed. This UI toggle is not a read-only acquisition step: the registered changed-settings subscriber2D278→2D300→2D2AC can request128-byte settings write3C920 and flush. b13-08047016.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-08047016.asm`; not distributed); b13-0804709a.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-0804709a.asm`; not distributed); app-08035398.asm (local-only reference: `builds/phase46-msd-filesystem-closure/app-08035398.asm`; not distributed); [persistence-routes.md](<../phase46-msd-filesystem-closure/persistence-routes.md>).

**PROVEN existing transient control route:** vendor prefix checked by248F0, command byte5=42hex, subcommand byte6=0, requested mode byte7.24918/2492E calls38C10 and248CE schedules248B5 after150 timer ticks (not asserted milliseconds). Timer callback248B4 builds config with MIDI byte1 and stored mode, then38C54 rebuilds classes. This is stock code present in B1.3, not rdiag or firmware installation. No packet/transmitter is generated and none is sent. b13-080248b4.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-080248b4.asm`; not distributed).

| Requested mode / config MSD byte | Immediate internal selection | After deferred callback | Final base |

|---|---|---|---|

|0|0 (disabled)|0, MIDI only|old pointer irrelevant |

|1|1|1, MIDI+MSD|94000 |

|2|2 (D4000)|3, MIDI+MSD|0 |

|3|3 (0)|2, MIDI+MSD|D4000 |

**PROVEN:**38C54 maps config2→internal3 and config3→internal2. These numbers cannot be interchanged in read-address calculations. Mode1 is stable under this remap and is the only mode in the decoder/conditional plan. START STOP/eject can schedule the same reapplication; exclude eject from a stable acquisition interval. b13-08038c10.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-08038c10.asm`; not distributed); native-reads.json (local-only reference: `builds/phase50-msd-readonly-geometry/native-reads.json`; not distributed); [msd-reachability.md](<../phase46-msd-filesystem-closure/msd-reachability.md>).

**PROVEN native slice:** real vendor248F0 parser→setter→timer scheduling, then real248B4 callback→38C54→class clear/register/descriptor build were executed for modes0..3. Low-level USB driver reset/config/start/endpoint-close calls are seams; no Storage/persistence calls observed. Mode1 registers200000EC MIDI and200000F8 MSD together, so they are not mutually exclusive. Mode change reconfigures USB; no MCU reboot is requested. [native_reads.py](<../../../builds/phase50-msd-readonly-geometry/native_reads.py>); b13-08036374.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-08036374.asm`; not distributed); b13-08036460.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-08036460.asm`; not distributed).

**PROVEN in inspected bodies:** no mount19A92/unmount1AE1C, settings save, FS flush or NOR write is directly called by transient42/38C54. **UNKNOWN:** complete upstream dispatcher and USB-driver callback closure and pre-existing background/queued work during the transition. The model does not prove the entire live mode-entry session has no persistence. This is the remaining mode-entry gate; an untested driver seam is not a hardware-tested no-write result.
