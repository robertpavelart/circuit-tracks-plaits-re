> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# NOR mutation graph — Phase45

**UNKNOWN: complete transitive reachability closure.** The preserved initial graph is a candidate xref inventory, not a complete CFG. This continuation expands it through initialized-RAM callbacks and filesystem mapping. It must not be promoted to an exhaustive proof merely because all direct branch candidates were scanned.

Evidence: saved graph (local-only reference: `builds/phase45-nor-mutation-closure/mutation-graph.json`; not distributed), [graph extractor](<../../../builds/phase45-nor-mutation-closure/mutation_graph.py>), native application listing (local-only reference: `builds/phase45-nor-mutation-closure/mutation-app.asm`; not distributed), native boot listing (local-only reference: `builds/phase45-nor-mutation-closure/mutation-boot.asm`; not distributed), additional global references (local-only reference: `builds/phase45-nor-mutation-closure/additional-global-xrefs.json`; not distributed), [Phase44 census](<../phase44-preflash-redteam-closure/nor-write-erase-census.md>).

## Reviewed primitives

Addresses are ARM instruction addresses; target intervals elsewhere are half-open NOR byte offsets.

| Primitive | Application / boot | Opcode and geometry | Address/length source and callers |
|---|---|---|---|
| Page program | `080374D4` / `08007770` | `$02/$12`; backend splits at256-byte pages | 32-bit address argument, buffer/count; app backend `08022FDC` call2305E, boot backend05380 call053F6 |
| Sector erase | `08037494` / `08007730` | `$20/$21`;4096-byte sectors | backend `08023078` call230DC / boot05410 call05474; start/end arguments |
| Chip erase | `08037648` / `080078E4` | `$60`; whole array | both backend erase endpoints must equal `$CF525EB4`; app230C6 / boot0545E |
| WREN/status/mode | command engine `0803769C`, controller `08022746`; boot equivalents in saved listing | reviewed descriptors `$06` WREN, `$05` status read, `$F5/$35/$B7` mode commands, `$AF` identity read | native driver initialization and program/erase helpers; address-mode/config effects matter even without an array program |
| Metadata publication | app `08039008`; boot recovery `08007D06` |23 bytes; erase-first sector | hardcoded80000, through storage WRITE interface |
| Identity writer | app `08025228`; boot `08005DB4` |23 bytes; erase81000,82000) | hardcoded81000; registered callback, not updater relocation |
| Block erase/write-status | No separately qualified32/64KiB erase or general status-register writer in reviewed driver | **UNKNOWN** global absence | arbitrary controller-descriptor clients cannot be excluded by this bounded helper map |

Serial addressing supports mode-dependent opcodes; native scalar addresses are32-bit. The earlier traced read has32-bit controller addressing. Complete width/configuration closure for every command-producing client is **UNKNOWN**; do not substitute the reference NOR part's datasheet for this unit's configuration. [Reviewed command records (local-only reference: `builds/phase45-nor-mutation-closure/nor-command-descriptors.json`; not distributed) include only six actual referenced descriptors, not arbitrary16-byte data interpreted as commands.

## Transitive routes actually established

| Root / producer | Route to mutation | Trigger / reachability limit |
|---|---|---|
| Application updater | dispatcher24D2C → selector/state38CFC/39088 → wrapper24164/241F0 → submit23F68 → worker24014 → backend22FDC/23078 → primitives | Complete accepted SysEx transition; selected selector0 traces preserve both targets. Other resource selectors are separate routes. |
| Recovery updater | boot intake59C4/59FA →7B*/7C*/7D* → boot storage wrappers → backend05380/05410 | Native own recovery intake proved separately; hardware entry now user-reported, rollback flashing untested. |
| Factory erase | app24DB0→241F0→worker→23078→37648; boot5A40→5940→05410→078E4 | SysEx77 and two magic arguments; not ordinary absence-of-input behavior |
| Identity edit | app2527C/252F8→registered callback→25228; boot5E10/5E88→callback→05DB4 | Enable bit10, matching vendor/subcommand6C, exact14-byte valid identity; app additionally requires old cached identity invalid |
| Project/session file save | content3CA52→queue22A46/22A5C→worker22AE4, op7→36B1C→file method25D98→19E50→disk-write abstraction | File namespace and physical backend must be followed; it is incorrect to classify all content writes as SD |
| Disk0 mapped write | disk dispatch1A7AC/1A7B4→1AF1E→NOR wrapper24164→worker→program/erase | Object20000AA0, geometry20000A98: baseD4000, sector4096. No local LBA bound check; upstream filesystem bound not yet proved. Disk1 selects20001AF4 / SD binding. |
| USB mass-storage write | **initialized RAM pointer2000379C=08057EF5** → callback57EF4 → native mode-selected address → wrapper24164 → worker | This callback was missed by flash-only pointer scanning. See new tests below. |
| Diagnostic | admitted command13 →47C6C→24130 READ→worker read branch | Fixed23 +8×64 schedule; no new write/erase producer |

Storage worker write dispatch is240B2, erase240C2, completion callback240D8. Six immediate submit candidates include five wrappers and the extra26C10 producer. The latter constructs operation0/status-query, not an array-write record; see saved `background-settings_read_query.asm`. Enumerating wrapper callers is not sufficient to close callers of their vtable slots or arbitrary queued callbacks.

## Newly established initialized-RAM and address-bound edges

[msd_writer_review.py](<../../../builds/phase45-nor-mutation-closure/msd_writer_review.py>) authenticates decompressed callback pointers and executes eight native mode/address cases. Default mode1 selects record08038C3C (base94000); mode2 baseD4000; mode3 record08038C44 base0. Mode3 with block81/82 programs and requests erase of81000/82000 sectors. This proves a **conditional capability**, not that ordinary boot enters mode3.

Mode setter038C10 is called by vendor handler24918/2492E and delayed USB-mode callback248B4→38C54. That callback can remap modes, including2→3. Timer setup248CE uses150 ticks. Complete exclusion of all such mode writes/queued callbacks over the actual boot-to-capture schedule remains **UNKNOWN**.

The callback's own block-index check is `<2000` (hex), not a proved bound to every selected window's advertised extent. The default/window test cases establish numerical32-bit addresses for the exercised arguments, not every host SCSI range check or physical NOR out-of-range behavior. Those upstream bounds and address-mode/array-access semantics remain part of closure; no untested wrap/alias behavior of this unit is assumed either safe or destructive.

[mapped_write_review.py](<../../../builds/phase45-nor-mutation-closure/mapped_write_review.py>) executes native `1AF1E`: `address=(D4000+4096*LBA) mod2^32`. Valid partition LBAs exclude targets. Adversarial LBA`FFFAD` maps81000; `FFFAE` maps82000. These are **not proven filesystem-produced LBAs**. They identify the exact upstream obligation: bound LBA/count and preserve object binding before claiming file persistence cannot hit evidence.

## Closure still required

**UNKNOWN:** all ordinary boot/restoration/timer/USB callback roots, their accepted data predicates, every filesystem logical-block producer, and computed queue/vtable target closure. Two concrete obligations now replace the old vague “background unknown”: prove the mass-storage mode invariant through248B4/24918/38C54, and prove filesystem LBA/count bounds upstream of1AF1E. No final candidate can be designated while those remain open.
