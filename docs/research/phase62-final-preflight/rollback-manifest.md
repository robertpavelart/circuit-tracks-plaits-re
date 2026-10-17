> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: FAILED / SUPERSEDED / DO NOT FLASH.

# Locally provisioned rollback chain

Files are physically present underrollback/ and pinned below. They were not sent/opened in a browser. The uploader HTML was copied byte-for-byte from the public reference repository, which was not modified.

| File | Bytes | SHA-256 | Provenance |

|---|---:|---|---|

|circuittracks-firmware-4486-STOCK.syx| raw instruction bytes omitted |`bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd`|C:\Proj SSD\CODEX\CIRCUIT\builds\phase43-hardware-test-candidate\rollback\circuittracks-firmware-4486-STOCK.syx|

|circuittracks-B1.3-manifest-matched.syx| raw instruction bytes omitted |`6f07376b5983a5e0350d4883ae9ed57a69bc735320afde9f43ca75017b8e8736`|Pinned official+COPY/ADD reconstruction, public B1.3 manifest C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\firmware\b1.3\manifest.json|

|ct_uploader-reference-pinned.html|48918|`c5d6bb67cd92720eac89d609ebaafc803902d28356840ae61691dd5987b43a6f`|C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\tools\ct_uploader.html|

B1.3 SYX independently decodes to BIN`2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41`, the actual installed image used by the new B1.3 updater replay and the exact incoming image in rollback. Its published SYX manifest hash matches exactly. Official4486 decodes to BIN`b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da`.

Official source provenance: **UNKNOWN for authenticated Novation-origin acquisition**. This phase inspected the existing reference/Phase43 files and baseline/provenance notes and found matching local bytes, not an independently authenticated Novation download record. No internet firmware download is substituted as if it were already available evidence.

The pinned reference uploader allowlists official4486 and B1.3, but **does not allowlist this corrected candidate**. Therefore rollback tooling is pinned, while a candidate-update uploader is not admitted. Do not weaken the allowlist or register a failing candidate merely to report readiness. Any future corrected candidate needs a reviewed exact-hash uploader binding. No uploader handshake or physical rollback flashing is claimed.

All3 exact frozen-image update/rollback replays pass: exact installed images, no silent no-op, bootloader equality, no internal operations outside application flash and zero external mutation overlap with either target. The modeled internal-flash calls never reach option bytes; this is not a physical option-byte measurement. See corrected-install-validation.json (local-only reference: `builds/phase62-final-preflight/corrected-install-validation.json`; not distributed), rollback-provisioning.json (local-only reference: `builds/phase62-final-preflight/rollback-provisioning.json`; not distributed) and the3 transition summaries/operation logs.
