> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: FAILED / SUPERSEDED / DO NOT FLASH.

# Windows / MSD automount — scoped risk decision

Existing Phase46 initialized callback/native SCSI evidence remains applicable to the unchanged SCSI/class/callback code in this corrected image: application startup setting bit17 can register an MSD class; it is not universally safe to assume MIDI-only application enumeration. The initialized backend at20003788 returns write-protected through08057E48, and normal state0 WRITE10 admission rejects before the lower writer. Bootloader's normal registered configuration has Audio/MIDI and no class8 MSD.

Therefore: **no accepted writable volume is demonstrated on the normal initialized application SCSI path**; conditional read-only MSD exposure is possible from retained settings. This is not a universal malformed-BOT/host-write-isolation theorem. The lower write callback exists, and all possible transport states have not been re-proved here. Unknown actual settings must not be replaced with a guessed MIDI-only descriptor.

Safest future setup: use the established MIDI-only path, do not enable/toggle MSD or send vendor-mode commands, do not browse/format/repair any volume, and stop if unexpected storage exposure occurs. Prefer no filesystem mount at all. No Windows setting is changed by this phase.

Conditional preflight defense, BEFORE connecting a separately authorized device: record current automount policy in an elevated DiskPart session (`automount`), then use `automount disable` if required by that chosen test environment. Alternatively `mountvol /N` disables automatic mounting of new basic volumes. Record/restore the previous policy later; do not blindly enable it. These are host-wide configuration changes, not device read-only commands, and are not executed here. They do not guarantee isolation of already-known/already-mounted volumes or all low-level writes. Do not use global mount-point scrubbing as a substitute for a planned isolated environment.

Microsoft definitions: [DiskPart automount](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/automount), [mountvol](https://learn.microsoft.com/windows-server/administration/windows-commands/mountvol). These support the precise new-volume mounting limitation, not a universal storage write block. Project evidence: builds/phase46-msd-filesystem-closure/msd-reachability.md and initialized-ram-callback.md; no device/port inquiry was performed.
