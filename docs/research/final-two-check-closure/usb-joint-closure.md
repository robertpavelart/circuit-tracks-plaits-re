> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# USB Storage / diagnostic joint path

USB STORAGE JOINT PATH: PASS

**PROVEN in the new native/model cases and STRONG INFERENCE from the initialized normal-host control path:** a USB OUT transfer can be received while the diagnostic waits, but normal host media work is not submitted by a second Main invocation while Main is suspended in the diagnostic raw-read frame. PASS applies to this synchronization/ownership question, not to complete USB emulation, malformed-host fuzzing, or the separate unresolved allocation census.

## Exact synchronization

Frozen BIN SHA-256: `edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9`.

**PROVEN by instructions:** Main calls output service at `0801D5B4`, MIDI input/parser at `0801D5B8`, and BOT service `0801F37C` at `0801D5BC`; deferred queue service is at `0801D662`. Native yield `0801BE60` requests scheduling, not nested Main event dispatch. A yielded Main resumes the same suspended frame.

BOT service checks endpoint completion flags at `+1C`, clears them through `0801E626/0801E746`, then invokes `08026DB0/08026DE6`. Normal OUT completion `0801E6CC` posts the flag or services the pre-existing bounded endpoint queue; it does not submit a NOR request. READ10 follows `08026DE6 → 0803B27C → 0803B480..0803B52E → 08057E88`. The normal callback uses transfer buffer `40024000`, distinct from the diagnostic's live stack buffer.

The other direct BOT-service caller, `08025C2C`, is the Components transfer pump: constructor `08025C36` installs callback `08025C2D` in an object with vtable `0805C084`, consumed by transfer object `080394D8` at offset `+48`. Its thunk `0801E472` loads object `+4`. Incoming Components dispatch `0802505A → 08039674` and timer callback `080395A8` belong to Main processing; Content completions return through the Main queue. The raw wrapper/fence/yield does not invoke this pump. This is why the joint fixture has one Main actor, not two independently schedulable copies of Main. See `service-xrefs.json` and the focused `.asm` listings; the broader unresolved callback inventory is not represented as fully closed.

The queued read path is `08024130 → 08023F68 → 08036708` (24-byte operation-1 descriptor). Drain `08023FD6` sets wrapper `+16`, signals task `+20`, and yields until cleared. Storage loop `0805769C` processes SD/NOR via `08024014`; NOR backend `08022F94` atomically acquires semaphore `+8`, calls `08037430`, then releases it at `08022FD4`. Busy acquisition returns without acquiring a second owner.

Saved modeled NOR wrapper: `[20006968]=2000AC94`, backend `[wrapper+4]=20000378`, vtable `0805B1AC`. These RAM values are model evidence, not physical-unit authentication. Both read paths use this same request/semaphore/controller machinery.

Raw fence `08070D00` requires DMA EN `400264B8=0`, NDTR `400264BC=0`, wrapper `+16=0`, backend semaphore `+8=1`. The wait yields at `08070D36`; it does not force release. Both payload consumption and common raw-frame exit pass the fence. Native final POP is `08070CB8`. In the fixture, R7 frame is `20008198`, raw payload `R7+192=20008258`, 64 bytes; local/save contribution is 280 bytes. Geometry/lifecycle record is `20044D70..20044D7B`.

## Both orders and exceptional events

`joint_tests.py` adds 36 cases, all passing in saved `joint-results.json`. It imports the preserved Phase63 model without invoking its old test main, verifies the complete emulated application image against the frozen package BIN, and executes the native BOT consumer, queue, Storage backend, ownership fence and QSPI IRQ `080573E0`.

| Event | Storage first, diagnostic second | Diagnostic first, Storage second |
|---|---|---|
| Normal / pending | BOT completes before parser can enter raw read; subsequent diagnostic performs nine fixed reads | OUT completion is posted; BOT media consumer is deferred until the raw frame returns |
| Missing completion | Main remains in BOT wait; no diagnostic frame/request appears | Main raw frame remains live; no host media read or second QSPI submission |
| TEF | Same blocked-Main ordering; late same-request completion does not auto-launch diagnostic | Failure remains non-success; owner/frame retained until actual release |
| Timeout | No active diagnostic is created by the timer while BOT owns Main | Native timeout handling prevents accepted success and cannot bypass the owner fence |
| Disconnect | No diagnostic auto-entry; ownership is unchanged by modeled disconnect | Lifecycle/USB status cannot free the raw frame while DMA/request ownership remains |
| Late completion | Can finish the original BOT request; does not issue diagnostic automatically | Can release the original diagnostic owner; deferred BOT can run only after native frame return |
| Remount | Native invalidation cannot create a diagnostic request inside blocked Main | Authorization/lifecycle is invalidated; tested raw result is not success `14`; live buffer remains fenced |
| BOT reset | Valid class request `21/FF` resets BOT protocol state, not Storage/QSPI ownership | Same; no raw-buffer cancellation or second QSPI request |
| USB class reset/deconfiguration | Native `08037F46` does not steal backend ownership | Same; outstanding raw ownership survives until genuine completion |

BOT reset handling `08058ECC → 08026D94` acts on BOT state/CBW reception. Class deconfiguration `08037F46` handles class/endpoint state. Neither is a raw Storage cancel operation. The pending-reset tests compare DMA EN/NDTR, request flag and backend semaphore before/after the callback. No successful enumeration or full USB reset waveform was synthesized.

**PROVEN in the cases:** no concurrent second QSPI command, no second backend owner, no host alias of the diagnostic buffer, no frame return before all fence predicates release, and no accepted success after the tested timeout/disconnect/remount/fault invalidations. The normal Storage request can run after a failed raw frame finally returns; this is not permission to retry the diagnostic.

**PROVEN preserved policy:** H4 still has no bounded device-side unwind. TEF/missing completion may retain the frame indefinitely. Host capture failure means discard all evidence, DO NOT RETRY, and full power cycle before another attempt. Late completion is an injected observation of the same outstanding transaction, not a host retry or a cleanup command. No global permanent prohibition of every ordinary Storage operation is claimed.

## Model boundaries and corrections

The prepared exported-geometry fixture, cooperative scheduling, synthetic CBW contents, GetRxCount=31, USB IN submission completion boundary, DMA payload/flags, and disconnect event state are declared seams. The host READ10 case uses LBA64, 4096 bytes at physical `D4000`, destination `40024000`. Diagnostic reads cover 23 bytes at `81000` plus eight 64-byte chunks at `82000..821FF`. No physical bytes are authenticated here.

The BOT's 4096-byte clear helper at `0801A7E4` is modeled as its bounded clear semantics (asserting exact destination/length). Attempting that helper natively hit an inherited execution-model boundary; no firmware defect was inferred and no broader CPU/peripheral investigation was opened. Storage synchronization and ownership code remains native.

The new fixture ends its stack-buffer canary lease at the native final POP, after asserting all owner predicates, including when a remount leaves lifecycle INVALID rather than COMPLETE. The old fixture's success-only lease termination produced a false canary complaint when dead stack storage was legitimately reused after return. No live-buffer guard was disabled. All 36 final cases completed with these explicit seams/corrections. Their exact assertions and per-case observations are saved; this is not uninterrupted reset-to-host capture or a physical timing proof.

**UNKNOWN:** physical host timing/enumeration; arbitrary corrupted callback pointers; all downstream allocations behind the separate census's unresolved indirect targets. These are not silently folded into this synchronization PASS. No firmware changes or hardware actions were made.
