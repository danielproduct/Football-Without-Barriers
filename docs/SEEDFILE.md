# FOOTBALL WITHOUT BARRIERS — COMPLETE PERSONAL CHATGPT SEEDFILE

**Version:** 0.2 research-complete handover (v0.1 code), 19 October 2026

**Copy this entire document into a new chat in your personal ChatGPT account, upload the ZIP build pack, and say:**

> Continue this personal hackathon project from the attached completed v0.1 build pack. First inspect the ZIP and README, respect all research/decisions and verify the live GitHub repository. We need to push the prepared POC from my own personal GitHub connection, turn on GitHub Pages, connect one real Microsoft Foundry AI endpoint using my personal Azure account without exposing secrets, test accessibility and AI factual accuracy, deploy a judge-accessible final app, record a <2-minute demonstration and submit before the competition deadline. Work one small approved gate at a time. Do not restart research or claim features work until you validate them.

## 1. WHO / OWNERSHIP

Individual project by Daniel, NOT PMY work. Personal accounts are to be used for GitHub, Azure and hackathon submission. Do not use any PMY, Brighton, BHA, Second Spectrum, client code, footage, proprietary files, notebooks or private infrastructure. Do not copy anything from employer shared systems. Examine employment/IP contract if needed. Third-party public schemas can be cited, but all generated match data is original fictional data.

Personal GitHub repo: https://github.com/danielproduct/Football-Without-Barriers
- Public, default branch `main`.
- At research time only a 260-byte README existed.
- Source ChatGPT GitHub connector could read but not push to it. Personal ChatGPT account is already connected to Daniel's personal GitHub, so use that to publish **after permission**.

## 2. OBJECTIVE / PERSONAS

Working title: Football Without Barriers.

Problem: blind football supporters and partially sighted supporters may struggle to understand the spatial actions that standard broadcast coverage takes for granted.

Solution: a single stream of synthetic match events drives (a) audio-first, adjustable narration and (b) a simple high-contrast pitch with ball and player movement, timestamped explanations and evidence. This is NOT merely a generic commentator: prioritise user choice, evidence-linked explanations, clarity and synchronization.

Success hypothesis: a supporter can understand a key attack and its spatial context without needing to see real footage. This is **not validated** until supporters test it.

## 3. HACKATHON / MUST COMPLY

Official rules: https://github.com/microsoft/insidethegamehackathon/blob/main/OFFICIAL%20RULES.md
Resource playlists: https://github.com/microsoft/insidethegamehackathon/blob/main/RESOURCE%20PLAYLISTS.md
Code of conduct: https://www.microsoft.com/en-gb/events/code-of-conduct
Video provided by user: https://www.youtube.com/live/EQ187ohgCbo?si=w-NJb7rH2mOk0uSS

Registration CONFIRMED by Daniel. Entrant: individual. Requirement: new original AI project using synthetic football-realistic data, ingest → interpret → explain → render → personalise, functioning judge-accessible experience, public GitHub repository, actual working demo video under two minutes at public URL, clear description of Microsoft/Azure tech. Deadline **28 Oct 2026 at 06:59 GMT** (27 Oct 23:59 Pacific). Judges assess technology, agents, impact, UX, category fit (20% each). Entrant retains title but grants sponsor broad permanent worldwide royalty-free licence; review before submitting anything proprietary.

## 4. KEY RESEARCH FINDINGS (DON'T REDO)

Metrica Sports sample-data: https://github.com/metrica-sports/sample-data
- Public synchronised events and tracking in CSV; event headers `Team`, `Type`, `Subtype`, `Period`, `Start Frame`, `Start Time [s]`, `End Frame`, `End Time [s]`, `From`, `To`, `Start X/Y`, `End X/Y`. Coordinates 0..1 on 105m x68m pitch. Used *only to learn formatting*.

SkillCorner open data: https://github.com/SkillCorner/opendata
- Broadcast tracking JSONL (frame, timestamp, ball_data, possession, player_data x/y/player_id) and other event CSVs. Uses pitch-centred metres. Repo MIT licence; do not assume every dataset/image licensed identically. Used *only as structural reference*.

StatsBomb open data contains useful discrete events, but is not a 22-player full-frame tracker. Second Spectrum commercial tracking is not required, no confirmed free schema/source used. All bundled match/player data is original fictional simulation.

Sky Sports and RNIB work shows descriptive TV commentary already exists, so innovation must be in control, synchronized pitch, explanations, and appropriate accessibility.

Microsoft Foundry chat endpoint: https://learn.microsoft.com/en-us/azure/foundry/openai/latest
Azure Speech REST: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-text-to-speech
Microsoft Agent Framework: https://github.com/microsoft/agent-framework
GitHub Pages publishing: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

Detailed pack in `docs/RESEARCH_AND_DECISIONS.md`.

## 5. WHAT HAS ALREADY BEEN BUILT (DON'T REDO)

