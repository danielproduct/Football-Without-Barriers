# Put the build in your personal GitHub repository

Repository: https://github.com/danielproduct/Football-Without-Barriers

The original repository was found **public** with `main` and one short README. This ChatGPT connection had `pull=true`, `push=false`; no repository changes were made during preparation. This package is designed to replace the README and add all files at repository root.

## Option 1 — easiest on a computer (recommended)

1. Download and unzip `Football-Without-Barriers-build-pack.zip` from the handover answer.
2. Open the existing repository on GitHub or use a local Git clone:

```bash
git clone https://github.com/danielproduct/Football-Without-Barriers.git
cd Football-Without-Barriers
```

3. Copy **the contents** of the extracted `football-without-barriers` folder into the clone so that `index.html`, `app.js`, `styles.css`, `server.js`, `README.md`, `public`, `docs`, `tools`, `tests` sit at repository root. Do not copy or commit any `.env` file.
4. Review changes; verify none of your original work was unintentionally overwritten. The original repo currently only contains a short README. Run local tests.
5. Commit and push with your personal GitHub credentials:

```bash
git add .
git commit -m "Build synthetic accessible match POC"
git push origin main
```

6. Configure Settings > Pages > main > /(root). Wait for GitHub to confirm your actual public Pages URL.

## Option 2 — GitHub website upload

1. Open the repo, select **Add file > Upload files**.
2. Drag the project files and folders *from inside the extracted folder*; GitHub UI handling of nested folders can vary and may need a computer. Create each file with **Add file > Create new file** if necessary. Use a Git client for the simplest multi-file upload.
3. Commit to `main` from your personal GitHub account. Do not upload the ZIP alone: GitHub Pages needs `index.html` and the dependent files in the repository.

## Setup after push

- Visit `https://danielproduct.github.io/Football-Without-Barriers/` **only after** Pages reports deployment. The address is the likely URL pattern, not a verified live deployment today.
- Test Play, Seek to 00:56, Audio-first mode, Essential/Detail selection, spoken commentary, mobile layout.
- Remember GitHub Pages only serves the static demo. **The Foundry/Azure Speech server must be separately hosted and safely secured for the submission**; the default Pages UI will correctly show the AI button disabled.
