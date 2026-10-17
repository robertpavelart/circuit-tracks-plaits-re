> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase46 — initialized callback provenance

**PROVEN:** the table is stock initialized data, not an address taken from the running fixture. [native_cases.py:provenance](<../../../builds/phase46-msd-filesystem-closure/native_cases.py>) poisons RAM with A5, loads each exact image, executes actual decompressor`080596C4` with descriptor`0805B7C8`, and compares every15618 output bytes with the independent decoder. Stock4486, published B1.3 and corrected diagnostic all produce SHA-256`2db584abde65123402067c89720f5a10e12c40650b700d6af2f13ed93743e04f`.

Descriptor`0805B7C8` supplies compressed source`0805C3C4`,2582 bytes, destination`20000000`. Scatter caller`0805B590` dispatches the decompressor before constructors/tasks; it returns the next descriptor. Thus pointers become valid on scatter completion. No NOR payload or synthetic state was used to produce them. decompressor (local-only reference: `builds/phase46-msd-filesystem-closure/app-080596c4.asm`; not distributed), native evidence (local-only reference: `builds/phase46-msd-filesystem-closure/native-cases.json`; not distributed).

`200037AC=20003788` points to:

| RAM slot | Initialized pointer | Role / observed caller |
|---|---|---|
|20003788 +0 |08057E31 | Init returns0; `08026D66–76` |
|2000378C +4 |08057E35 | Capacity8192×4096; `0803B3DE–EC`, `0803B434–42` |
|20003790 +8 |08057E45 | Ready returns0; `0803B2DC–E6`, `0803B496–9E`, `0803B588–94` |
|20003794 +C |08057E49 | Write-protected returns1; `0803B5AA–B2` |
|20003798 +10 |08057E89 | Raw NOR read; `0803B522–2E` |
|2000379C +14 |08057EF5 | Raw NOR write-with-erase if admitted; `0803B64A–58` |
|200037A0 +18 |08057FB1 | Max LUN0; USB control`08058EFA–F02` |
|200037A4 +1C |08057FB5 | Eject timer schedule; `0803B76A–70` |
|200037A8 +20 |0805B6B8 | Inquiry data; `0803B364–72` |

The actual write route is `08057EF4 → NOR wrapper [20006968] vtable+10 → 08024164 → queue/Storage worker → 08022FDC/08023078 → program/erase`. Eject's deferred target is`080248B4`; class/mode reconfiguration is not itself a storage write. Every table consumer found by the saved PC-relative reference inventory loads its slot; none of those consumers replaces the backend pointer or table entries. That inventory does **not** exclude arbitrary computed RAM aliases or memory corruption. callback-table.json (local-only reference: `builds/phase46-msd-filesystem-closure/callback-table.json`; not distributed), SCSI listing (local-only reference: `builds/phase46-msd-filesystem-closure/app-0803b27c.asm`; not distributed), USB class control (local-only reference: `builds/phase46-msd-filesystem-closure/app-08058ea0.asm`; not distributed).

**PROVEN:** actual targets and initialization source for the candidate are resolved. **STRONG INFERENCE:** under ordinary non-corrupt execution the table stays at those targets; no runtime table setter was identified. **UNKNOWN:** exhaustive whole-image alias-write exclusion / every malformed-BOT state transition. In particular the write continuation skips the state0 protection check, so a claim of universal hostile-host isolation would require the upstream state-lifetime proof, not just a table hash.

**PROVEN source scope:** `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/build_sc35d8.py:extra` installs persist19/probe35s/rdiag on its earlier chain; SC35D8 manifest records BIN SHA`1525c6662bbff9ced7e6055bb54e864615c30013f1b4dec4be6c404f8c750c05`. Its exact standalone BIN is absent from`firmware/sc35d8`; no builder was rerun. **STRONG INFERENCE:** this unchanged stock table was also inherited by SC35D8. **UNKNOWN:** separate native decompression from that exact standalone SC35D8 artifact. This limitation does not weaken the direct exact-byte candidate test.

Bootloader native decompression was tested separately: descriptor`08009694`, decompressor`0800927C`, destination`20000004`,11084 bytes, SHA`7e6f9f2ef9ae96a8ab8cf3f0b11b5df1520aad4bc483f559682525540b48bd18`. Its pointer table near`20000950` is USB descriptors/strings, as shown by the actual functions`08005F08..08005F7C`; treating seven consecutive pointers as an MSD table would be wrong. Its normal registered configuration has Audio/MIDI interfaces and no MSD interface. This is a registered-configuration proof, not an assertion that pointer scanning alone found every possible boot USB route.
