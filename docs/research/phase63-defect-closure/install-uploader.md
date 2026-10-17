> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Exact identity, updater and rollback review

**PROVEN:** file-first independent decode and CRC equal the new BIN; 1,558 byte differences are classified in development-identity.json. MarkerN63DEV changes the native38-byte compared header at080101C8..080101EE; same-version header equality is not relied on to trigger installation.

**PROVEN in inherited explicit RTOS/peripheral models:** actual installed B1.3→development candidate, candidate→official4486 and candidate→B1.3 all install exact incoming bytes, with silent_noop=false. All selected application-staging instructions are checked against the actual installed source image, and actual RAM selector20003CC8→20003C88 is recorded. install-validation.json (local-only reference: `builds/phase63-defect-closure/install-validation.json`; not distributed) links summarized results; full operations and native summaries remain available.

All three transitions exclude internal bootloader00000..10000, use application internal flash10000..80000, preserve sentinels and have zero NOR write/erase overlap with81000..81017 and82000..82200. Metadata erase80000..81000 is exclusive at81000. Staging erases end at66000 for candidate,4D000 for official,6B000 for B1.3. These are offline updater-path results, not hardware rollback tests or complete cold-boot preservation proof.

**PROVEN:** review uploader `ct_uploader-phase63-offline-locked.html`, SHA-256 `bf1ef00dbca9c3715932235249fcc8ba0a71d6f2f989c047aa8caf66b85e17a5`, derived from exact reference ct_uploader.html SHA `c5d6bb67cd92720eac89d609ebaafc803902d28356840ae61691dd5987b43a6f`; upstream has no explicit semantic version. Its allowlist is narrowed to exactly the new candidate SYX and the two pinned rollbacks. Product0164, manufacturerF0 00 20 29 00, command order71/7C/72*/73, decoded size and MPEG-2 CRC checks remain. Marker and native header comparison are separately validated by the install replays.

**PROVEN:** uploader-tests.json (local-only reference: `builds/phase63-defect-closure/uploader-tests.json`; not distributed) executes the exact HTML parser in isolated Node VM, decodes all three files, verifies hash membership and tests MIDI/identify/send guards. Mock navigator MIDI call count=0. This is not a browser or device test. `PREFLIGHT_QUALIFIED=false` deliberately locks all three live handlers. Future approval requires a separately reviewed enabled copy with a new recorded hash; no enabled uploader is delivered for this ineligible image.

Rollback official SYX SHA bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd; B1.3 SYX SHA6f07376b5983a5e0350d4883ae9ed57a69bc735320afde9f43ca75017b8e8736. Files are in rollback/. Local manifest/file matching is **PROVEN**; independently authenticated vendor-origin acquisition of the local official file remains **UNKNOWN**, unchanged from Phase62.

No uploader/browser was opened, no port enumerated, and no transmission occurred. Existing Windows/MSD operational cautions and H4 full physical power-cycle requirement are unchanged; no OS storage setting was changed.
