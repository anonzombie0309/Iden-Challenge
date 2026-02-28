# Iden Playwright Challenge

## Description
This project uses a Python Playwright script to:
- reuse an existing session (or log in and save a new one),
- navigate the hidden challenge flow to the product table,
- extract all available product data with lazy-loading support,
- export results to `data/products.json`.

## File Structure
- `src/iden_extractor.py`
  Standalone entrypoint. Loads settings, creates browser context, runs extraction workflow, saves session/output.
- `src/iden/config.py`
  Reads environment variables (`.env`) and builds runtime settings (URLs, credentials, timeouts, file paths).
- `src/iden/pages/base_page.py`
  Base page object with shared helpers like smart waits and conditional clicks.
- `src/iden/pages/login_page.py`
  Login/session page object. Reuses existing session when valid, otherwise performs sign-in.
- `src/iden/pages/challenge_page.py`
  Challenge navigation page object. Handles wizard steps and lazy-loaded product extraction.
- `src/iden/pages/submit_page.py`
  Optional page object for the “Submit Script” page.
- `src/iden/workflows/extraction.py`
  Orchestration layer that connects login + challenge extraction flow.
- `state/session.json`
  Persisted Playwright storage state used for session reuse.
- `data/products.json`
  Final extracted product dataset in structured JSON format.
- `requirements.txt`
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
pip install -r requirements.txt
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
python /src/iden_extractor.py
```

## Output
- Product data JSON: `/data/products.json`
- Session state file: `/state/session.json`
