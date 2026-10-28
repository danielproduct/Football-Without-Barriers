"""Export evidence-linked AI insights from *personal* Microsoft Foundry.

Use in Azure Cloud Shell or an authenticated local environment. Model access incurs usage.
No API keys/tokens are written into exported files or source control.

The output is an *offline batch*, not a live hosted AI service. The source
synthetic fixture and authored play descriptions remain authoritative.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'public' / 'data' / 'match.json'
DEFAULT_OUTPUT = ROOT / 'public' / 'data' / 'foundry_insights.json'
SCOPE = 'https://ai.azure.com/.default'
SYSTEM_PROMPT = '''You are an accessibility-oriented football moment interpreter.
You are given ONE synthetic football event and trusted event-specific narration.
Return ONLY a JSON object with exactly these keys:
  event_id (copy the exact event ID),
  salience (one of: low, normal, high),
  explanation (one short sentence, maximum 160 characters, explaining the
               tactical relevance using ONLY the verified evidence),
  evidence_ids (array with ONLY the provided event ID).
Rules: Do not mention scores, goals, penalties, fouls or real teams. Do not
invent players, possession changes, times, outcomes, defensive intent,
statistics, or tactics unsupported by the supplied event. Do not imply
prediction or real-time inference. Do not include markdown or surrounding prose.
If the event is a pressure event, do not claim a possession turnover.
If the event is a shot, do not claim a goal. Keep your wording plain, concrete,
neutral and suitable for blind or partially sighted fans.'''

FORBIDDEN = re.compile(r'\b(?:goal|scores?|scor(?:ed|ing)|penalt(?:y|ies)|offside|fouls?|var|red card|premier league|hat trick)\b', re.I)
SCORELINE = re.compile(r'\b\d+\s*[-:]\s*\d+\b')


def validate_endpoint(endpoint: str) -> str:
    parsed = urlsplit(endpoint.strip())
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('Foundry endpoint must be a plain HTTPS URL without credentials or query strings')
    if not parsed.hostname.endswith(('.services.ai.azure.com', '.openai.azure.com')):
        raise ValueError('Expected a Microsoft Foundry or Azure OpenAI endpoint host')
    if parsed.path.rstrip('/') != '/openai/v1':
        raise ValueError('The endpoint must end with /openai/v1')
    return endpoint.rstrip('/') + '/'


def make_input(event: dict, players: dict[str, dict]) -> dict:
    names = {}
    for key in ('player_id', 'recipient_id'):
        pid = event.get(key)
        if pid:
            names[key] = players[pid]['name']
    return {
        'event_id': event['id'],
        'observed_at_ms': event['observed_at_ms'],
        'confirmed_at_ms': event['available_at_ms'],
        'status': 'confirmed' if event['available_at_ms'] >= event['observed_at_ms'] else 'unknown',
        'kind': event['kind'],
        'outcome': event['outcome'],
        'player_names': names,
        'narration_essential': event['narration']['essential'],
        'narration_detailed': event['narration']['detailed'],
        'authored_reason': event['why'],
        'evidence_ids': [event['id']],
    }


def validate_insight(raw: str, event: dict, players: dict[str, dict]) -> dict:
    try:
        obj = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise ValueError('Model did not return a JSON object') from exc
    if not isinstance(obj, dict) or set(obj) != {'event_id', 'salience', 'explanation', 'evidence_ids'}:
        raise ValueError('Unexpected AI output schema')
    if obj['event_id'] != event['id'] or obj['evidence_ids'] != [event['id']]:
        raise ValueError('Event/evidence mismatch')
    if obj['salience'] not in ('low', 'normal', 'high'):
        raise ValueError('Unsupported salience')
    explanation = obj['explanation']
    if not isinstance(explanation, str) or not (12 <= len(explanation) <= 160):
        raise ValueError('Invalid explanation length')
    if '\n' in explanation or '<' in explanation or '>' in explanation or FORBIDDEN.search(explanation) or SCORELINE.search(explanation):
        raise ValueError('Potential unsupported claim or markup')
    # Guard against naming a different fictional player. This is not a complete
    # semantic fact checker, so we never label this output factually verified.
    allowed = {players[event['player_id']]['name'].casefold()}
    if event.get('recipient_id'):
        allowed.add(players[event['recipient_id']]['name'].casefold())
    for player in players.values():
        name = player['name'].casefold()
        if name not in allowed and re.search(r'\b' + re.escape(name) + r'\b', explanation.casefold()):
            raise ValueError('Unsupported player named in explanation')
    return {
        'event_id': event['id'],
        'available_at_ms': event['available_at_ms'],
        'salience': obj['salience'],
        'explanation': explanation.strip(),
        'evidence_ids': [event['id']],
        'automated_checks_passed': True,
        'human_reviewed': False,
    }


def validate_bundle(bundle: dict, fixture: dict) -> None:
    if bundle.get('source') != 'microsoft_foundry_responses' or bundle.get('synthetic') is not True:
        raise ValueError('Bad bundle source')
    if bundle.get('match_id') != fixture['match_id']:
        raise ValueError('Wrong match fixture')
    if not isinstance(bundle.get('events'), list):
        raise ValueError('Events missing')
    by_id = {e['id']: e for e in fixture['events']}
    seen = set()
    for insight in bundle['events']:
        eid = insight.get('event_id')
        if eid not in by_id or eid in seen:
            raise ValueError('Missing or duplicate event ID')
        seen.add(eid)
        if insight.get('evidence_ids') != [eid] or insight.get('available_at_ms') != by_id[eid]['available_at_ms']:
            raise ValueError('Evidence or timestamp mismatch')
        if not insight.get('automated_checks_passed') or insight.get('human_reviewed') is not False:
            raise ValueError('Invalid review status')
        if not isinstance(insight.get('explanation'), str) or FORBIDDEN.search(insight['explanation']):
            raise ValueError('Invalid explanation')


def fetch_one(client, model: str, event: dict, players: dict[str, dict]) -> dict:
    response = client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=json.dumps(make_input(event, players), separators=(',', ':')),
        max_output_tokens=180,
    )
    return validate_insight(response.output_text, event, players)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--endpoint', default=os.environ.get('FOUNDRY_BASE_URL', ''), help='Azure model endpoint ending /openai/v1 (NOT an API key)')
    parser.add_argument('--model', default=os.environ.get('FOUNDRY_MODEL', 'gpt-4.1-mini'))
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument('--event', default='E01', help='Single event (default E01)')
    selection.add_argument('--all', action='store_true', help='Generate all 12 events (12 model requests)')
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--check-only', action='store_true', help='Validate an existing output with zero Azure calls')
    args = parser.parse_args(argv)
    fixture = json.loads(SOURCE.read_text(encoding='utf-8'))
    if args.check_only:
        bundle = json.loads(args.output.read_text(encoding='utf-8'))
        validate_bundle(bundle, fixture)
        print(f"VALID: {len(bundle['events'])} pre-generated, automatically checked Foundry insights")
        return 0
    endpoint = validate_endpoint(args.endpoint)
    if not re.fullmatch(r'[a-zA-Z0-9_.-]{1,80}', args.model):
        parser.error('Invalid deployment name')
    players = {p['id']: p for p in fixture['players']}
    events = fixture['events'] if args.all else [e for e in fixture['events'] if e['id'] == args.event]
    if not events:
        parser.error('Unknown event ID')
    try:
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        from openai import OpenAI
    except ImportError as e:
        parser.error('Install dependencies: python -m pip install openai azure-identity')
    token_provider = get_bearer_token_provider(DefaultAzureCredential(), SCOPE)
    client = OpenAI(base_url=endpoint, api_key=token_provider, timeout=25, max_retries=1)
    entries = []
    for event in events:
        insight = fetch_one(client, args.model, event, players)
        entries.append(insight)
        print(f"{event['id']}: {insight['salience'].upper()} | {insight['explanation']}")
    bundle = {
        'schema_version': '1',
        'source': 'microsoft_foundry_responses',
        'synthetic': True,
        'generation_mode': 'offline_batch',
        'model_deployment': args.model,
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'match_id': fixture['match_id'],
        'review_note': 'Automated validation only; factual human review not yet completed. This is NOT live AI inference.',
        'events': entries,
    }
    validate_bundle(bundle, fixture)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"Wrote {args.output} ({len(entries)} events). No tokens or keys stored.")
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except ValueError as e:
        print(f'Foundry output rejected: {e}', file=sys.stderr)
        raise SystemExit(1)
