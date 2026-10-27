# Sherlock follow-up: What research still changes the hackathon build?

Checked: 19 October 2026. Project: Football Without Barriers, entirely personal; not PMY. Findings below are from official public sources plus a read-only inspection of the v0.1 local prototype. No credentials, client assets or licensed match data used.

## Executive assessment

There is little reason to continue searching for football datasets or Second Spectrum schemas. Original synthetic match data is already sufficient for the demonstration. The remaining research is about accessibility, believable narration, honest real-time claims, meaningful Microsoft AI use and safe deployment. **The strongest next step is applied validation, not another generic information search.**

## 1. Market challenge: audio description alone is not differentiated

- Sky Sports/Guinness publicly announced descriptive audio commentary across approximately 109 Premier League matches per season starting October 2026, and subtitles on main-channel matches. This is a direct incumbent comparison; it proves neither that all blind supporters have access nor that our proposed alternative is superior.
- Evidence: https://www.diageo.com/en/news-and-media/press-releases/2026/sky-media-and-guinness-launch-sky-sports-biggest-expansion
- Implication: never pitch this as the first live descriptive football commentary. Position the innovation as **user-controlled depth, evidence transparency, replayability, visual support and event selection**. Test whether these features add genuine value versus radio or a human descriptive commentator.

## 2. User research: narration is more than correct facts

- RNIB's October 2023 football broadcasting study interviewed 10 blind and partially sighted participants; they often preferred radio and reported television commentary lacked enough description to accurately follow play. The small qualitative sample is useful but not representative of all supporters.
- RNIB's 2025 research on synthetic speech found that participants particularly wanted human-like emotion for sports and drama; clarity alone was not always enough.
- RNIB's June 2026 guidance emphasises context, atmosphere, emotion and pace alongside descriptions of play.
- Evidence: https://www.rnib.org.uk/professionals/research-and-data/reports-and-insight/accessibility-of-football-broadcasts-on-tv-research-report/
- https://www.rnib.org.uk/professionals/research-and-data/reports-and-insight/rnib-study-report-synthetic-speech-for-audio-description/
- https://www.rnib.org.uk/news/making-sport-more-accessible-from-broadcast-to-live-experience/
- Implication: present essential/detailed choices, but also test **emotion, natural pacing, crowd sound interaction, and whether users actually prefer it to radio**. Do not claim accessible quality from UI screenshot inspection.

## 3. Critical technical defect: knowledge of future outcomes

Inspection of `tools/generate_match.py` and `app.js` reveals the synthetic pass event `E01` occurs at 9.0 seconds and is labelled `complete` even though the ball's recorded passage ends at 10.2 seconds. Similar pattern applies to other passes. The current engine can therefore narrate a completed pass before receipt has happened. This is fine as an authored replay, **not** as evidence of causal live intelligence.

Recommended minimal data-contract change before claiming live event ingestion:

- `observed_at_ms`: start of the play, e.g. 9000.
- `resolved_at_ms`: completion/outcome observed, e.g. 10200.
- `available_at_ms`: earliest point the narration system is permitted to use this fact.
- `status`: provisional, confirmed or unknown.
- `evidence_ids`: source tracking frame/event IDs supporting the claim.
- `confidence`: bounded score or `not_applicable` where no model estimation is used; never invent certainty.

Test: at t=9.0 the engine may say "Hart plays it towards Imani"; it cannot yet say "completed pass." At t=10.2 the completion may be confirmed and described. For shots and goals, never announce a goal without a distinct confirmation event.

## 4. The AI/judging gap

The official rules require a five-step pipeline: ingest, interpret, explain, render and personalise. Stage-two scores five criteria at 20% each, including **agentic design and innovation**.

Current code: offline descriptions are authored; `POST /api/narrate` optionally asks a Foundry-compatible chat model to rephrase one prewritten event. This is neither an autonomous interpretation pipeline nor a demonstrated orchestrated agent workflow. The Azure path has only mock tests.

Recommendation: once a *real* model call works, implement a **small explainable chain** rather than a decorative multi-agent system:

1. Ingest synthetic events with causal confirmation timestamps.
2. Interpret a validated structured event and supporting player/ball coordinates; choose meaningful moments and a priority.
3. Generate an **evidence-linked** description at the user's level of detail.
4. Verify all factual claims using deterministic schema checks, event IDs and constraints. Reject unsupported names/scores/outcomes; don't rely on the current regex-only filter.
5. Render as timestamped text and speech (with a fallback), and adapt to user preference.

If two genuine agents are adopted (narrator and independent reviewer), their distinct outputs, failure paths and handoffs should be auditable and their added latency measured. Do **not** call the current single button a multi-agent system. Microsoft Agent Framework supports workflows, but has not been deployed in this POC.

