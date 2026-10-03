import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from k4_ramsey.dashboard import _timeline, render
from fractions import Fraction


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.reports = self.root/'reports'
        self.reports.mkdir()
        self.out = self.root/'journal.html'

    def record(self, name, numerator=1, denominator=32, **changes):
        run = self.reports/name
        run.mkdir(parents=True)
        candidate = b'{"test": true}'
        (run/'candidate.json').write_bytes(candidate)
        data = dict(status='completed', hypothesis='Testing a hypothesis', prediction='A prediction',
                    started_at='2026-09-27T12:00:00+00:00', total_seconds=1.25,
                    evidence='lean_native_checked', candidate_sha256=hashlib.sha256(candidate).hexdigest(),
                    verification=dict(status='lean_native_checked', numerator=numerator, denominator=denominator))
        data.update(changes)
        (run/'report.json').write_text(json.dumps(data))
        return run

    def page(self):
        self.assertEqual(render(self.reports, self.out), self.out.resolve())
        return self.out.read_text()

    def test_basic(self):
        run = self.record('basic')
        (run/'status.json').write_text(json.dumps(dict(status='failed', hypothesis='STALE', started_at='today')))
        page = self.page()
        self.assertIn('1 / 1', page)
        self.assertIn('1/32', page)
        self.assertIn('./reports/basic/candidate.json', page)
        self.assertIn('1.25 s', page)
        self.assertNotIn('STALE', page)
        self.assertIn('compiled Lean recount', page)
        self.assertIn('Static snapshot', page)
        self.assertIn('Gap to McKay · fixed units', page)
        self.assertIn('Numerator units with denominator 768⁴', page)

    def test_portfolio_is_notes_not_ranking(self):
        self.record('checked', 1, 32)
        research = self.root/'research'
        research.mkdir()
        (research/'portfolio-status.json').write_text(json.dumps({
            'updated_at': '2026-09-27T21:20:00Z',
            'limits': '8 agents; 4 compute jobs',
            'lanes': [{'lane': '<script>bad</script>', 'status': 'proposed',
                       'next_test': 'Unverified prediction: 0'}]}))
        page = self.page()
        self.assertIn('Current research portfolio', page)
        self.assertIn('&lt;script&gt;bad&lt;/script&gt;', page)
        self.assertNotIn('<script>bad</script>', page)
        self.assertIn('<small>checked</small>', page)
        self.assertIn('not verified scores or live process telemetry', page)
        (research/'portfolio-status.json').write_text('{broken')
        self.assertIn('checked rankings are unaffected', self.page())

    def test_escaping(self):
        self.record('evil"#<name>', hypothesis='<script>alert("x")</script>', error='<img src=x onerror=bad>')
        page = self.page()
        self.assertNotIn('<script>alert', page)
        self.assertNotIn('<img src=x', page)
        self.assertIn('&lt;script&gt;', page)
        self.assertIn('evil%22%23%3Cname%3E', page)

    def test_exact_best_and_corrupt_exclusion(self):
        # These fractions collapse to the same float, but the second is smaller.
        self.record('larger', 10**20+1, 10**22)
        self.record('smaller', 10**20, 10**22)
        corrupt = self.record('corrupt', 0, 1)
        (corrupt/'candidate.json').write_text('changed')
        self.record('failed', 0, 1, status='failed')
        page = self.page()
        self.assertIn('<small>smaller</small>', page)
        self.assertIn('4 / 2', page)
        self.assertIn('Candidate hash mismatch', page)
        self.assertIn('failed', page)

    def test_empty_and_ignore_nonexperiments(self):
        (self.reports/'report.json').write_text('{"status":"old"}')
        self.record('snapshot/ignored')
        page = self.page()
        self.assertIn('No experiment reports yet', page)
        self.assertIn('No checked candidate', page)

    def test_in_progress_and_invalid_values(self):
        run = self.reports/'running'
        run.mkdir()
        (run/'status.json').write_text(json.dumps(dict(status='searching', hypothesis='Live attempt', started_at='now')))
        self.record('invalid', denominator=0)
        page = self.page()
        self.assertIn('2 / 0', page)
        self.assertIn('Live attempt', page)
        self.assertIn('Invalid exact verification value', page)

    def test_timeline_exact_cumulative_best(self):
        self.record('first', 10**20+1, 10**22, started_at='2026-09-27T12:00:00+00:00')
        self.record('better', 10**20, 10**22, started_at='2026-09-27T12:01:00+00:00')
        self.record('worse', 1, 20, started_at='2026-09-27T12:02:00+00:00')
        page=self.page()
        self.assertIn('<svg',page)
        self.assertIn('Step line is the cumulative best',page)
        self.assertIn('best 1/100 · worse',page)
        self.assertIn('2026-09-27T12:01:01.250000+00:00',page)
        self.assertIn('McKay reference',page)
        self.assertIn('Published seed',page)
        self.assertIn('2026 announced &lt;0.030139; not reproduced',page)
        self.assertIn('stroke-dasharray="10 3 2 3"',page)

    def test_timeline_empty_single_and_bad_timestamp(self):
        self.assertIn('No hash-valid checked results',self.page())
        self.record('single')
        self.assertIn('<circle cx="530.000"',self.page())
        invalid=[(self.reports/'x/report.json',dict(started_at='bad',total_seconds=1),Fraction(1,32),'')]
        self.assertIn('No hash-valid checked results',_timeline(invalid,Fraction(1,32)))

    def weighted_record(self, name='weighted'):
        run = self.record(name, evidence='unverified', verification=None)
        candidate = run/'candidate-weighted.json'
        candidate.write_text('{"weights":[1,1]}')
        sidecar = dict(schema='k4-weighted-verification-v1',
                       status='lean_native_checked_weighted_v1', total_weight=10,
                       numerator=300, denominator=10000, candidate=str(candidate),
                       candidate_sha256=hashlib.sha256(candidate.read_bytes()).hexdigest())
        (run/'weighted-verification-v1.json').write_text(json.dumps(sidecar))
        return run, sidecar

    def test_weighted_sidecar_separate_contract(self):
        run, sidecar = self.weighted_record()
        original = (run/'report.json').read_bytes()
        page = self.page()
        self.assertIn('weighted v1 · checked', page)
        self.assertIn('300 / 10000', page)
        self.assertIn('total weight⁴', page)
        self.assertIn('candidate-weighted.json', page)
        self.assertIn('weighted-verification-v1.json', page)
        self.assertIn('below McKay', page)
        self.assertEqual(original, (run/'report.json').read_bytes())

    def test_weighted_bad_hash_denominator_and_path(self):
        for failure in ('hash', 'denominator', 'path'):
            with self.subTest(failure=failure):
                run, sidecar = self.weighted_record(failure)
                if failure == 'hash':
                    sidecar['candidate_sha256'] = 'wrong'
                elif failure == 'denominator':
                    sidecar['denominator'] = 10001
                else:
                    sidecar['candidate'] = str(self.root/'outside.json')
                (run/'weighted-verification-v1.json').write_text(json.dumps(sidecar))
        page = self.page()
        self.assertIn('3 / 0', page)
        self.assertIn('Candidate hash mismatch', page)
        self.assertIn('weighted denominator must equal total weight⁴', page)
        self.assertIn('weighted candidate must belong to this experiment', page)

    def test_graphon_evidence_is_separate_and_hash_gated(self):
        candidate_dir = self.reports/'graphon-parent'
        candidate_dir.mkdir()
        candidate = candidate_dir/'graphon-candidate.json'
        candidate.write_text('{"schema":"test-graphon"}')
        digest = hashlib.sha256(candidate.read_bytes()).hexdigest()

        lean_dir = self.reports/'graphon-lean'
        lean_dir.mkdir()
        lean = dict(status='completed',
                    evidence='independent_standalone_compiled_lean_exact_nat_recount',
                    hypothesis='Independent graphon recount',
                    candidate=dict(path=str(candidate), sha256=digest),
                    lean_recount=dict(density='3013898/100000000'),
                    trust='Compiled Lean test evidence')
        (lean_dir/'report.json').write_text(json.dumps(lean))

        latent_dir = self.reports/'graphon-latent'
        latent_dir.mkdir()
        latent_candidate = latent_dir/'graphon-candidate.json'
        latent_candidate.write_text('{"schema":"latent"}')
        latent = dict(status='independent_u256_ordered_recount_passed',
                      hypothesis='Latent refinement', actual_density='3013897/100000000',
                      finished_at='2026-09-27T12:05:00+00:00',
                      candidate_sha256=hashlib.sha256(latent_candidate.read_bytes()).hexdigest(),
                      trust='Exact U256 test evidence')
        (latent_dir/'report.json').write_text(json.dumps(latent))

        page = self.page()
        self.assertIn('Asymptotic graphon constructions', page)
        self.assertIn('Strongest exact graphon recount', page)
        self.assertIn('0.030138970000000', page)
        self.assertIn('Strongest compiled-Lean graphon recount', page)
        self.assertIn('0.030138980000000', page)
        self.assertIn('Independent exact native recount (U256)', page)
        # The overall headline and cumulative timeline include graphons too.
        self.assertIn('<small>graphon-latent</small>', page)
        self.assertIn('best 3013897/100000000 · graphon-latent', page)
        self.assertIn('binary, weighted, and graphon candidates', page)
        # These remain outside the binary/weighted run count and ranking.
        self.assertIn('0 / 0', page)

        latent_candidate.write_text('corrupt')
        page = self.page()
        self.assertNotIn('0.030138970000000', page)

    def test_cross_method_timeline_never_worsens(self):
        binary = [(self.reports/'binary/report.json',
                   dict(finished_at='2026-09-27T12:00:00+00:00'),
                   Fraction(1, 32), 'Compiled Lean')]
        graphons = [dict(path=self.reports/'graphon/report.json',
                         timing=dict(finished_at='2026-09-27T12:01:00+00:00'),
                         value=Fraction(3, 100), level='Native exact'),
                    dict(path=self.reports/'later-worse/report.json',
                         timing=dict(finished_at='2026-09-27T12:02:00+00:00'),
                         value=Fraction(31, 1000), level='Native exact')]
        chart = _timeline(binary, Fraction(1,32), graphons)
        self.assertIn('best 3/100 · graphon · Native exact', chart)
        self.assertIn('best 3/100 · later-worse · Native exact', chart)
        self.assertNotIn('best 31/1000', chart)

    def test_standalone_direct_graphon_recount_ranks_and_checks_hash(self):
        run = self.reports/'direct-graphon'
        run.mkdir()
        candidate = run/'graphon-candidate.json'
        candidate.write_text('{"fixture":true}')
        record = dict(status='completed',
                      evidence='independent_generic_direct_ordered_index_u256_recount',
                      finished_at='2026-09-27T12:00:00+00:00',
                      candidate=dict(path=str(candidate),
                                     sha256=hashlib.sha256(candidate.read_bytes()).hexdigest()),
                      direct_recount=dict(density='3/100'))
        (run/'report.json').write_text(json.dumps(record))
        page = self.page()
        self.assertIn('<small>direct-graphon</small>', page)
        self.assertIn('best 3/100 · direct-graphon', page)
        self.assertIn('Independent direct exact native recount (U256)', page)
        candidate.write_text('changed')
        self.assertNotIn('<small>direct-graphon</small>', self.page())


if __name__ == '__main__':
    unittest.main()
