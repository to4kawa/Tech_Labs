# codexbar_api_probe

Small experiment to probe public `models.dev` metadata for CodexBar / multi-provider coding usage monitoring.

## Purpose
- Hit a public endpoint (no API key) on `models.dev`.
- Extract provider name, model name, and input/output cost fields when available.
- Save a machine-readable snapshot under `logs/`.

## Run
```bash
python codexbar_api_probe/scripts/test_models_dev.py
```

## Output
- `codexbar_api_probe/logs/models_dev_latest.json`
- `codexbar_api_probe/logs/api_test_log.md`
