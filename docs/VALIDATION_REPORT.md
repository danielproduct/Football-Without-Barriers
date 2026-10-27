# Build validation report | 19 October 2026

## Verification completed in source work account

| Area | Check | Result |
|---|---|---|
| Generator | Original 80-second 5fps source reproducibly emits 401 frames, 22 players, 12 events | PASS |
| Physics | All pitch positions bounded, source/recipient aligned at known pass windows, no teleporting players/ball at 5Hz | PASS (synthetic constraints only) |
| Event evidence | Player IDs, event IDs, chronological order, no confirmed goals, documented sources | PASS |
| Offline API | Local Node capabilities, health, no Azure functionality claimed without config, static-file allowlist | PASS |
| Security guard | Mocked Azure API keys stay in server request, unsafe score/goal output patterns blocked, XML escaped | PASS (not comprehensive security audit) |
| Azure adapter | Mocked Foundry chat-completions request and Azure Speech SSML request | PASS (MOCK ONLY) |
| Desktop browser | Chromium Playwright: initial load, 22 markers, seek, four completed passes at 00:60, descriptions, mode switching, event jump, play/pause | PASS |
| Mobile browser viewport | Chromium Playwright 390 x 844: same state/interaction tests, no JS console errors | PASS |
| Preview screenshots | `previews/desktop.png`, `previews/mobile.png` | CREATED |

Automated test summary: **6 Python tests + 7 Node tests + desktop and mobile browser interactions passed**. Direct Chromium navigation to localhost/file URIs was blocked by the research runner's browser administrator policy; browser JS validation used injected source in an `about:blank` page. The Node HTTP service health response was separately observed, but a real end-user browser test on the deployed URL is outstanding.

## Not tested / not to claim

- No personal Azure credentials, no actual Foundry model inference, no actual Azure Speech API call. These integrations are scaffolded and mock-tested only.
- No publicly hosted live app, no deployed GitHub Pages, no real cloud request cost measurement.
- No test on iOS Safari, VoiceOver, NVDA, TalkBack or with a blind/partially sighted football supporter.
- No performance/latency benchmark across a full real match.
- No external security review; do not host this Node backend publicly without authentication/rate limits and spending controls.
- No guarantee that output from an AI model remains factual; guardrails are only a smoke filter.

## Release gate

Approved only as **original synthetic offline POC v0.1**, prepared for personal GitHub import and the next live Azure and accessibility test gates. Not yet submission-ready.
