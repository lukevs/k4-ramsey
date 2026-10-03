import json
from pathlib import Path
import tempfile
import unittest
from k4_ramsey.engine import ROOT, certificate, Graph
from k4_ramsey.lab import experiment, write_json


class StrategyTests(unittest.TestCase):
    def test_scan_and_anneal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root/'input.json'
            write_json(source,certificate(['00000']*5))
            for strategy,config in [('scan_descent',{}),('anneal',{'max_moves':100,'cycle_moves':25})]:
                result=experiment(out=root/strategy,input_path=source,
                    strategy=ROOT/f'experiments/strategies/{strategy}.py',
                    hypothesis='Tiny correctness fixture',prediction='Lean agrees',
                    seconds=1,timeout=6,config=config)
                self.assertEqual(result['status'],'completed',result.get('error'))
                self.assertGreaterEqual(result['improvement'],0)
                if strategy == 'scan_descent':
                    self.assertTrue(result['search_reported']['single_edge_local_minimum'])
                    graph=Graph(json.loads((root/strategy/'candidate.json').read_text()))
                    self.assertTrue(all(graph.delta(u,v)>=0 for u in range(5) for v in range(u+1,5)))


if __name__ == '__main__': unittest.main()
