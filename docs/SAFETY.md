# Safety

## Physical device rule

Hard project rule: **do not open or physically probe the Circuit Tracks**.

No soldering, continuity probing, JTAG/OnCE/SWD, test-pad access, internal wiring, or other invasive hardware work.

Normal external interfaces only.

## Current hardware status

The current Phase63 `N63DEV` diagnostic candidate has **not** been installed on hardware.

Phase67 has a scoped offline/model PASS, but the stronger operational preflight remains **UNQUALIFIED**.

Do not describe the candidate as "safe to flash".

Preferred wording:

> Reasonable to proceed with a controlled hardware test, subject to explicitly accepted residual risk.

## Accepted residual risk

The user accepts:

- possibility of a soft brick;
- possibility that recovery may be required.

This acceptance does not convert unknown recovery behavior into proven behavior.

## Recovery evidence

### PROVEN on the physical unit

- recovery/bootloader mode can be entered;
- recovery mode can be exited by full power cycle;
- B1.3 boots normally afterward;
- no firmware was transmitted during the rehearsal.

### NOT PROVEN

- recovery-mode host enumeration;
- uploader handshake in recovery;
- actual recovery flash of B1.3;
- actual recovery flash of stock 4486;
- recovery from a non-booting diagnostic candidate;
- guaranteed recovery.

No concrete bootloader-loss path has been identified in the current candidate.

The bootloader remains outside the modeled application erase/program range.

Candidate-specific physical recovery remains **HARDWARE-ONLY UNKNOWN**.

## Operational-tool rule

The frozen host and uploader remain intentionally locked.

Do not manually toggle:

- `live_enabled=false`
- `PREFLIGHT_QUALIFIED=false`

A separately reviewed operational release with new hashes is required before hardware use.

## Windows / removable-storage rule

Before an authorized hardware session:

- back up projects and SD content;
- do not rely on automount disable alone as write isolation;
- apply the prepared removable-storage denial policy;
- close Components, DAWs and other MIDI users;
- do not browse the exposed filesystem;
- do not accept scan/repair prompts;
- do not format;
- do not touch or modify the SD card;
- unexpected storage access or mounted-volume behavior means **STOP**.

## Diagnostic-session rule

The capture workflow is intentionally one-shot.

Geometry must be queried and validated before authorization.

If geometry is unsafe or unknown, stop and do not authorize.

If raw capture fails:

- discard partial evidence;
- no retry within the failed session;
- no second diagnostic/Storage request;
- no cleanup request;
- full physical power OFF;
- unplug USB;
- end the session.

H4 therefore remains **FAIL**.

## Evidence labels

Use these labels consistently:

- **PROVEN**
- **STRONG INFERENCE**
- **UNKNOWN**
- **FAILED**
- **SUPERSEDED**
- **HARDWARE-ONLY UNKNOWN**

A scoped/model PASS is not physical proof.
