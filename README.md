# Iden Playwright Challenge

## Description
This project uses a Python Playwright script to:
- reuse an existing session (or log in and save a new one),
- navigate the hidden challenge flow to the product table,
- extract all available product data with lazy-loading support,
- export results to `automation/data/products.json`.

## File Structure
- `automation/src/iden_extractor.py`
  Standalone entrypoint. Loads settings, creates browser context, runs extraction workflow, saves session/output.
- `automation/src/iden/config.py`
  Reads environment variables (`.env`) and builds runtime settings (URLs, credentials, timeouts, file paths).
- `automation/src/iden/pages/base_page.py`
  Base page object with shared helpers like smart waits and conditional clicks.
- `automation/src/iden/pages/login_page.py`
  Login/session page object. Reuses existing session when valid, otherwise performs sign-in.
- `automation/src/iden/pages/challenge_page.py`
  Challenge navigation page object. Handles wizard steps and lazy-loaded product extraction.
- `automation/src/iden/pages/submit_page.py`
  Optional page object for the “Submit Script” page.
- `automation/src/iden/workflows/extraction.py`
  Orchestration layer that connects login + challenge extraction flow.
- `automation/state/session.json`
  Persisted Playwright storage state used for session reuse.
- `automation/data/products.json`
  Final extracted product dataset in structured JSON format.
- `automation/requirements.txt`
  Python dependencies needed to run the project.
- `.env`
  Local secrets/config (credentials and base URL).

## Steps To Execute
1. Create and activate a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate
```
2. Install dependencies:
```bash
pip install -r automation/requirements.txt
python -m playwright install chromium
```
3. Ensure `.env` contains:
```env
IDEN_BASE_URL=https://hiring.idenhq.com/
IDEN_EMAIL=your-email@example.com
IDEN_PASSWORD=your-password
```
4. Run the script:
```bash
python automation/src/iden_extractor.py
```

## Output
- Product data JSON: `automation/data/products.json`
- Session state file: `automation/state/session.json`
