# Football Without Barriers

**A personal Microsoft x Premier League Inside the Game hackathon project.**

An accessibility-first fictional football experience that combines a high-contrast live pitch simulation, adjustable descriptions and optional spoken narration. One consistent synthetic match stream drives everything on screen.

> **State of the build:** a **working offline POC**, with an **optional unverified Microsoft Foundry and Azure Speech integration**. The offline commentary is authored, not AI-generated. No real football matches, player identities, video, tracking, logos or club assets are included.

## Experience

- **Visual support:** 22 shape-coded players, ball movement, timeline, high-contrast field, narrated events.
- **Audio-first:** larger event description, optional device narration, same evidence trail.
- **Controls:** play/pause, restart, seek, half speed/normal/1.5x, essential/detailed descriptions, mute/unmute.
- **Evidence:** each described event links to timestamped original synthetic frames and event records; ball/player positions use a 105 x 68 metre pitch. Confirmed pass/shot outcomes are withheld until the corresponding sampled ball arrival or shot frame (causal replay gating).
- **Microsoft integration prepared:** local Node backend can use Microsoft Foundry's Azure OpenAI v1 chat completions endpoint for *AI rephrasing*, and Azure Speech's REST API for synthesised audio once personal Azure credentials are configured.

## Run locally for free

**Option A — zero setup:** open `index.html` in a current desktop browser. `public/data/match.js` embeds the generated fixture so no fetch request is necessary. Native speech is browser/OS-dependent; start or enable it with a click.

**Option B — local web server (Node.js 20 or later):**

```bash
node server.js
# Visit http://127.0.0.1:3000
```

**Optional data validation (Python 3):**

```bash
python3 tools/generate_match.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/server.test.js
```

## Microsoft Foundry and Azure Speech (optional, may incur charges)

1. Create a **personal** Azure subscription and Foundry model deployment only when you are ready to test live AI. Configure spending limits, a budget alert, keys, quotas, and use the lowest suitable model.
2. Copy `.env.example` to `.env` and fill in only your personal secrets. `.env` is in `.gitignore`. `FOUNDRY_BASE_URL` must be a **chat-completions-compatible** base such as `https://YOUR_RESOURCE.openai.azure.com/openai/v1`; `FOUNDRY_MODEL` is your deployment name. These settings **may differ** for newer project-scoped Foundry endpoints.
3. If you enable Azure Speech, set `AZURE_SPEECH_REGION` and `AZURE_SPEECH_KEY` from your personal Speech resource.
4. Run `node --env-file=.env server.js` (Node 20+). The UI enables **Ask Foundry to rephrase** and **Azure Speech** when the backend reports them configured. A configured switch does **not** guarantee working Azure access: a real end-to-end test is required.
5. **Never** put Azure keys in `app.js`, in GitHub Pages, in a committed `.env`, or in the ChatGPT conversation. If a secret is published, revoke it.

The server starts on `127.0.0.1` deliberately. **It is not production-hosted or hardened for public, anonymous API use.** A public backend needs identity/rate limits, logging, secret storage, hosting and costs reviewed first. GitHub Pages cannot run Node server code.

## Publish the static baseline on GitHub Pages

1. Upload the contents of this package into [danielproduct/Football-Without-Barriers](https://github.com/danielproduct/Football-Without-Barriers), keeping `index.html` at repository root. Replace the existing short README with this one if approved.
2. Open repository **Settings > Pages > Build and deployment**. Choose **Deploy from a branch**, branch `main`, folder `/(root)`, then save.
3. GitHub Pages will provide a public URL (normally under `https://danielproduct.github.io/Football-Without-Barriers/`). **Do not claim the URL is live until GitHub confirms deployment.** This baseline is offline/deterministic; it does not include hosted Foundry or Azure Speech integration.
4. Before submission, deploy and test the live Microsoft AI path or clearly explain the implemented Microsoft technology to judges. Do **not** submit the offline-only baseline as if it were a completed AI submission.

## Files

| Path | Role |
|---|---|
| `index.html`, `styles.css`, `app.js` | Static accessible visual and browser narration |
| `public/data/match.json` | Source data: fictional match, 401 frames, 22 players, 12 causally gated events |
| `public/data/match.js` | Same match as a globally loaded browser fixture |
| `tools/generate_match.py` | Source-of-truth synthetic data generator |
| `server.js` | Local Node host and optional secure server-side Azure API adapters |
| `tests/` | Data, truth-consistency and route smoke tests |
| `docs/` | Research, decisions, data contract, Azure guidance, pitch, validation report and personal handover |
| `previews/` | Captured desktop and mobile screenshots of the rendered offline POC |

**Research audit (19 Oct):** see `docs/RESEARCH_GAP_ANALYSIS_2026-10-19.md`. **Update (27 Oct):** the local v0.2 release candidate addresses the authored-replay causal timestamps and reduces duplicate aria-live announcements when optional device speech is on. Genuine agentic AI, Azure end-to-end verification, user testing and safe public hosting are **not** complete.

## Important limitations

- **Synthetic replay, not a real match or true live feed.** Although it uses frame-by-frame data and timestamps, it does not ingest events from a real broadcast or hardware.
- **Speech:** browser speech synthesis varies by browser and voice. Azure Speech integration has not been exercised with a real credential in this handover.
- **Evidence:** timestamps and coordinates are reproducible. Generated narration may still make unsupported claims; initial server-side guardrails are **not** a proof of factual accuracy.
- **Accessibility:** HTML labels, controls and shape coding are designed to help; an actual blind or partially sighted supporter must still test the experience before an accessibility claim is made.
- **Ownership:** all demonstration data is original and fictional. Separate personal project. No PMY, Brighton, Second Spectrum or proprietary source data was imported. Review any employment/IP clauses independently.
- **No third-party football media or code is bundled.** Metrica/SkillCorner datasets informed the public schema research only (links in `docs/RESEARCH_AND_DECISIONS.md`).

## Competition checklist

The official [Microsoft Premier League Hackathon rules](https://github.com/microsoft/insidethegamehackathon/blob/main/OFFICIAL%20RULES.md) specify: newly built project, synthetic football events, transparent/meaningful match intelligence, personalised fan experience; public GitHub repository; actual functioning demo accessible to judges; video **under 2 minutes**, publicly hosted; and project description including Microsoft/Azure technologies used. Deadline: **27 Oct 2026 23:59 Pacific = 28 Oct 2026 06:59 GMT**. Registration confirmed by project owner. Refer to `docs/SUBMISSION_CHECKLIST.md`.

**Owner:** the individual entrant, not PMY. Public source is not equivalent to permission to reuse proprietary code. See `docs/SEEDFILE.md` for decisions and next gates.