Completed **local offline v0.1 POC**, contained in ZIP:
- `index.html`, `styles.css`, `app.js` responsive, high-contrast desktop/mobile app.
- `tools/generate_match.py` deterministic original fictional simulation, outputs 80-second 5fps JSON and JS.
- `public/data/match.json`, `public/data/match.js`: 401 frames, 22 players, 12 events, ball, possession, descriptions, evidence refs.
- `server.js`: local Node 20 no-dependency static server with optional Microsoft Foundry chat-completions and Azure Speech REST adapters. Keys server-side via `.env`; `.env` ignored. No actual Azure credentials used, no live model/voice test yet. `server.js` listens on 127.0.0.1 by default. Public production backend and rate limits NOT ready.
- `tests/test_fixture.py`, `tests/server.test.js`: synthetic data continuity/metadata checks and Node offline route/security tests.
- `docs/`: contract, research, Azure steps, accessibility test plan, submission checklist, demo script, repo upload instructions, this seedfile.
- README has exact setup and scope/limitations.

**Critical honesty:** All initial commentary is authored/deterministic. Device `speechSynthesis` is not Microsoft AI. Optional Foundry adapter produces text rephrasing only if configured and called; output remains *unverified* and the static demo button is disabled. A real Microsoft AI integration is outstanding and required for the intended hackathon submission. Browser smoke tests were completed with Chromium Playwright using in-memory HTML injection because direct navigation was blocked by the research sandbox. Model and Speech live integrations have NOT been exercised or verified. No GitHub push, Pages deploy, Azure spend, demo video or final submission has happened.

## 6. HOW TO RUN

Unzip project directory. Open `index.html` for static preview. Or use Node 20:

```bash
node server.js
# http://127.0.0.1:3000
```

Regenerate/test data:

```bash
python3 tools/generate_match.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/server.test.js
```

For live Azure adapter, personal Azure subscription with budget alert is prerequisite. Copy `.env.example` to `.env`; configure valid Azure resource chat-completions v1 URL, deployment name and API key, plus optional Azure Speech region/key. Start with `node --env-file=.env server.js`. Never upload `.env` or keys to GitHub/ChatGPT. Verify API compatibility with actual Azure resource. Only then claim the AI function works.

## 7. DEMO / PRODUCT DESIGN

Fictional fixture **Rivergate vs Northbridge, 0–0** (not any real club/match). Sequence: home build-up → progressive passes → close-down → wide switch → runner through → shot → keeper save → away distribution. Full 80s, not an official match clock. Two user modes; essential vs detailed prose; optional speech opt-in. All player movement on 105 x 68m pitch uses static shape-coded teams.

Accessible claim is a hypothesis. Test with real blind/partially sighted supporters (VoiceOver/NVDA, browser/screen size; listenability, pace, sequence comprehension). A keyboard-operable pitch is not equivalent to certified WCAG compliance.

## 8. GATES STILL REQUIRED

GATE A (NEXT): In personal GitHub account, inspect ZIP, upload files into repo root, commit/push to `main`, activate GitHub Pages and confirm the **actual** publicly working static POC URL.

GATE B: Confirm personal Azure subscription and quota; establish one **real, tested** Foundry call with no leaked keys and measurable latency. At this stage, do not build a vast multi-agent backend unless minimal evidence path works.

GATE C: Speech, claim grounding and failover; consider explicit interpretation/narrator/checker roles only if true separate functioning agents, not arbitrary labels. Test known false claims and latency.

GATE D: Public deployment of fully working Microsoft AI demo with usage/rate limits/budget control; supporter-accessibility feedback; proper credit/licences.

GATE E: <2-minute actual screen-recorded public demo, final competition project page, GitHub URL, final submission before deadline.

## 9. NEXT MESSAGE FOR PERSONAL CHATGPT

'I've uploaded the ZIP from the previous account. Start at Gate A. Inspect the files and my GitHub repository, confirm differences, tell me exactly what you plan to commit, and ask me to approve the push. We will then turn on Pages and verify the public site. Keep all subsequent tasks small, ordered and directly actionable. Don't use PMY data or spend on Azure without checking with me.'

## 10. ADDITIONAL RESEARCH FINDINGS (19 OCT 2026)

The ZIP now includes `docs/RESEARCH_GAP_ANALYSIS_2026-10-19.md`. Read this **before** doing live-AI work. The most important audit findings are: (1) pass outcomes are visible too early in the authored replay and must be separated into observed and confirmed times before a live-stream claim; (2) the current one-click Foundry *rephrase* feature is not a proven agentic interpretation pipeline; (3) VoiceOver + built-in TTS could create duplicate announcements and shot/save speech may be interrupted; (4) Sky Sports announced 109 descriptive-audio Premier League matches per season, so personalisation and evidence are the differentiators; (5) RNIB synthetic-speech studies found emotional quality important in sport; (6) Azure budgets only warn and do **not** stop usage. None of these issues blocks publishing a truthfully labelled static offline prototype.

Do not spend more time searching for match schemas. Resolve the causal-event and real-AI gaps, then test with actual supporters. Sources and detailed priorities are in the added research document.

## 11. OPEN QUESTIONS TO RESOLVE ONLY WHEN THEY BLOCK

- Does Daniel have a personal Azure subscription and permission to deploy Foundry/Speech resources?
- Can personal GitHub connector push? What approval level/permission is available?
- What is the minimal secure public backend needed for judges, and within what agreed Azure budget?
- Can at least one target-supporter test be arranged before submission?
- Are there contractual IP restrictions on submitting a personal project developed with AI tools?

**No additional broad research is needed before Gate A; critical validation and the new research addendum still apply.** Preserve all existing code and decisions unless testing disproves them. If something differs in the user's personal repository, reconcile first rather than overwrite.
