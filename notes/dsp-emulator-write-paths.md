# Phase 19A — audited enabled write paths

2026-10-06. IMPLEMENTED/TESTED for forced-interpreter syntheticfixture harness,
not generalDSP56724 stock replay certification. Exact source andoverlay hashes:
emulator/harness/source-manifest.json; reviewdiff:instrumentation.patch.

| Site/path | Instrumentation | Exercised by |
|---|---|---|
|DSP::memWrite→Memory::dspWrite|replayWrite callback delegates all authoritativeRAM commits toBus::write; same-valuewrites retained|direct,indirect,postinc/postdec,predec,indexed,offset,bit_store|
|Parallel X/Y stores|same callback, two records with common instruction ordinal|parallel|
|DSP::memWriteP→Memory::set|same bus; existing opcode invalidation retained|pwrite,dma_p|
|Memory::get/getOpcode|authoritativeread callbacks; boundsfaults andwatch ranges|read_watch,invalid_read; allfixtureopcodefetches|
|DSP::execOp|opcode/context callback for normal/DO/IRQ execution|do,do_offset,nested,interrupt|
|DSP::rep_exec cachedfunc loop|explicit callback before each subsequent iteration|rep,modulo/modulo_dec|
|DmaChannel::memCopy individual andfast branch|fastmemcpy replaced with perwordread/write; no rawpointer writes|dma_copy,dma_controller,dma_p,dma_shared|
|DmaChannel::memFill direct/individual/readMultiple branches|directpointer fill replaced byperwordmemWrite; individual and peripheral-source branches mediated|dma_fill,dma_p_fill,dma_peripheral_fill|
|DmaChannel::memCopyToFixedDest|existing perwordmemWrite mediated|dma_fixed|
|DMA::memWrite normal/P/peripheral|normal/P reach samebus; unsupportedperipheral destination faults|dma_copy,dma_p,dma_peripheral_copy; genericexternal/chipperipheral transfers notenabled|
|Peripherals56362::write|guard/observer before approvedfixture registersemantics; log command transaction|peripheral;initialcontrolwrites|
|Y peripheral adapter|allunmodeledaddresses fault|strict enabled surface; noYperipheralmodel|
|Loader/host/worker toy actors|Bus::write, withnonCPU PCnull anddeclaredkind|allprogram loads;actors fixture|
|InvalidRAM/peripheral|explicitfault+address/PC; no silentzero/drop|invalid_read/write/peripheral,custom_sizes|

**IMPLEMENTED source guard:**203 sourcefiles plus harness/build/testdefinition
hashes. Changing/adding/removing source forcesauditfailure; not automatically
accepted by regeneratinghashes. Restoredmemcpy/directfill/rawpointer DMA calls
fail structuralchecks; requiredfixturesmustallpass. The negativecopy adding an
unregisteredstore sitefailed as intended. No negativealteration touched live
core/original/vendor artifacts.

**JIT DISABLED:**jitmem.cpp can emit rawsingle/parallelbufferstores; jitops_mem,
optimizedloops andPcache pathsneedfuturecomplete interception. LinkedJITclasses
are not used forDSPfixtureexecution. NoJITinstrumentation implemented.

**Excluded/unresolved APIs:** OMF/bootROMloader,externalBusDevice,fullperipheral
models/ICCworker,rawmemorypointer clients,arbitrarychangedsource orJITexecution.
These are not exposed as a certified replaymode. Sourceguarddetects changes,
but cannot by itself prove semanticcoverage of anunexecutedpath. The spare
upstreamrawarrays are not authoritativefixtureRAM; APIs that use them must
not be introduced withoutbus mediation andnewcoveragefixtures.

**Metadata limit:** applicableRn is recorded forunambiguousfixtureoperands,
otherwise null; parallelorunrecognizedmetadata isnot invented. LOOP labels
come fromauditedfixtureannotations. GeneralstockEAorigin/actor/space translation,
complete before/after registerstate andunknown-value tracking remainlaterwork.
