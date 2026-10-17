> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Deferred/background persistence

**PROVEN source/byte identity:** this diagnostic inherits SC35D8-era code, not the final B1.3 feature set. Saved background-evidence.json (local-only reference: `builds/phase45-nor-mutation-closure/background-evidence.json`; not distributed) authenticates all13 examined candidate ranges as unchanged from Phase43. Its rebuilt report has `persist19.fix_lock=true`; later `GUARD`, `REC_RESTORE`, `BLOB_KEEP`, `SAVE_MASK`, `GFX_GLOBAL` variants and late vcf21 behavior must not be imported without actual candidate-byte evidence. [Extractor](<../../../builds/phase45-nor-mutation-closure/extract_background_evidence.py>) reads builders as source only; none was executed.

| Feature | Trigger / delay / owner | Effect and predicate | Target conclusion |
|---|---|---|---|
| persist19 `c_pl_load` at806B4A0 | End of stock session apply, including power-up | Sets RESYNC bit0 in state+179 if `c_gfst` returns state | RAM only at this hook |
| `c_pl_new` at806B4B8 | New-project defaults | Sets NEW bit1 if state exists, then stock29A00 | RAM only in custom hook |
| `c_rs` at806B340 | DSP service tick after load/new/power-up; **no inherited15/30s guard timer** | State exists AND RESYNC set AND all four drum handlers exist. NEW may zero extension state; validate/load65 extension bytes, dirty drum parameters, clear held/master-effect state, clear flags | Native ARM/DSP mutable state/mailboxes, no raw NOR call in this custom work |
| `c_dtick19` | DSP-service chain | For each existing drum handler, choose lowest dirty bit, update flags/tag and write DSP mailbox through292F8 | DSP address space, not ARM external NOR |
| `c_pl_save` at806B4D6 | Stock save call redirected at802FE5E | State exists AND flags byte==0 permits `c_xm_save`; then stock802F63C always executes | Copies extension state into session/live storage; subsequent stock file save must be traced |
| srcview806B4F8..806B6CC | UI view/pad activity | Source-view RAM/LED handling; builder hook restored/retired as documented in final diagnostic | No new raw NOR writer in reviewed body; no invented automatic persistence timer |
| vpre-related state | Audio/service/note/parameter handling | DSP routing, mailbox/state and mixing; no reason to equate DSP external SDRAM with ARM NOR | Does not by itself expose a NOR writer; global callback closure is separate |
| Stock session/project persistence | Save/restore/content jobs |2FE88→3C946→3CC16→3CA52→content queue22A5C/worker22AE4; op7→36B1C | File operation, not an inherently SD-only path |
| Content-file write | Content worker |36B1C selects storage/file object; vtable+14→25D98→19E50; seek/open state must pass | Disk0 can map to NOR partition; disk1 binds SD |
| Settings/status query26BDC | Vendor query type40 | Constructs operation0 at26C10, sends to NOR worker and returns status | This particular extra submit producer is not an array WRITE/ERASE |
| Updater metadata cleanup | Successful upload/reset/next boot | Native finalizers publish23 bytes80000 after CRC success; validator/installer retains metadata | No automatic metadata-clear write proved or assumed |
| USB-mode deferred callback |248CE schedules150 ticks;248B4/38C54 reapplies/transforms mode | Mode2 can transform to whole-NOR mode3; selection/root ordering still open | Must close mode invariant before excluding host MSD writes |

## Persistence backend correction

It would be incorrect to dismiss all project/session persistence as SD. Native disk dispatch `0801A7AC` selects object20000AA0 for drive0 and20001AF4 for drive1. Constructor1F0A8 binds their raw wrappers to20006968 (NOR) and2000696C (SD). Initialized geometry is baseD4000/sector1000 for NOR, base0/sector200 for SD. The file writer's logical offsets are not arbitrary physical NOR offsets, but the mapping must still be bounded.

**PROVEN in native mapper tests:** `0801AF1E` computes32-bit `base+sector_size*LBA` and forwards a write-with-erase request. For valid partition LBAs `<1F2C`, neither evidence region is touched. The mapper contains no own LBA-bound check; adversarial LBAs `FFFAD/FFFAE` wrap to81000/82000. **UNKNOWN:** complete upstream filesystem validation and automatic restore/flush predicates exclude those arguments. The tests deliberately inject them at the interface and do not assert ordinary filesystem reachability.

The exact live-store copy at3BBE2 only copies bytes into RAM; its presence is not physical persistence. Conversely, reaching file-write25D98/19E50 is not proof that disk completion happened or that it used SD. Keep these distinct.

## Remaining background obligations

**UNKNOWN:** complete stock save/flush scheduling and accepted on-storage metadata constraints across first-use project/session/settings restore; complete timer/USB callbacks before capture. The custom resync itself is narrowed to RAM/DSP, but its surrounding stock persistence system is not globally closed. Both can run within a pre-capture observation window depending on task/input/state predicates; no maximum quiet period is established. A hypothetical wait does not close reachability.

Evidence listings: persist19 (local-only reference: `builds/phase45-nor-mutation-closure/background-persist19.asm`; not distributed), srcview (local-only reference: `builds/phase45-nor-mutation-closure/background-srcview.asm`; not distributed), save tail (local-only reference: `builds/phase45-nor-mutation-closure/background-stock_save_tail.asm`; not distributed), content dispatch (local-only reference: `builds/phase45-nor-mutation-closure/background-content_dispatch.asm`; not distributed), content worker (local-only reference: `builds/phase45-nor-mutation-closure/background-content_queue.asm`; not distributed), file write (local-only reference: `builds/phase45-nor-mutation-closure/background-content_file_write.asm`; not distributed), live copy (local-only reference: `builds/phase45-nor-mutation-closure/background-live_store_copy.asm`; not distributed), new mapper tests (local-only reference: `builds/phase45-nor-mutation-closure/mapped-write-review.json`; not distributed).
