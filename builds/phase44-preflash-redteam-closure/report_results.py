"""Summarize completed offline evidence; no emulator, build or device action."""
from pathlib import Path
import json
O=Path(__file__).resolve().parent;R=O.parents[1]
def load(n):return json.loads((O/n).read_text())
def link(n):return f'[{n}](<{(O/n).as_posix()}>)'
def ranges(xs):return ', '.join('['+a+','+b+')' for a,b in xs)
def main():
 names=['b13-to-candidate','candidate-to-official','candidate-to-b13']
 old={n:load(n+'-summary.json') for n in names}
 new={n:load('atomic-'+n+'-summary.json') for n in names}
 ident=load('atomic-candidate-identity.json')
 for row in [*old.values(),*new.values()]:
  assert row['accepted'] and row['actual_install_performed'] and not row['silent_noop']
  assert row['incoming_image_sha256']==row['final_installed_sha256']==row['staged_image_sha256']
  assert all(x['writes']==0 and x['erase_overlaps']==0 and x['sentinel_unchanged'] for x in row['preservation'].values())
 a=old['b13-to-candidate']
 text='''# Exact B1.3 application-updater replay

**PROVEN within explicit offline seams:** the exact existing Phase43 candidate SYX is accepted by the authenticated B1.3 application updater, staged byte-exactly and installed by the authenticated bootloader. This does not substitute an SC35D8 application updater for the B1.3 updater.

B1.3 image SHA-256 `2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41`, length435220 (`0x6A414`). The reference manifest authenticates the COPY/ADD reconstruction; the complete installed application is loaded before the first native updater call. Exact incoming SYX SHA-256 `59be0e5733c70783c278ff5f89e575d77eef4dd3f6389841eac4a488111df32b`; decoded image SHA-256 `9b29180ff7f88c9c982c60abdfd5e5b296e8f2240ad57580366a5a7f797930a6`, CRC `AC9987BA`.

## Actual code/data/selector provenance

Native `08024D2C` vendor dispatcher, `08038CFC`/`08039088` state methods, block decoder `08024E20`, request queue, worker `08024014` and native NOR program/erase address algorithms execute from B1.3. The runner records every executed application PC and a digest of those actual B1.3 halfwords. It does not assign acceptance from a host protocol simulation. The worker's flag1→erase-first0 conversion executes rather than being assumed.

The selector fixture is separately authenticated by native B1.3 scatter decompression `080596C4`, descriptor `0805B7C8`, with poisoned output and independent decoder equality. All80 bytes at `20003C88–20003CD7`, including records/table, equal the running-RAM fixture. Initialized data hash `2db584abde65123402067c89720f5a10e12c40650b700d6af2f13ed93743e04f` (15618 bytes). This closes selector provenance without claiming complete reset/constructors.

| Selector | Native record | Base | Capacity |
|---:|---|---|---|
| 0 | `20003C88` | `0` | `80000` |
| 1 | `20003C98` | `D4000` | `1F2C000` |
| 2 | `20003CA8` | `82000` | `12000` |
| 3 | `20003CB8` | `94000` | `40000` |

All table values are hex NOR byte offsets/capacities. `20003CC8` holds the four record pointers. `080390B6–080390D4` bounds/loads the selector and `08038ECA–08038EDE` derives the selected staging address. Actual candidate selector=0, staging base=0, capacity=`0x80000`; the boot internal-application size bound is separately `0x70000`.

## Exact selected footprint

All intervals are half-open, NOR offsets in bytes unless explicitly internal flash.

'''
 text+=f'- NOR erase union: {ranges(a["external_erase_ranges"])}. Exact individual sector/page operations are in the operations JSON.\n'
 text+=f'- NOR program union: {ranges(a["external_program_ranges"])}. Staged bytes375948, padded375968 (`0x5BCA0`), including20 FF bytes; final staged SHA-256 `{a["staged_image_sha256"]}`.\n'
 text+=f'- Metadata: erase[0x80000,0x81000), program[0x80000,0x80017), raw23 bytes `{a["metadata"]}`.\n'
 text+='''- Internal effective erase sectors: [08010000,08018000), [08018000,08020000), [08020000,08040000), [08040000,08080000). The extra08080000 erase-wrapper call is a native no-op.
- Internal programs: [08010000,0806BCA0),93992 four-byte words. Logical image ends0806BC8C. Final375948 bytes equal the decoded candidate; bootloader unchanged.

| Guarded NOR region | Direct program overlaps | Erase overlaps | Nearest program | Gap | Nearest erase | Gap |
|---|---:|---:|---|---:|---|---:|
| [81000,81017) | 0 | 0 | [80000,80017) | 4073 | [80000,81000) | 0, adjacent |
| [82000,82200) | 0 | 0 | [80000,80017) | 8169 | [80000,81000) | 4096 |

Synthetic sentinels verify these two selected-path preservation claims; they are not authentic NOR contents.

## Is metadata address movable to81000?

**PROVEN for the native updater finalizer:** `0803901A–0803901C` permits metadata publication for selector0. `0803902C MOV.W r1,#0x80000` supplies the address directly, length23 at08039022, erase-first1 at08039020/28. The address is **hardcoded**, not selector-, argument- or table-derived. Table-derived staging bases do not shift this publication to81000. Boot metadata read08003B36 and recovery publication08007D28 independently use80000. Within these decoded finalizers no alternate branch substitutes81000.

**PROVEN distinction:** identity setter08005DB4/app08025228 intentionally writes81000; this is a separate feature, not relocated updater metadata. Factory chip erase/resource-selector update can affect other regions. **UNKNOWN:** arbitrary corruption/indirect clients and complete normal boot/background mutation closure; this report does not prove global NOR immutability.

## Corrected candidate follow-up

The existing candidate was replayed unchanged first. A later native test proved its quarantine-store race. The separately named N44ATM correction was then replayed through actual B1.3 as well, with the same footprint and zero overlaps; its different CRC/metadata/hash are recorded separately. Do not conflate original identity with corrected identity.

## Explicit seams

**UNKNOWN beyond this model:** reset-to-ready constructors, actual timing/task scheduling, preparatory timer/DSP/UI acknowledgements, CRC peripheral, array-read completion, boot object construction and physical internal-flash primitives. Native queue/worker/address/validator/installer decisions run; those peripheral/RTOS completions are supplied at named seams. Not hardware recovery proof or full cold-boot write census.

'''
 text+='Evidence: '+', '.join(link(n) for n in ['transition_replay.py','b13-to-candidate-summary.json','b13-to-candidate-operations.json','selector_provenance.py','b13-selector-provenance.json','b13-08038c90.asm','atomic-b13-to-candidate-summary.json'])+'.\n'
 (O/'b13-updater-replay.md').write_text(text,encoding='utf-8')
 text='''# Rollback transition replay

**PROVEN within the native offline application-updater/boot-installer model:** all three requested transitions accept and actually erase/program the destination. None silently no-ops. Original Phase43 and corrected N44ATM cases are kept separate. All sizes/addresses below are byte units and half-open.

## Original exact Phase43 candidate

| Transition | Incoming bytes | NOR staging erase | NOR staging program (padded) | Internal program | Final installed SHA-256 |
|---|---:|---|---|---|---|
'''
 for n,a in old.items():
  text+=f'| {n} | {a["incoming_bytes"]} | {ranges(a["external_erase_ranges"][:1])} | {ranges(a["external_program_ranges"][:1])} | {ranges(a["internal_program_ranges"])} | `{a["final_installed_sha256"]}` |\n'
 text+='''
Every row uses selector0/base0/capacity80000. Every row additionally erases metadata [80000,81000), programs23 bytes [80000,80017), and performs the same four internal erase sectors [08010000,08018000), [08018000,08020000), [08020000,08040000), [08040000,08080000). Application code does not execute after handoff in this model. Every target direct-program/erase overlap is zero; nearest mutations to both targets are the same metadata ranges/gaps as b13-updater-replay.md.

B1.3 rollback SYX was not found as a standalone file locally. The existing published B1.3 image was encoded **only in memory**, and the resulting complete stream must match manifest SHA-256 `6f07376b5983a5e0350d4883ae9ed57a69bc735320afde9f43ca75017b8e8736` before replay. No new B1.3 firmware/SYX file was produced. This is exact authenticated-stream reconstruction, not a guessed substitute.

## Version/build and silent no-op decisions

**PROVEN:** application header handling admits protocol/header values and selects the storage record; actual complete transfers reach CRC success/publication. In boot08003B9A: size must be≤70000, selector0, CRC!=FFFFFFFF. Staged header compatibility bytes+4/+5 must match boot header080001C8+4/+5; CRC must pass. Then08003BE4–08003BF6 compares38 staged/current header bytes at image offset1C8 through1ED. Equal headers skip08003C24 installation; different compatible headers install. There is no numeric “newer than current build” comparison on this executed branch.

**PROVEN controls:** same valid image/header does zero internal writes; numeric metadata version000000 still installs official4486; changed executable code with an unchanged compared header also silently no-ops. Changing only the six-byte N44ATM marker inside that header makes the corrected image install over original Phase43. Therefore future binary edits must change that compared identity, not just CRC.

Metadata remains present after native validator/installer; it is not cleared there. A subsequent valid upload replaces it only after successful staging/CRC publication. Exact raw metadata per transition is in its summary JSON. It must not be described as an authenticated device metadata capture.

## Corrected N44ATM candidate follow-up

'''
 text+=f'Corrected BIN `{ident["BIN_sha256"]}`, SYX `{ident["SYX_sha256"]}`, CRC `{ident["CRC32_MPEG2"]}`.\n\n'
 text+='| Transition | Acceptance/install | Final installed SHA-256 |\n|---|---|---|\n'
 for n,a in new.items():text+=f'| {n} | Accepted; actual install; no no-op | `{a["final_installed_sha256"]}` |\n'
 text+='''
All corrected-case footprints and target overlaps match their original-case counterparts; only the candidate payload/CRC/metadata/identity changes. The corrected B1.3-to-candidate install is separately asserted byte-exact, not inferred from header compatibility. Own bootloader recovery intake is covered in recovery-mode-model.md and atomic-supplement.json, separately from these application-updater transitions.

**UNKNOWN:** hardware timing, actual physical flash/NOR faults, complete boot-to-capture mutation exclusion, every torn-install boundary and unit recovery. No hardware action occurred.

'''
 text+='Evidence: '+', '.join(link(n) for n in ['transition_replay.py','header-noop-control.json','recovery-results.json','atomic-candidate-identity.json']+[n+'-summary.json' for n in names]+['atomic-'+n+'-summary.json' for n in names])+'.\n'
 (O/'rollback-transition-replay.md').write_text(text,encoding='utf-8')
 print('Original and corrected application transition reports complete; six native full transfers verified.')
if __name__=='__main__':main()