- Rules: https://github.com/microsoft/insidethegamehackathon/blob/main/OFFICIAL%20RULES.md
- Framework: https://learn.microsoft.com/en-us/agent-framework/
- Examples: https://github.com/microsoft/agent-framework/tree/main/python/samples/01-get-started

## 5. Accessibility and audio interruption gap

The browser presently sets `aria-live="polite"` on commentary and also offers device text-to-speech. With a screen reader enabled, that can lead to double announcements. More importantly, the engine cancels current speech when the next event arrives: the one-second gap between the shot (61 seconds) and the save (62 seconds) is a stress test. A supporter must not lose the shot description or hear a misleading delayed goal claim.

Research-backed guidance: user-selectable description, appropriate pacing, audio controls and accessible alternatives are recommended by W3C. However, prerecorded WCAG media techniques do not themselves certify this live-style app.

- https://www.w3.org/WAI/WCAG22/Techniques/general/G78
- https://www.w3.org/WAI/media/av/planning/
- https://www.w3.org/WAI/media/av/description/

Recommended tests: VoiceOver + browser speech on an iPhone; NVDA + Chrome on Windows; real audio timing at 61/62 seconds; keyboard focus; zoom and colour-independent player differentiation; muted narration and replay. A text-only fallback must tell the same factual story.

## 6. Latency and Microsoft technology

Microsoft documents Speech SDK measurement of first-byte, full-synthesis and network latency, as well as streaming text-to-speech approaches. Existing code uses Azure Speech REST to request the entire clip before playback; adequate for a small demo, not evidence of true live performance. Test actual end-to-end time from confirmed event -> AI text -> audio first audible byte; record p50/p95 and failure cases. A provisional internal success target of p95 <=2 seconds is **not a Microsoft SLA** and remains unverified.

- https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-lower-speech-synthesis-latency
- https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-text-to-speech

Use priority-based narrative interruptions: shot, save, goal confirmation and possession turnover may override routine passes, but messages shouldn't be silently lost. Presynthesised audio is fine for *replay*, never describe it as live LLM inference.

## 7. Azure costs: crucial clarification

Microsoft says the Foundry portal/platform can be explored at no charge but model/features usage incurs charges, and a subscription is required to build agents. Azure Speech offers a Free F0 tier with quotas subject to service availability and quota checks; it is not synonymous with unlimited free use. Most importantly, **Azure budgets/alerts do not stop resources or consumption** when the threshold is exceeded. Treat alerts as notification, not a hard cap; use a small chosen quota/low-cost model, optional manual shutdown, rate limiting and server-side credentials.

- https://azure.microsoft.com/en-us/pricing/details/microsoft-foundry/
- https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-services-quotas-and-limits
- https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets

An anonymously callable public AI API without limits creates a potential cost and abuse exposure. GitHub Pages is static only; it cannot hold secrets or serve Node backend routes. Hosting choice is **unresolved** until a personal Azure subscription and budget are verified.

## 8. Fast, falsifiable user test (not a research claim)

Using an actual blind or partially sighted supporter, let them first follow an 80-second passage without seeing the screen. Ask after a single listen: who had possession, which area play moved towards, what opened the chance, whether a shot was taken and whether a goal was scored. Collect wrong answers and confusion points. Then replay with detailed narration and ask about comprehension, enjoyment, timing, verbosity and control. For a low-vision tester also test ball discovery and team separation on their real device. Include a radio-style commentary as a comparator if possible.

These are formative sessions, not proof of population-wide accessibility. With only eight or nine days until submission, one or two real sessions are more valuable than extensive additional desk research.

## Recommended priority order as of 19 October

| Priority | Next validation | Why it matters | Gate |
|---|---|---|---|
| P0 | Confirm personal Azure subscription/budget and whether one actual model can be deployed | AI implementation/eligibility | Before public AI demo |
| P0 | Fix event outcome availability times; test the 9.0-to-10.2 pass and shot/save | No invented future facts | Before describing as event intelligence |
| P0 | Validate one event -> genuine Foundry reasoning -> checked output | Current app is only deterministic + manual rephrase | Before submission |
| P1 | Speech overlap and actual device/screen-reader tests | Primary user value could fail | Before accessibility claim |
| P1 | Public backend security/cost controls and real deployment | Judges need access | Before final video |
| P1 | Direct blind/low-vision supporter feedback; radio comparison | Real-world impact evidence | Before final pitch if feasible |
| P2 | More datasets, production tracking, multilingual support, 90-minute simulation | Not needed to prove current hypothesis | Defer |

## Status and source provenance

Evidence strength: high for official rules, public competitor announcement and Microsoft/W3C/RNIB documents; medium for preferred technical path; no genuine usability or Azure runtime measurements yet. No source supports claiming production readiness or validated supporter benefit.

The existing source package is not being automatically modified by this research note. This is an audit and ordered validation brief, not a confirmation that these defects have already been resolved.

**Vault boundary:** This is personal-project intelligence only. Do not write it into PMY's shared Vault.
