> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase59 — queue/work ordering

**PROVEN native allocation:**1E3A8 creates two1C-byte wrappers. NOR2000AC94 points to backend20000378; SD2000AD08 points to20000338. Each uses a3-record ring, record size18 hex /24 bytes, created by366E0. Wrapper+8 is ring object,+C pending count,+10 drain/sync flags,+14 Storage task object,+18 completion result. Content has its own2-record ring of48 hex /72-byte work items. These are ARM RAM queues, unrelated to DSP SDRAM. app-0801e3a8.asm (local-only reference: `builds/phase59-scheduler-first-mount-order/app-0801e3a8.asm`; not distributed), app-08023f2c.asm (local-only reference: `builds/phase59-scheduler-first-mount-order/app-08023f2c.asm`; not distributed), app-08022a0c.asm (local-only reference: `builds/phase59-scheduler-first-mount-order/app-08022a0c.asm`; not distributed).

**PROVEN observed normal producer chain:**Main1EC80→2520C submits identity read81000/23 bytes; the pre-mount ioctl obtains stride4096; filesystem BPB read becomes physicalD4000/4096. Native enqueue23F68→ring36708 precedes notify1BDE8(Storage,flag1). Storage registers completion observers before draining SD first, NOR second, via24014. Native36732 dequeues,24070 dispatches op0control/op1read/op2program/op3erase/op4sync;240D8 invokes optional completion callback. Each enqueue/dequeue/Storage drain and native ordinal is in the JSON.

|Enqueue instruction index|Producer TCB|Record opcode / arguments|

|---:|---|---|

|48931|0x2000835c|0x1 / 0x81000 / 0x20006868 / 0x17 / 0x0 / 0x0|

|53357|0x2000835c|0x0 / 0x3 / 0x20000abc / 0x4 / 0x0 / 0x0|

|56129|0x2000835c|0x1 / 0xd4000 / 0x20000aec / 0x1000 / 0x0 / 0x0|

**PROVEN tested scope:** no program/erase enqueue appears in the baseline or injected status-query case. Queue injection allocates32 bytes via the real allocator then invokes real23F68 before SVC with a well-formed read-only control record, rather than editing a queue link. It tests a valid queue state, **not a demonstrated normal pre-scheduler producer**. Normal constructor/startup observed queues are empty at scheduler launch. queued-query.json (local-only reference: `builds/phase59-scheduler-first-mount-order/queued-query.json`; not distributed), app-08023f2c.asm (local-only reference: `builds/phase59-scheduler-first-mount-order/app-08023f2c.asm`; not distributed).

**UNKNOWN complete producer exclusion:** Content operation dispatch22B24 (eleven cases), queued completion callback240D8, indirect UI/USB producers and future binding/remount changes still require transitive reachability/argument proof. A blank queue in a replay does not prove all producer predicates false. Existing preserved producer graph remains scoped: [nor-mutation-callgraph.md](<../phase45-nor-mutation-closure/nor-mutation-callgraph.md>). No later B1.3 persistence feature is imported into the SC35D8-derived image by name.
