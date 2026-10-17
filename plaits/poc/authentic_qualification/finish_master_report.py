"""Finalize the report only after the independent evidence verifier passes."""
from environment import ROOT
from master_path import OUT
import json,re
def main():
 r=json.loads((OUT/'final-verification.json').read_text());long=json.loads((OUT/'long-result.json').read_text())
 assert r['main_blocks']==r['exact_native_state_and_transaction_checks']==8192 and r['qualified_shared_code_words']==1075
 assert not r['reference_inputs_changed'] and r['exact_stage_files'] and r['exact_output_journals']
 report=ROOT/'notes/stock-master-signal-path-qualification.md';text=report.read_text(encoding='utf-8')
 text=text.replace('2026-10-15. Offline B1.3 baseline and Layout A only. The short non-silent comparisons pass. The 8,192-block paired replay is in progress; its final result is recorded below when complete.',
  '2026-10-15. **PROVEN within the stated offline model:** the restored non-silent stock baseline and Layout A match through 8,192 consecutive numbered audio blocks, with no divergence. The three retained 64-block paired regressions also pass. The conservative 1,075-word shared-code budget is qualified for the next offline admission experiment; no Plaits engine was ported.')
 text=text.replace('The final long-run result and exact gate decision are appended after completion. Its explicit workload is',
  '**PROVEN:** the completed long replay contains')
 vpre=int(re.search(r'vpre=(\d+)',r['last_summary']).group(1));c1=int(re.search(r'c1contract=(\d+)',r['last_summary']).group(1))
 stereo=r['main_stereo'];signals=r['main_blocks_with_signal']
 extra=f'''

## 8. Final verification and admission decision

**PROVEN:** all 8,192 consecutive numbered blocks (0–8,191) completed in one uninterrupted rerun, without resetting either DSP. Every block has an exact native state/transaction comparison and an intact guard check in both layouts. There are {vpre:,} complete stock audio-block/vpre calls in total because actual ARM readback servicing also executes complete blocks. Those additional calls are included in sample-file and traffic comparisons; they are not substituted for the 8,192 required numbered blocks. The run issued {long['actual_ARM_DSP_reads']:,} actual-model DSP readbacks to the executing ARM code and checked the core-1 R5/M5 task contract {c1:,} times.

| Requested gate | Confidence / result | Evidence |
|---|---|---|
| Rendered samples, every captured stage and final stereo ring | **PROVEN — exact** | Complete baseline/Layout A stage files compare byte-for-byte; all 8,192 main-block output observations are present. |
| DSP data state | **PROVEN — exact, 8,192 comparisons** | Both cores' complete private X/Y backing, shared SRAM and declared external words/known bits/canaries. |
| Supported architectural registers | **PROVEN — exact** | Native boundary comparisons plus {vpre:,} vpre caller contracts and {c1:,} core-1 task contracts. |
| Shared/external transactions | **PROVEN — exact** | Ordered value/address/core/space/read-write/origin records, compared as bytes; private writes included. Negative transient-write control also passes. |
| P:`3BBA–3FFF` | **PROVEN — intact** | 8,192 block-end checks per layout; opcode-time execution/data guards throughout; zero P writes. |
| Active stock Synth1 and Synth2 | **PROVEN** | Isolated-bank tests plus {r['both_banks_nonzero_main_blocks']:,} main blocks with both accumulated banks nonzero. |
| Mixer, level/pan automation and sends | **PROVEN for exercised cases** | Long mixer path/global sends, plus retained 64-block real ARM parameter-listener automation with distinct L/R output and measured nonzero send stores. |
| Active Master FX | **PROVEN for exercised selectors** | Both retained 64-block active-effect comparisons pass, including actual DSP effect-loop execution. This is separate from the long run's ordinary FX service/bypass coverage. |

The final main-block stereo output has L/R peaks **{stereo['left']['peak']:,} / {stereo['right']['peak']:,}**, L/R RMS **{stereo['left']['RMS']:.6f} / {stereo['right']['RMS']:.6f}** in signed integer sample units, and L/R nonzero sample counts **{stereo['left']['nonzero']:,} / {stereo['right']['nonzero']:,}** out of {stereo['left']['samples']:,} samples per channel. Main-block observations with nonzero signal: Synth1 bank **{signals['bank0_pre_strip']:,}**, Synth2 bank **{signals['bank1_pre_strip']:,}**, final ring **{signals['output_ring']:,}**. Idle/released blocks are retained rather than removed from the comparison.

The rerun also reproduces **{r['preserved_stage_prefix_reproduced_bytes']:,} bytes** of the interrupted run's preserved common stage prefix exactly. Thus the necessary reconstruction of continuous execution did not alter the earlier measured sample path. The independent verifier rechecks all 8,192 sequential comparison records, byte-compares complete output journals and sample files, verifies the P-guard logs and zero P-write counts, verifies the native executable against its existing build provenance, and confirms **{r['reference_inputs_verified']} reference inputs unchanged**.

Primary final evidence: [independent verification](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase20l-master-path/final-verification.json>), [long-run result](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase20l-master-path/long-result.json>), [per-block native comparison records](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase20l-master-path/long-checks.jsonl>), [baseline complete output](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase20l-master-path/long-baseline/output.txt>), [Layout A complete output](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase20l-master-path/long-layout-A/output.txt>), [streamed per-stage statistics](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase20l-master-path/long-baseline/stage-statistics.csv>), [main/all-observation summaries](<C:/Proj SSD/CODEX/CIRCUIT/builds/phase20l-master-path/long-baseline/stage-summary.json>), [verifier implementation](<C:/Proj SSD/CODEX/CIRCUIT/plaits/poc/authentic_qualification/verify_master_final.py>).

**STRONG INFERENCE:** Layout A's conservative deletion/relocation preserves the tested non-silent stock signal path and exercised retained control/effect paths, making its 1,075 reclaimed program words suitable for the next offline shared-code admission experiment. The original program has 16,365 words and Layout A has 15,290: the difference is exactly 1,075. The additional 19-word original tail remains excluded from this budget.

**UNKNOWN / not qualified by this replay:** audible sample drums or their sample payloads; isolated retained MIDI line audibility; active granular/capture/glitch content; delayed wet-tail return beyond the measured cases; every compressor/limiter mode; every project/restore mode; physical interrupt/ESAI timing and CPU headroom. Drum-message attempts and retained service/bypass execution do not prove those subsystems' audible operation. None of these is silently promoted to a passing full-feature hardware regression.

The qualified result is limited to this offline experiment and its exercised allocation/paths. No new DSP data-memory ownership, hardware recovery guarantee, firmware-image readiness or Plaits implementation is claimed. No firmware was generated or flashed, and no reference files were modified.

QUALIFIED PLAITS SHARED-CODE P BUDGET = 1075 words
'''
 assert '## 8. Final verification' not in text
 report.write_text(text+extra,encoding='utf-8');print(report)
if __name__=='__main__':main()
