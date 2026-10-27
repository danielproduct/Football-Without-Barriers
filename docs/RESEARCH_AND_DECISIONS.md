# Sherlock evidence pack | Football Without Barriers

**Research checked:** 19 October 2026. **Decision:** generate wholly original football-realistic match data with publicly documented formats as references only. Do not import licensed footage or client assets.

## Why this idea

Problem: standard football broadcasts can fail to describe the spatial and off-ball actions a blind supporter needs to follow play. For partially sighted supporters, screen clutter and small player/ball details add friction. Relevant research includes RNIB work on football broadcast accessibility and Sky Sports' 2026 descriptive football commentary rollout (see below). These findings justify testing a more user-controlled format, **not** declaring the product accessible before supporter trials.

Proposed solution: a synthetic event stream becomes both a shape-coded animated pitch view and adjustable audio descriptions. Explanation and evidence must remain linked: if the data does not show a goal, the commentary cannot claim one.

## Public data references researched

| Reference | What it contains | Decision and caution |
|---|---|---|
| [Metrica Sports sample data](https://github.com/metrica-sports/sample-data) | Aligned event CSVs and team tracking; 105x68m pitch; positions normalized to 0..1 | **Schema reference only.** Public examples request attribution for public use; data licensing terms are not a blank cheque for redistribution. Do not copy into this repo. |
| [SkillCorner opendata](https://github.com/SkillCorner/opendata) | Tracking JSONL at ~10 Hz for selected A-League matches, possession and event CSVs; metre units, pitch-centred coordinates | **Schema reference only.** Repo includes an MIT LICENSE; confirm any separately stated dataset terms before reuse. Neither real match contents nor code are shipped here. |
| [StatsBomb open data](https://github.com/statsbomb/open-data) | Open football match events; some 360 frames for spatial context | Useful for event naming and spatial concepts, but ordinary event records do **not** give continuous 22-player tracking. Not needed for v0.1. |
| [Genius Sports / Second Spectrum](https://www.geniussports.com/second-spectrum/) | Commercial football tracking and analytics context | No verified free tracking feed/schema appropriate for this experiment; no dependency. Avoid PMY/BHA familiarity or vendor client data. |

## Official competition sources

- [Microsoft Premier League Hackathon Official Rules](https://github.com/microsoft/insidethegamehackathon/blob/main/OFFICIAL%20RULES.md) — new original projects, synthetic football-realistic data, five-step intelligence pipeline, judgeable app, public repo, <2-minute public demonstration video, IP and open source restrictions, deadline 27 Oct 23:59 US Pacific.
- [Official resource playlists](https://github.com/microsoft/insidethegamehackathon/blob/main/RESOURCE%20PLAYLISTS.md) — GitHub Copilot, Foundry, Foundry Agents, Agentic Workflows and data.
- [Microsoft code of conduct](https://www.microsoft.com/en-gb/events/code-of-conduct) — applies to participation, including respectful conduct.
- [Microsoft Reactor Inside the Game event series](https://developer.microsoft.com/en-us/reactor/series/S-1709/) — 14 October recording/event focused on Azure Kubernetes Service and Container Apps architecture. The supplied YouTube video was not reliably transcribed in this research. **Do not infer webinar-specific tips.**

## Microsoft platform and hosting references

- [Microsoft Foundry chat completions REST](https://learn.microsoft.com/en-us/azure/foundry/openai/latest) — documents `POST {endpoint}/openai/v1/chat/completions`. The built optional adapter uses this *chat-completions-compatible* resource endpoint (not the newer project-scoped Foundry Agent API). Actual deployment/API version/model availability must be tested.
- [Microsoft Foundry quickstarts](https://learn.microsoft.com/en-us/azure/foundry/quickstarts/quickstarts) — alternate agent, orchestration and hosted agent approaches if advancing beyond v0.1.
- [Microsoft Agent Framework getting started](https://github.com/microsoft/agent-framework/tree/main/python/samples/01-get-started) — agentic orchestration, if demonstrated and justified for v0.2.
- [Azure Speech REST text-to-speech](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-text-to-speech) — requires a region-specific Speech service resource and credentials; billing may apply. The SDK may be preferable for fine-grained streaming and word boundaries.
- [GitHub Pages publishing from a branch](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) — static `main` + `/(root)`; does not host private server endpoints.
- [RNIB](https://www.rnib.org.uk/) — stakeholder research and accessibility guidance; direct supporter testing remains necessary.

## Competitive positioning

Audio description alone is **not** novel. Sky Sports' expanded descriptive commentary in 2026 demonstrates progress by incumbents. Differentiate on user-controlled narrative density, event evidence, replayability and synchronized visual support across blindness/low vision. The pitch view is an optional companion, never a substitute for speech.

## Key decisions (explicit)

1. **Personal entry**, not PMY. Keep IP, accounts, Azure billing and code under the individual's ownership; no PMY, Brighton, Second Spectrum or other internal assets.
2. **Source truth:** fictional event script + interpolated 5Hz 22-player/ball tracking, 80 seconds. All output generated by `tools/generate_match.py`.
3. **Client:** zero-dependency responsive static HTML/CSS/JS. Publish static preview with GitHub Pages only when approved.
4. **Accessibility:** shape-coded high-contrast pitch, two presentation modes, essential/detailed descriptions, device TTS opt-in, explicit event evidence, keyboard-operable controls. Real user testing still required.
5. **AI:** Azure adapter scaffolded. **Not validated with an Azure model or account.** Offline text and device speech are not Microsoft AI services and must not be misrepresented as such.
6. **Costs:** no hosting spend or paid Microsoft resources committed. Review Azure spending cap, billing owner, and free credits/tiers in portal before enabling live services.
7. **Submission:** do not submit as an AI-powered solution until tested live Microsoft technology is genuinely present and demonstrable.

## Challenge and disconfirmation

- **Authenticity:** 80 seconds of fictional scripted events does not prove live accuracy, soccer realism over 90 minutes, human-level narration quality or latency.
- **Narration errors:** a language model can hallucinate; one basic rule filter is not a claim checker. v0.2 needs strict structured claims / evidence IDs and a reviewer agent or rules.
- **Timing:** events currently reflect some pre-known outcomes at event start; true streaming needs independent `start`, `resolution`, `evidence_confirmed` timestamps.
- **Accessibility:** without user testing, positive outcomes are only a hypothesis. Seek feedback from blind and partially sighted people; avoid representing one tester as the whole community.
- **Hosting:** GitHub Pages can demonstrate deterministic UI but cannot secure Foundry/Speech keys. A separately secured paid/limited backend is required for live AI.
- **Ownership:** consult your personal contract/terms before submission; do not assume work created outside working hours is automatically excluded from IP clauses.

**Sherlock confidence:** high on availability of public format documentation and rule requirements; medium on untested Azure adapter API fit; low on asserted usability until actual supporters test. **Vault:** no PMY Vault update, deliberately maintaining a personal boundary.
