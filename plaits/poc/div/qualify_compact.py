"""Run the identical isolated fixtures against the compact native helper."""
import argparse
from pathlib import Path
import qualify
from generate_compact import helper
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output-dir',type=Path,required=True);a.add_argument('--fixture-exe',type=Path,required=True)
 ns=a.parse_args();qualify.helper=helper;qualify.qualify(ns.output_dir,ns.fixture_exe.resolve())
