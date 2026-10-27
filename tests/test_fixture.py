"""Synthetic data contract and football-continuity smoke tests (stdlib only)."""
import json
import math
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MATCH=json.loads((ROOT/'public/data/match.json').read_text())

def dist(a,b):return math.hypot(a['x']-b['x'],a['y']-b['y'])

class FixtureTests(unittest.TestCase):
    def test_original_synthetic_provenance(self):
        self.assertTrue(MATCH['synthetic'])
        self.assertIn('Original fictional',MATCH['provenance'])
        self.assertEqual(MATCH['duration_ms'],80000)
        self.assertEqual(MATCH['fps'],5)
        self.assertEqual(len(MATCH['frames']),401)
        self.assertEqual(len(MATCH['players']),22)
        self.assertEqual(len(MATCH['events']),12)
    def test_exact_one_per_200_ms_and_22_unique_players(self):
        expected_ids={p['id'] for p in MATCH['players']}
        self.assertEqual(len(expected_ids),22)
        for i,f in enumerate(MATCH['frames']):
            self.assertEqual(f['t_ms'],i*200)
            self.assertEqual([p['id'] for p in f['players']],[p['id'] for p in MATCH['players']])
    def test_valid_bounds_and_speed(self):
        last=None
        for f in MATCH['frames']:
            for p in f['players']:
                self.assertTrue(0<=p['x']<=105 and 0<=p['y']<=68)
            self.assertTrue(0<=f['ball']['x']<=105 and 0<=f['ball']['y']<=68)
            if last:
                self.assertLessEqual(dist(f['ball'],last['ball'])/.2,40,'Synthetic ball teleport')
                for a,b in zip(f['players'],last['players']):
                    self.assertLessEqual(dist(a,b)/.2,9,'Player teleports')
            last=f
    def test_ball_follows_known_passes(self):
        # The source must own ball at the pass departure and the receiver at arrival.
        passages=[(9.0,10.2,'H6','H8'),(18.0,19.3,'H8','H10'),(43.0,44.5,'H10','H7'),
                  (56.0,57.4,'H7','H9'),(67.0,68.7,'A1','A4')]
        for start,end,src,dst in passages:
            fi=MATCH['frames'][round(start*5)]
            start_pos=next(p for p in fi['players'] if p['id']==src)
            self.assertLess(dist(start_pos,fi['ball']),.1)
            arrived=MATCH['frames'][math.ceil(end*5)]
            pos=next(p for p in arrived['players'] if p['id']==dst)
            self.assertLess(dist(pos,arrived['ball']),.3)
    def test_evidence_event_links(self):
        ids={p['id'] for p in MATCH['players']}
        times=[e['t_ms'] for e in MATCH['events']]
        self.assertEqual(times,sorted(times))
        for e in MATCH['events']:
            self.assertIn(e['player_id'],ids)
            if e['recipient_id']:self.assertIn(e['recipient_id'],ids)
            self.assertEqual(e['evidence']['source'],'original synthetic frames and authored events')
            self.assertEqual(e['evidence']['frame_t_ms'],e['available_at_ms'])
            self.assertEqual(e['evidence']['observation_frame_t_ms'],e['observed_at_ms'])
            self.assertFalse(e['facts']['confirmed_goal'])
            self.assertTrue(e['narration']['essential'] and e['narration']['detailed'] and e['why'])
    def test_causal_confirmation_timing(self):
        frames={f['t_ms']:f for f in MATCH['frames']}
        for e in MATCH['events']:
            self.assertEqual(e['t_ms'],e['observed_at_ms'])
            self.assertLessEqual(e['observed_at_ms'],e['resolved_at_ms'])
            self.assertLessEqual(e['resolved_at_ms'],e['available_at_ms'])
            self.assertIn(e['available_at_ms'],frames)
            if e['kind'] == 'pass':
                self.assertGreater(e['available_at_ms'],e['t_ms'])
                receipt=frames[e['available_at_ms']]
                target=next(p for p in receipt['players'] if p['id']==e['recipient_id'])
                self.assertLess(dist(receipt['ball'],target),0.3)
        by_id={e['id']:e for e in MATCH['events']}
        self.assertEqual(by_id['E01']['available_at_ms'],10200)
        self.assertEqual(by_id['E02']['available_at_ms'],19400)
        self.assertEqual(by_id['E08']['available_at_ms'],61600)
        self.assertEqual(by_id['E10']['available_at_ms'],68800)

    def test_outcome(self):
        self.assertEqual((MATCH['result']['home_goals'],MATCH['result']['away_goals']),(0,0))
        self.assertEqual([e['kind'] for e in MATCH['events'] if e['priority']==4],['shot','save'])

if __name__=='__main__':unittest.main()
