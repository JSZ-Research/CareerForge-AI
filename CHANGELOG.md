# Changelog

## [v1.1] - 2026-01-21

### Security
- **Encrypted Secrets**: Added optional master-password encryption for API keys using AES (Fernet) + PBKDF2.
- **Injection Defense**: Added system prompts to treat User inputs (JD/Resume) as untrusted data.
- **Token Tracking**: Added session-based token usage display.

### Infrastructure
- **Multi-Profile**: Support for multiple user profiles via `profiles/` directory.
- **Robustness**: Improved JSON parsing for OpenAI (Structured Outputs) and Gemini (Regex fallback).
- **Dependencies**: Pinned versions in `requirements.txt` and added `cryptography`.

### UI/UX
- **Named Keys**: API keys can now have user-defined labels.
- **Export Control**: Checkboxes to select desired export formats.
- **Markdown Preview**: Improved preview rendering and added "Copy to Clipboard" raw view.
- **Editable Result**: Users can directly edit the generated text, and exports (PDF/Word) will automatically regenerate.
- **Status**: Added sidebar status for secrets lock state and session usage.

### Exports
- **Word**: Added bold styling for headers and bullet point support.
- **PDF**: Added support for custom Unicode fonts (if present in `assets/fonts/`) and improved margins.
- **LaTeX**: Improved escaping of special characters and formatting.
