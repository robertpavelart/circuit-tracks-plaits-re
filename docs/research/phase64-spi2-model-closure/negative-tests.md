> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Bounded native model tests

**PROVEN:** model-tests.json (local-only reference: `builds/phase64-spi2-model-closure/model-tests.json`; not distributed) runs the unchanged candidate's actual37960 helper in isolated argument fixtures. These fixtures are not inserted into startup RAM.

| Case | Native result |

|---|---|

| Normal delay3 | Returns after100 instructions; exact transformed test RX bytes; guards intact |

| Delayed completion30 | Returns after343 instructions; same exact output |

| Receive completion absent |5000-instruction observer stops at3798A; no fabricated receive or return |

| SPI disabled |5000-instruction observer stops at3798A; no fabricated receive or return |

The latter stops are observer bounds, not firmware timeout/error returns. The native routine has no bounded failure exit for these conditions. Tests confirm reset SR2 has TXE but no RXNE.

**PROVEN:** eleven peer-contract checks in peer-tests.json (local-only reference: `builds/phase64-spi2-model-closure/peer-tests.json`; not distributed): absent boot marker, uncompleted ARM request, completed wire marker, initialized idle mailbox, four exact ordered procedural jobs busy→complete, rejection of unsupported selector0, rejection of the unmodeled16-bit transition, and rejection of an unknown consumed readback. A prefetched value that is subsequently discarded may be marked unknown; consuming it instead stops the model. All accepted successful response values are supported separately by native DSP execution, not substituted ARM returns. Exact initialization-memory and job-order assertions prevent reuse of these contracts for unrelated requests.

**PROVEN:** native DSP producer tests (peer-ready-job.txt (local-only reference: `builds/phase64-spi2-model-closure/peer-ready-job.txt`; not distributed), peer-ready-output.txt (local-only reference: `builds/phase64-spi2-model-closure/peer-ready-output.txt`; not distributed), ready-writes.txt) run the unmodified extracted program. Zero XFFF remains waiting at25F3; nonzero XFFF reaches2601 and writes Y2B=1. Boot sets Y2C=800000 at2875. This is a targeted DSP execution with modeled peripherals and explicit XFFF stimulus, not a hardware test or full processor-pair replay.

**PROVEN:** [peer_mailbox_test.py](<../../../builds/phase64-spi2-model-closure/peer_mailbox_test.py>) reapplies2951 X-memory values captured from actual SPI words in the continuous ARM prefix and runs original DSP init to113, then invokes original1C53 via an emulator-only caller atP7000. The ordered exact jobs080002/094403/0A8804/0BCC05 reach800000 after1/327/327/327 service invocations. Each deferred job is observed for1024 invocations; its first326 areC00000 and the rest800000. Source1D2B publishesC00000 and1DA8 publishes800000;1D41 advances persistent continuation, including X1B15 and X42/43. The earlier32-service bound was insufficient, not a firmware hang. peer-contract-proof.json (local-only reference: `builds/phase64-spi2-model-closure/peer-contract-proof.json`; not distributed) pins program, observed initialization and native output hashes. This confirms the already saved Phase24 four-job result against this exact candidate's observed wire initialization; it does not reopen the prior investigation or claim cycle timing.

Earlier isolated selector probes mailbox-0/2/3/4/5-output.txt start from a less complete DSP state; they are exploratory and do not qualify full startup or actual deferred-job completion. No P7000 test caller is written to candidate images; extracted BE24 files are unchanged analysis inputs, not new deployable firmware.
