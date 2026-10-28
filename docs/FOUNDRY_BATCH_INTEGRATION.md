# Microsoft Foundry batch integration — quick, low-exposure path

**Status:** Implementation prepared and offline-tested. No live Azure call has been executed by this code yet. The owner has tested a prompt in the Foundry Playground independently.

The public GitHub Pages website is static. This route lets us show *actual Microsoft Foundry-generated explanations* without placing credentials or a pay-per-use model endpoint on a publicly accessible page. It is **offline batch inference**, NOT live cloud AI on the website, and should be described accurately to judges.

## 1. Prepare a safe Python environment

In a personal Azure Cloud Shell terminal (Bash) or on a personal computer with Azure CLI signed in:

```bash
# If using your own computer, first run: az login
python3 -m pip install --user --upgrade openai azure-identity
# If the terminal is fresh, fetch the personal repository:
git clone https://github.com/danielproduct/Football-Without-Barriers.git
cd Football-Without-Barriers
```

The GitHub repository must include this exporter first. The script's only external authentication is Microsoft Entra ID through `DefaultAzureCredential`. **Do not paste any API keys or tokens into scripts, GitHub or ChatGPT.**

## 2. Generate one model insight (one billable inference call)

```bash
python3 tools/generate_foundry_insights.py \
  --endpoint "https://rg-football-without-barriers.services.ai.azure.com/openai/v1" \
  --model gpt-4.1-mini --event E01
```

- `E01` was observed at 9.0s and confirmed at 10.2s; the model only sees already-confirmed evidence.
- The exporter requests a one-sentence explanation and relative event salience.
- It checks event ID, evidence ID, a small set of unsupported claims, length, and unrelated player names. **These checks are not a full semantic verifier or user study**.
- Success writes `public/data/foundry_insights.json` with `source=microsoft_foundry_responses` and `generation_mode=offline_batch`.
- Your model returns **AI context only**. The baseline factual narration and spoken audio remain authored and linked to the synthetic event; we do not re-label them AI-generated.
- View the JSON and review the claim yourself before making it public.

If identity authentication fails, verify the Azure subscription, tenant, resource roles, and Azure CLI login. If the model rejects the request or deployment is unavailable, stop and use the Playground response; don't expose a key.

## 3. Validate without spending money

```bash
python3 tools/generate_foundry_insights.py --check-only
python3 -m unittest discover -s tests -p 'test_*.py' -v
npm test
```

An optional second run with `--all` makes **12 separate model requests**, which can incur usage charges. Don't do it just to prove a single inference works.

## 4. Publish the AI output after checking it

The owner can upload the generated `public/data/foundry_insights.json` file for review, or paste the resulting event explanation and show model provenance. Do not publish a raw secret or Azure token. Once reviewed and explicitly approved, commit only that JSON to the public repository and verify the web page displays **"Why it matters · Foundry batch"** on the relevant event.

The app loads this optional JSON through a same-origin static request. Missing or invalid assets leave the site fully usable with its original descriptions. This route never calls Foundry on a judge's behalf and incurs no model inference cost from web visitors.

## 5. Precise hackathon claims

Safe: "We used a personal Microsoft Foundry `gpt-4.1-mini` model through the Responses API to generate event interpretations; the outputs are checked against specific synthetic football events, then embedded in a static accessibility prototype."

Not safe: "AI narrates live matches", "an autonomous multi-agent system runs for each viewer", "outputs are fully fact-checked", "the website uses Azure Speech", or "we have completed accessibility user research". Those capabilities are not demonstrated here.

## Important constraints

- Any model inference may incur charges. Azure budget alerts are not a hard spending cap.
- GitHub Pages cannot securely execute a private key-backed API or run `server.js`.
- The existing `server.js` **still expects an API key** for its optional *local* Foundry adapter. This separate exporter uses keyless Microsoft Entra ID and the Responses API.
- Microsoft Foundry direct model inference and Foundry Agent Service are not equivalent; this workflow is **one model with deterministic validation**, not an agent-orchestration solution.
- No PMY data, licensed match footage or real club logos are used.

Official reference: https://learn.microsoft.com/en-us/azure/foundry/openai/api-version-lifecycle
