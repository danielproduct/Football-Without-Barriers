# Microsoft service integration checklist (personal account only)

**Purpose:** add one real, testable Microsoft AI capability to an already-working synthetic replay. This document is a prepared integration path, **not evidence of successful live Azure integration**.

## Architecture

```
original fixture + events -> browser pitch map + baseline narration
                         \-> Node backend (server-side credentials)
                               |-> Microsoft Foundry chat-completions-compatible model
                               \-> Azure Speech TTS REST
```

The offline client is usable without Azure. The backend responds `/api/capabilities` and disables Azure buttons until the corresponding environment variables are set. `server.js` has an authored-content guard but **does not implement a rigorous factuality checker**.

## Personal Azure account setup

1. Log in to `https://portal.azure.com` with the individual's account. Confirm account ownership, subscription, spending limit/alert, region, quota. **Do not use PMY credentials or resources.**
2. Create/choose a Microsoft Foundry project or Azure OpenAI resource and deploy a chat-capable model. Use a low-cost model. In this prototype, the **chat completions-compatible resource** endpoint must end in `/openai/v1` (for example `https://MYRESOURCE.openai.azure.com/openai/v1`). Project-scoped Foundry agent URLs are a different API and require an adapter change.
3. Copy `.env.example` to `.env` and enter `FOUNDRY_BASE_URL`, `FOUNDRY_MODEL`, `FOUNDRY_API_KEY`. Do not share or commit `.env`.
4. Run `node --env-file=.env server.js`, open `http://127.0.0.1:3000`, choose an event, and click **Ask Foundry to rephrase this event**. Verify actual cloud response and cost. UI will label AI output as needing review.
5. To add Azure Speech, create a personal Speech resource in a supported region, obtain key + region, set `AZURE_SPEECH_REGION`, `AZURE_SPEECH_KEY`, and optionally `AZURE_SPEECH_VOICE`, restart. Choose Azure Speech voice in the UI and test both levels. The first demo can still use device TTS if the Azure voice feature is blocked, provided other real Microsoft AI work is correctly demonstrated.
6. Record measured p50/p95 time-to-text and time-to-audio over at least 20 requests; compare to the synthetic event frequency. Test failures (no network, timeouts, bad credentials) and ensure that essential baseline description still works.

## Key cautions

- API version, model name and permission requirements vary by resource type. Verify exact values in Azure portal documentation. This code uses the Azure OpenAI **v1 chat completions** convention. Supported model deployments can differ in `temperature`, `max_tokens` and accepted JSON output formats; adapt if required.
- Azure Speech REST works for simple TTS; for actual stream synchronization and word boundary callbacks, investigate the **Speech SDK**. This POC has browser speech as a free fallback.
- `server.js` binds to localhost. For a real publicly judgeable deployment, choose a secure managed host, implement authentication or per-IP request caps, service key vault/environment secrets, budget guardrails and logging. Do not expose an unrestricted key-backed narration endpoint.
- GitHub Pages hosts only the **offline static** UI. It cannot run the server-side Foundry/Speech code.
- The raw model output is labelled unverified; prohibit asserting that a rule filter proves facts. Future structure: fact extractor → event state → narrating agent → verifier → presentation.

## Relevant official documentation

- Microsoft Foundry chat completions: https://learn.microsoft.com/en-us/azure/foundry/openai/latest
- Foundry quickstarts: https://learn.microsoft.com/en-us/azure/foundry/quickstarts/quickstarts
- Microsoft Agent Framework Python: https://github.com/microsoft/agent-framework/tree/main/python/samples/01-get-started
- Azure Speech REST: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-text-to-speech

## Suggested v0.2 agent workflow (not currently built)

**Agent A: Moment interpreter** receives stream-confirmed events and produces a limited list of JSON claim objects with frame/evidence IDs. **Agent B: Audience narrator** uses only accepted claims to produce two versions: essential and detailed; **Verifier** rejects unsupported player names, scores, outcomes or timing. Both are evaluated against the same original event stream. This may demonstrate purposeful specialist agents if they truly run and hand off; simply naming deterministic functions 'agents' is not enough.
