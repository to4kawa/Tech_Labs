#!/usr/bin/env python3
"""Minimal probe for public models.dev metadata (no API key required)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import urlopen

ENDPOINTS = [
    "https://models.dev/api/models",
    "https://models.dev/models.json",
    "https://models.dev/api/v1/models",
]


def fetch_json(url: str):
    with urlopen(url, timeout=20) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def extract_records(data):
    records = []

    if isinstance(data, dict) and isinstance(data.get("models"), list):
        models = data["models"]
    elif isinstance(data, list):
        models = data
    elif isinstance(data, dict):
        models = []
        for provider, provider_models in data.items():
            if isinstance(provider_models, list):
                for m in provider_models:
                    if isinstance(m, dict):
                        m = {**m, "provider": m.get("provider", provider)}
                        models.append(m)
    else:
        models = []

    for model in models:
        if not isinstance(model, dict):
            continue

        pricing = model.get("pricing") or model.get("cost") or {}
        in_cost = (
            model.get("input_cost")
            or pricing.get("input")
            or pricing.get("prompt")
            or pricing.get("input_cost")
        )
        out_cost = (
            model.get("output_cost")
            or pricing.get("output")
            or pricing.get("completion")
            or pricing.get("output_cost")
        )

        records.append(
            {
                "provider": model.get("provider") or model.get("vendor") or "unknown",
                "model": model.get("model") or model.get("name") or model.get("id") or "unknown",
                "input_cost": in_cost,
                "output_cost": out_cost,
            }
        )

    return records


def main():
    ts = datetime.now(timezone.utc).isoformat()
    report = {
        "timestamp_utc": ts,
        "success": False,
        "endpoint": None,
        "record_count": 0,
        "sample": [],
        "error": None,
    }

    for endpoint in ENDPOINTS:
        try:
            data = fetch_json(endpoint)
            rows = extract_records(data)
            report.update(
                {
                    "success": True,
                    "endpoint": endpoint,
                    "record_count": len(rows),
                    "sample": rows[:10],
                }
            )
            break
        except (URLError, HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            report["error"] = f"{type(exc).__name__}: {exc}"

    out = Path(__file__).resolve().parents[1] / "logs" / "models_dev_latest.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if report["success"]:
        print(f"SUCCESS endpoint={report['endpoint']} records={report['record_count']}")
    else:
        print(f"FAILED endpoint_attempts={len(ENDPOINTS)} error={report['error']}")


if __name__ == "__main__":
    main()
