from pathlib import Path
from types import SimpleNamespace
import sys,json
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
import native_regression as selected
s=(R/'builds/phase62-final-preflight/reservation_negative_test.py').read_text().replace('import native_tests as T','import native_tests as UNUSED_T')
ns=dict(__file__=str(O/'reservation_tests.py'),__name__='selected_reservation',T=SimpleNamespace(**selected.ns));exec(compile(s,str(O/'selected-reservation-tests.py'),'exec'),ns)
result=ns['run'](selected.ns['image'],'Phase63 development')
(O/'reservation-tests.json').write_text(json.dumps(result,indent=2)+'\n');assert result['passed'];print('Reservation cases PASS',len(result['cases']))
