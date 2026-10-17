> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase57 — first relevant epoch provenance

**UNKNOWN — is1AE06 the first relevant filesystem epoch of the complete boot?** No earlier epoch was demonstrated; absence of one in the Main prefix is not the required full-chain proof.

**PROVEN application reset chain:** vector08010004→0805C00C; platform setup1BC78 then5C19C→5B990→scatter dispatcher5B590. Scatter record5B7B4 selects zero helper1A7EA, zeroing20003D04,20006A54); record5B7C4 selects596C4 for initialized data[20000000,20003D02). Record5B7D4 selects constructor-dispatch handler**0805B958**, whose iterator5B978 walks the relative constructor table[5B5B8,5B5E0). After it,5B9AE calls1D3C8. Sources: [app-0805c00c.asm (local-only reference: `builds/phase57-first-mount-provenance/app-0805c00c.asm`; not distributed), app-0805c19c.asm (local-only reference: `builds/phase57-first-mount-provenance/app-0805c19c.asm`; not distributed), app-0805b990.asm (local-only reference: `builds/phase57-first-mount-provenance/app-0805b990.asm`; not distributed), app-0805b590.asm (local-only reference: `builds/phase57-first-mount-provenance/app-0805b590.asm`; not distributed), app-0805b958.asm (local-only reference: `builds/phase57-first-mount-provenance/app-0805b958.asm`; not distributed), app-0801a7ea.asm (local-only reference: `builds/phase57-first-mount-provenance/app-0801a7ea.asm`; not distributed), ownership.json (local-only reference: `builds/phase57-first-mount-provenance/ownership.json`; not distributed).

|Constructor table slot |Authenticated Thumb target |

|---|---|

|0x805b5b8|0x8059381|

|0x805b5bc|0x801dc65|

|0x805b5c0|0x801debd|

|0x805b5c4|0x801f051|

|0x805b5c8|0x805be05|

|0x805b5cc|0x8025079|

|0x805b5d0|0x802e689|

|0x805b5d4|0x802eb99|

|0x805b5d8|0x804633d|

|0x805b5dc|0x8058345|

**PROVEN:**1F050 in that list invokes1ADD0 to initialize disk vtable/drive/geometry pointers.1ADD0 only writes those object fields; it does **not** call mount. Other entries include USB/peripheral structures, raw backend/controller setup and state initialization. Listed bodies/callees have not all received a complete transitive callback closure; the table itself is enumerated, not guessed from function names.

**PROVEN:**1D3C8 creates Main/UI/Storage/Content via1DDD4 before scheduler start1DE78. The Content task22ACC waits/drains22AE4; its queue22A0C→366E0 initializes input/output indices0 at366FC/FE. This is native queue-initialization evidence, not a proof that no producer subsequently submits before Main's snapshot. app-0801d3c8.asm (local-only reference: `builds/phase57-first-mount-provenance/app-0801d3c8.asm`; not distributed), app-0801dd80.asm (local-only reference: `builds/phase57-first-mount-provenance/app-0801dd80.asm`; not distributed), app-08022a0c.asm (local-only reference: `builds/phase57-first-mount-provenance/app-08022a0c.asm`; not distributed), app-080366e0.asm (local-only reference: `builds/phase57-first-mount-provenance/app-080366e0.asm`; not distributed).

**PROVEN Main prefix:**1D4B0→1EC80(identity,including2520C read), then1EEAA→25AC6→2448C/24484/3ADBC→2445C peripheral/display service, then1F0A8→NOR1ADDC→f_mount19A92→197A0→return1AE06; SD follows. No earlier Main filesystem mount is present in this prefix. Do not treat that prefix as a reset-to-Main trace. app-0801d4b0.asm (local-only reference: `builds/phase57-first-mount-provenance/app-0801d4b0.asm`; not distributed), app-0801eeaa.asm (local-only reference: `builds/phase57-first-mount-provenance/app-0801eeaa.asm`; not distributed), app-08025ac6.asm (local-only reference: `builds/phase57-first-mount-provenance/app-08025ac6.asm`; not distributed), app-0803adbc.asm (local-only reference: `builds/phase57-first-mount-provenance/app-0803adbc.asm`; not distributed); successful mount details reused from [mount-to-persistence-ordering.md](<../phase55-precleanup-geometry-snapshot/mount-to-persistence-ordering.md>).

**UNKNOWN exact earlier obligations:** completed bootloader control after the real81000 read at051C2; all10 application constructor subgraphs/registered callbacks before1D3C8; and normal producer ordering between queue initialization22A40 and Main mount1D4C0. Concrete dispatch boundaries include UI1D698→1E4BE and Content22ADA→22AE4. No earlier actual filesystem epoch is invented to fill these gaps. The current saved cold-boot execution never reaches application1AE06.

**STRONG INFERENCE:**5B958 entry offers a new preconstructor initialization point after scatter memory initialization. Replacing its initial4 bytes(PUSH r4,lr;MOV r4,r0) with a correctly wrapped hook could reserve/reset the same12 bytes before any constructor. The helper must replay the displaced prologue and preserve the scatter argument/return contract. This is a site proposal, not patched code or proven all-boot liveness. Any earlier unexpected application mount encountered after that guard would quarantine, not become an accepted first snapshot.
