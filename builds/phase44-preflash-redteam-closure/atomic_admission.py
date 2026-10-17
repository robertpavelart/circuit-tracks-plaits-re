"""Re-run unchanged phase43 admission/dormancy tests on corrected disk SYX."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];S=R/'builds/phase43-hardware-test-candidate'
sys.path.insert(0,str(S))
source=(S/'native_regression.py').read_text()
source=source.replace('circuittracks-4486-nor-evidence-test.syx','circuittracks-4486-nor-evidence-atomic-test.syx')
source=source.replace("O/'native-regression.json'", "O/'atomic-native-regression.json'")
exec(compile(source,str(S/'native_regression.py')+'[phase44-corrected-image]', 'exec'),dict(__file__=str(O/'atomic_admission.py'),__name__='__main__'))
