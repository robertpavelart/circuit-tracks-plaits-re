> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase51 — separate entry, read and exit

**PROVEN:** existing transient entry is normal application SysEx dispatcher0801EB30→248F0 (vendor command byte5=42hex,subcommand byte6=0,mode byte7=1)→24918→38C10→248CE (150 timer ticks)→248B4→38C54. No rdiag or new firmware is involved. **STRONG INFERENCE:** ordinary incoming SysEx/Main application callback context, not QSPI IRQ; the timer callback runs through the application timer service. **UNKNOWN:** fully reconstructed RTOS scheduling/current-task state on the real unit. b13-080248b4.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-080248b4.asm`; not distributed); b13-0801eb30.asm (local-only reference: `builds/phase51-msd-read-safety/b13-0801eb30.asm`; not distributed).

**PROVEN new native scope:** full incoming dispatcher, not merely248F0, followed by real deferred callback, class reset/register, descriptor merge, USB wrapper/controller setup and endpoint closure, executes twice for entry1 and twice for exit0. It visits685 distinct instruction addresses. USB HAL stop/start/init/FIFO/endpoint register operations, the disconnect delay and timer enqueue are explicit seams. Unlike Phase50,24630/245C6/246A8/2464C and their application wrappers execute natively. No Storage enqueue23F68, mount19A92, unmount1AE1C, settings-save2D2AC, content-write/delete/flush, NOR program/erase, or updater-reset39042 is reached. [mode_cases.py](<../../../builds/phase51-msd-read-safety/mode_cases.py>); mode-cases.json (local-only reference: `builds/phase51-msd-read-safety/mode-cases.json`; not distributed); b13-080245c6.asm (local-only reference: `builds/phase51-msd-read-safety/b13-080245c6.asm`; not distributed); b13-08024630.asm (local-only reference: `builds/phase51-msd-read-safety/b13-08024630.asm`; not distributed); b13-080246a8.asm (local-only reference: `builds/phase51-msd-read-safety/b13-080246a8.asm`; not distributed).

| Route | Persistent producers and state changes |

|---|---|

|A transient mode1 entry |**PROVEN tested route:** none; mode RAM/window pointer, timer state and USB controller/class state change. Registers MIDI200000EC + MSD200000F8; base94000. No MCU reboot or FS mount/unmount. USB stop/re-enumeration is not MCU reset. |

|B READ10 |**PROVEN:** read op1 plus queue-drain waits; no new write/erase/FS flush producer. Existing unrelated queued operations can complete during the waits. |

|C transient mode0 exit |**PROVEN tested route:** none; same class rebuild with MIDI only, mode0. No FS restore/remount because no FS was unmounted. |

|UI Advanced Setup bit17 toggle, either direction |**PROVEN conditional producer:** setting commit353C0→registered changed-settings callback2D278→2D300→2D2AC→128-byte write3C920+flush. This is not a read-only substitute for transient mode control. |

|SCSI START STOP/eject |**PROVEN:**57FB4→248CE→248B4 re-applies mode1, not mode0 exit; no explicit FS flush in this route. |

Sources for UI/save/eject: [mode-entry.md](<../phase50-msd-readonly-geometry/mode-entry.md>); [persistence-routes.md](<../phase46-msd-filesystem-closure/persistence-routes.md>); [msd-reachability.md](<../phase46-msd-filesystem-closure/msd-reachability.md>). No project/session, SD, NOR or updater metadata write producer was found solely in the tested transient entry/exit route. **UNKNOWN:** universal closure through modeled USB HAL/MSP/IRQ effects and independently scheduled background work; zero observed writes in these slices is not an exhaustive whole-system theorem. Entry assumes ordinary application state, no active updater or Storage fault.

Power-cycle alternative: **PROVEN** an abrupt power loss would bypass later execution of the normal exit routine; **UNKNOWN** persistence during the next boot, queued-write interruption, and cold-boot cleanup predicates. Prior phases explicitly leave those tied to actual filesystem state. It cannot be certified as a safer no-mutation exit or as evidence that entry/READ were safe. No physical action is recommended or performed. [startup-persistence.md](<../phase47-filesystem-state-closure/startup-persistence.md>).
