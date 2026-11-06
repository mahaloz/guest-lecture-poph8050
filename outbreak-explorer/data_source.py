"""Daily download cache with a versioned, verifiable offline fallback."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import requests
import streamlit as st
from core import CSV_URL, parse_data

DATA = Path(__file__).parent / "data"


@st.cache_data(ttl=86400, show_spinner="Loading APHIS-derived detection records…")
def load_data():
    cached = DATA / "latest.csv"
    metadata = DATA / "latest.metadata.json"
    if cached.exists() and metadata.exists():
        try:
            meta = json.loads(metadata.read_text())
            age = datetime.now(timezone.utc) - datetime.fromisoformat(meta["retrieved_at"])
            raw = cached.read_bytes()
            if age.total_seconds() < 86400 and hashlib.sha256(raw).hexdigest() == meta["sha256"]:
                return parse_data(raw), meta, "Local download cache", None
        except (ValueError, KeyError, OSError):
            pass
    try:
        response = requests.get(CSV_URL, timeout=(5, 15))
        response.raise_for_status()
        raw = response.content
        frame = parse_data(raw)
        meta = {"url": CSV_URL, "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "sha256": hashlib.sha256(raw).hexdigest()}
        try:
            tmp = DATA / "latest.csv.tmp"
            tmp.write_bytes(raw)
            tmp.replace(cached)
            metadata.write_text(json.dumps(meta, indent=2) + "\n")
        except OSError:
            pass  # In-memory cache still works on read-only installations.
        return frame, meta, "Downloaded source", None
    except (requests.RequestException, ValueError) as exc:
        for path in (cached, DATA / "poultry_detections.csv"):
            try:
                raw = path.read_bytes()
                meta = json.loads(path.with_suffix(".metadata.json").read_text())
                if hashlib.sha256(raw).hexdigest() != meta["sha256"]:
                    continue
                return parse_data(raw), meta, "Offline snapshot", str(exc)
            except (OSError, ValueError, KeyError):
                continue
        raise RuntimeError("Download failed and no verified local snapshot is available.") from exc
