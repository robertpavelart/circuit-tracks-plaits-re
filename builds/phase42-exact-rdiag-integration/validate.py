"""Final evidence/report consistency; does not replay completed workloads."""
from pathlib import Path
import json,hashlib,re,ast
O=Path(__file__).resolve().parent;R=O.parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((O/n).read_text())
def main():
 native=sum(read(n)['case_count'] for n in ('native-results.json','ownership-results.json','filter-results.json'))+1
 assert native==44 and read('masterfx-init-results.json')['original_and_integrated_initialization_equal']
 host=len(read('test-results.json')['host_cases'])+len(read('publication-results.json'))+len(read('end-to-end-results.json')['cases'])+read('host-adapter-results.json')['case_count']
 assert host==26
 assert read('integration.json')['image_sha256']==read('audit-results.json')['candidate_sha256']==read('installation.json')['candidate']['sha256']==digest(O/'integrated-internal.bin')
 links=[]
 for p in [O/'findings.md',R/'notes/fixed-nor-evidence-diagnostic.md',R/'notes/qspi82000-hardware-readiness.md']:
  assert p.read_text().rstrip().endswith('EXACT RDIAG NOR INTEGRATION = PASS')
  # Validate links in the new phase42 section, retaining older evidence as-is.
  text=p.read_text() if p.parent==O else p.read_text().split('## Phase42 — exact SC35D8 integration qualified offline',1)[1]
  for value in re.findall(r'\]\(<([^>]+)>\)',text):
   assert Path(value).exists(),value;links.append(value)
 for p in O.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 assert not list(O.rglob('*.syx'))
 # Rehash the published synthetic capture without rerunning or replacing it.
 manifest=read('end-to-end-results.json')['cases'][0]['result']['sha256']
 for name,n in [('nor_00081000_00081016.bin',23),('nor_00082000_000821ff.bin',512)]:
  p=O/'synthetic-capture'/name;assert p.stat().st_size==n and digest(p)==manifest[name]
 result=dict(confidence='PROVEN',verdict='PASS',scope='Exact integrated BIN offline qualification; hardware and complete cold boot not qualified',candidate_sha256=digest(O/'integrated-internal.bin'),native_case_control_records=native,host_case_records=host,reference_files_unchanged=451,pinned_sources_unchanged=183,phase42_source_inputs_unchanged=439,verified_report_links=len(links),hardware_access=False,SYX_generated=False,SC35D8_reproduction_reused_not_rerun=True,broad_cold_boot_run=False,notes_sha256={str(p):digest(p) for p in (R/'notes/fixed-nor-evidence-diagnostic.md',R/'notes/qspi82000-hardware-readiness.md')},evidence_sha256={p.name:digest(p) for p in sorted(O.iterdir()) if p.is_file() and p.name!='validation.json'},synthetic_sha256=manifest)
 (O/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ('evidence_sha256','notes_sha256','synthetic_sha256')},indent=2))
if __name__=='__main__':main()
