# Copilot Instructions

## Build, run, test
- Setup venv/deps: `./setup.sh` (creates `venv/` and `run.sh`).
- Run app (macOS): `./start_app.command` (clears quarantine flags, runs setup if needed).
- Run app (manual): `source venv/bin/activate && streamlit run app.py` (or `./run.sh` after setup).
- Run all tests: `python3 -m unittest`.
- Run a single test file: `python3 -m unittest tests/test_basics.py`.
- Run a single test: `python3 -m unittest tests.test_basics.TestBasics.test_json_cleanup`.
- No lint config found in the repo.

## High-level architecture
- `app.py` is the Streamlit UI; it owns session state and calls helpers to generate letters and refresh exports.
- `utils.py` implements the OpenAI/Gemini generation pipeline (extract skills/HR info, match CV, draft) and PDF text extraction.
- `secrets_utils.py` manages API keys in `secrets_store.json`, supports optional encryption, and merges env overrides (`OPENAI_API_KEY`, `GEMINI_API_KEY`).
- `profile_utils.py` stores profiles as JSON files in `profiles/` and migrates from `my_profile.json` if present.
- `export_utils.py` renders DOCX/PDF/LaTeX exports used by the UI and by `tests/test_verify_exports.py`.

## Key conventions
- Provider names: UI uses `OpenAI` / `Google Gemini`, but `utils.generate_cover_letter` expects `OpenAI` or `Gemini`.
- Session state keys (e.g., `cover_letter_content`, `docx_data`, `pdf_data`, `latex_data`, `gen_metadata`, `export_formats`) are shared across tabs; keep them in sync when editing.
- `profiles/` contains `{ProfileName}.json`; if empty, a `Default` profile is assumed.
- `secrets_store.json` can be encrypted (versioned dict) or legacy plain; use `secrets_utils` helpers to preserve compatibility.
- Export formatting assumes Markdown-style `**bold**` in DOCX/LaTeX; PDF export is plain text with unicode fallback.
