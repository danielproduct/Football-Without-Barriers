"""Offline verification of Foundry batch exporter (does not call Microsoft)."""
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('insight_export', HERE / 'tools' / 'generate_foundry_insights.py')
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
fixture = json.loads((HERE / 'public' / 'data' / 'match.json').read_text())
by_id = {e['id']: e for e in fixture['events']}
players = {p['id']: p for p in fixture['players']}


class FoundryExportTests(unittest.TestCase):
    def test_endpoint_supports_services_foundry(self):
        url = 'https://fwb.services.ai.azure.com/openai/v1'
        self.assertEqual(mod.validate_endpoint(url), url + '/')

    def test_endpoint_rejects_secret_in_url(self):
        with self.assertRaises(ValueError):
            mod.validate_endpoint('https://service.services.ai.azure.com/openai/v1?api_key=secret')

    def test_endpoint_rejects_non_azure_host(self):
        with self.assertRaises(ValueError):
            mod.validate_endpoint('https://attacker.example/openai/v1')

    def test_request_has_only_confirmed_event_facts(self):
        p = mod.make_input(by_id['E01'], players)
        self.assertEqual(p['confirmed_at_ms'], 10200)
        self.assertEqual(p['observed_at_ms'], 9000)
        self.assertEqual(p['evidence_ids'], ['E01'])

    def test_accepts_grounded_output(self):
        raw = json.dumps({'event_id': 'E01', 'salience': 'normal', 'explanation': 'The completed pass moves play into central midfield while possession is maintained.', 'evidence_ids': ['E01']})
        obj = mod.validate_insight(raw, by_id['E01'], players)
        self.assertEqual(obj['available_at_ms'], 10200)
        self.assertFalse(obj['human_reviewed'])

    def test_rejects_future_score(self):
        raw = json.dumps({'event_id': 'E01', 'salience': 'high', 'explanation': 'This pass creates a goal for the team and sends them ahead.', 'evidence_ids': ['E01']})
        with self.assertRaises(ValueError):
            mod.validate_insight(raw, by_id['E01'], players)

    def test_rejects_other_player(self):
        raw = json.dumps({'event_id': 'E01', 'salience': 'high', 'explanation': 'The pass moves the ball to Taylor in the penalty area.', 'evidence_ids': ['E01']})
        with self.assertRaises(ValueError):
            mod.validate_insight(raw, by_id['E01'], players)

    def test_rejects_wrong_evidence(self):
        raw = json.dumps({'event_id': 'E01', 'salience': 'normal', 'explanation': 'The pass moves play forward into central midfield.', 'evidence_ids': ['E02']})
        with self.assertRaises(ValueError):
            mod.validate_insight(raw, by_id['E01'], players)

    def test_client_mock_run(self):
        class Response:
            output_text = json.dumps({'event_id': 'E01', 'salience': 'normal', 'explanation': 'The confirmed pass progresses play into midfield.', 'evidence_ids': ['E01']})
        class Completions:
            def create(self, **kwargs):
                self.kwargs = kwargs
                return Response()
        class Client:
            responses = Completions()
        client = Client()
        insight = mod.fetch_one(client, 'gpt-4.1-mini', by_id['E01'], players)
        self.assertEqual(insight['event_id'], 'E01')
        self.assertEqual(client.responses.kwargs['model'], 'gpt-4.1-mini')
        self.assertIn('10200', client.responses.kwargs['input'])

    def test_bundle_rejects_wrong_match(self):
        with self.assertRaises(ValueError):
            mod.validate_bundle({'source': 'microsoft_foundry_responses', 'synthetic': True, 'match_id': 'wrong', 'events': []}, fixture)


if __name__ == '__main__':
    unittest.main()
