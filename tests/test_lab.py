import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from k4_ramsey.engine import ROOT, certificate
from k4_ramsey.lab import experiment, run_process, write_json


class LabTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='k4-lab-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.input = self.root/'input.json'
        write_json(self.input, certificate(['010','101','010']))

    def run_one(self, name='run', strategy=None, **kwargs):
        return experiment(out=self.root/name, input_path=self.input,
            strategy=strategy or ROOT/'src/k4_ramsey/strategies/edge_descent.py',
            hypothesis='Test-only runner fixture', prediction='Exact recount agrees',
            seconds=.1, timeout=5, config={'max_moves':0}, **kwargs)

    def script(self, body):
        p = self.root/'fixture.py'
        p.write_text('import sys,json,shutil\nfrom pathlib import Path\n'
            "out=Path(sys.argv[sys.argv.index('--output')+1])\n"
            "inp=Path(sys.argv[sys.argv.index('--input')+1])\n"+body)
        return p

    def test_replay_and_no_overwrite(self):
        report = self.run_one()
        self.assertEqual(report['status'],'completed')
        self.assertEqual(report['improvement'],0)
        self.assertEqual(report['evidence'],'lean_native_checked')
        with self.assertRaises(FileExistsError): self.run_one()

    def test_parallel_isolation(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(self.run_one,['a','b']))
        self.assertTrue(all(r['status']=='completed' for r in results))
        self.assertEqual(results[0]['candidate_sha256'],results[1]['candidate_sha256'])

    def test_strategy_imports_frozen_package_without_pythonpath(self):
        s = self.script("import os,k4_ramsey.engine\n"
            "assert 'PYTHONPATH' not in os.environ\n"
            "assert Path(k4_ramsey.engine.__file__).resolve().parent.parent == Path(__file__).resolve().parent\n"
            "shutil.copy(inp,out)\n")
        report = self.run_one(strategy=s)
        self.assertEqual(report['status'], 'completed', report)

    def test_bad_claim_quarantined(self):
        s = self.script("shutil.copy(inp,out)\n(out.parent/'search.json').write_text('{\"numerator\": 0}')\n")
        report=self.run_one(strategy=s)
        self.assertEqual(report['status'],'failed')
        self.assertEqual(report['evidence'],'unverified')

    def test_nonfinite_metrics_still_leave_failure_report(self):
        for index, number in enumerate(['NaN', 'Infinity', '1e999']):
            with self.subTest(number=number):
                s=self.script("shutil.copy(inp,out)\n(out.parent/'search.json').write_text('{\"x\": " + number + "}')\n")
                name=f'nonfinite-{index}'
                report=self.run_one(name=name,strategy=s)
                self.assertEqual(report['status'],'failed')
                self.assertTrue((self.root/name/'report.json').exists())

    def test_self_modification_rejected(self):
        s=self.script("shutil.copy(inp,out)\nPath(__file__).write_text('# changed')\n")
        self.assertEqual(self.run_one(strategy=s)['status'],'failed')

    def test_failure_and_missing_output(self):
        s=self.script("raise RuntimeError('intentional test failure')\n")
        report=self.run_one(strategy=s)
        self.assertEqual(report['status'],'failed')
        self.assertIn('intentional', (self.root/'run/stderr.log').read_text())
        s=self.script('pass\n')
        self.assertEqual(self.run_one(name='missing',strategy=s)['status'],'failed')

    def test_process_timeout_and_nonzero_exit(self):
        common=dict(cwd=self.root,env=os.environ.copy(),timeout=.1,
                    stdout=self.root/'stdout',stderr=self.root/'stderr')
        r=run_process([sys.executable,'-c','import time; time.sleep(10)'],**common)
        self.assertEqual(r['status'],'timeout')
        self.assertLess(r['seconds'],2)
        with self.assertRaises(ProcessLookupError): os.kill(r['pid'],0)
        r=run_process([sys.executable,'-c','raise SystemExit(7)'],**common)
        self.assertEqual(r['returncode'],7)

    def test_sigterm_writes_report_and_reaps_search(self):
        s=self.script('import time\ntime.sleep(10)\n')
        out=self.root/'signal'
        env=os.environ.copy();env.pop('PYTHONPATH', None)
        command=[sys.executable,'-m','k4_ramsey.lab','run','--input',str(self.input),
                 '--out',str(out),'--strategy',str(s),'--hypothesis','signal test',
                 '--prediction','interruption recorded','--seconds','10','--timeout','20']
        p=subprocess.Popen(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            until=time.monotonic()+5
            while time.monotonic()<until:
                if (out/'stdout.log').exists(): break
                time.sleep(.02)
            self.assertTrue((out/'stdout.log').exists())
            p.terminate();p.communicate(timeout=3)
            self.assertEqual(json.loads((out/'report.json').read_text())['status'],'interrupted')
        finally:
            if p.poll() is None: p.kill();p.communicate()


if __name__ == '__main__': unittest.main()
