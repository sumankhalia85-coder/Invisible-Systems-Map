from fastapi import FastAPI, HTTPException  # type: ignore[import-not-found]
from fastapi.middleware.cors import CORSMiddleware  # type: ignore[import-not-found]
from pydantic import BaseModel  # type: ignore[import-not-found]
import json
import os
import openai  # type: ignore[import-not-found]
import requests  # type: ignore[import-not-found]
import time
from dotenv import load_dotenv  # type: ignore[import-not-found]
from typing import Optional
from datetime import datetime, timedelta
import subprocess
import sys
from apscheduler.schedulers.background import BackgroundScheduler # type: ignore
from contextlib import asynccontextmanager

load_dotenv()

# ── GDELT in-memory cache ────────────────────────────────────
_gdelt_cache: dict = {"data": [], "fetched_at": None}

# Background job to run the pipeline
def run_conflict_pipeline():
    print(f"[{datetime.utcnow()}] Running background conflict data ingestion pipeline...")
    script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'fetch_conflicts.py')
    try:
        subprocess.run([sys.executable, script_path], check=True)
        # Reload cache globally
        global conflicts_data
        conflicts_data = load_json('conflicts.json')
        _gdelt_cache["fetched_at"] = datetime.utcnow()
        print("✅ Background pipeline completed successfully.")
    except Exception as e:
        print(f"❌ Background pipeline failed: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: start the background scheduler
    scheduler = BackgroundScheduler()
    # Run every 30 minutes
    scheduler.add_job(run_conflict_pipeline, 'interval', minutes=30)
    scheduler.start()
    
    # Run once at startup
    run_conflict_pipeline()
    
    yield
    # Shutdown: cleanly shut down the scheduler
    scheduler.shutdown()

app = FastAPI(title="Invisible Systems Map API", version="2.0.0", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Data paths ──────────────────────────────────────────────
# main.py is at backend/app/ → go up 1 dir to backend/ → datasets/datasets/
# JSON files live inside the nested datasets/datasets/ structure
DATASETS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datasets', 'datasets')
)

def load_json(filename):
    path = os.path.join(DATASETS_DIR, filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load {path}: {e}")
        return []

nodes_data = load_json('nodes.json')
connections_data = load_json('connections.json')
conflicts_data = load_json('conflicts.json')

print(f"✅ Loaded: {len(nodes_data)} nodes, {len(connections_data)} connections, {len(conflicts_data)} conflict events")
print(f"   DATASETS_DIR = {DATASETS_DIR}")

GDELT_CACHE_TTL_SECONDS = 3600  # 1 hour

EVENT_TYPE_MAP = {
    "battle": "battle", "conflict": "battle", "war": "battle",
    "airstrike": "airstrike", "air strike": "airstrike", "bombing": "airstrike",
    "missile": "missile", "rocket": "missile",
    "drone": "airstrike", "explosion": "bombing",
    "protest": "protest", "demonstration": "protest",
    "riot": "riot", "unrest": "riot",
    "tension": "geopolitical", "sanction": "geopolitical",
}

def parse_gdelt_event_type(title: str) -> str:
    title_lower = title.lower()
    for kw, evt in EVENT_TYPE_MAP.items():
        if kw in title_lower:
            return evt
    return "geopolitical"

def fetch_gdelt_live() -> list:
    """Return conflict events from the local pre-fetched dataset, bypassing rate-limited APIs."""
    # Always read fresh from disk so background pipeline updates are immediately visible!
    return load_json('conflicts.json')


# ══════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════

@app.get("/")
def read_root():
    return {
        "message": "Invisible Systems Map API v2.0",
        "nodes": len(nodes_data),
        "connections": len(connections_data),
        "conflict_events": len(conflicts_data),
        "datasets_dir": DATASETS_DIR,
    }


@app.get("/systems/{system_name}")
def get_system_data(system_name: str):
    """Returns GeoJSON data for a specific infrastructure system."""

    # ── Climate: special real-time handler ──
    if system_name == "climate":
        try:
            # Try live fetch using the climate script
            sys_path = os.path.join(os.path.dirname(__file__), '..', 'scripts')
            import importlib.util
            spec = importlib.util.spec_from_file_location("fetch_climate", os.path.join(sys_path, "fetch_climate.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore
            climate_nodes = mod.fetch_climate_data()
        except Exception as e:
            print(f"Climate live fetch failed: {e}, using cached")
            climate_nodes = load_json('climate.json')
            if not climate_nodes:
                climate_nodes = []

        node_features = []
        for cn in climate_nodes:
            props = cn.get("properties", cn)
            coords = cn.get("coordinates", props.get("coordinates", [0, 0]))
            node_features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": coords},
                "properties": {
                    "id": cn.get("id", ""),
                    "name": props.get("name", cn.get("name", "Climate Station")),
                    "type": props.get("type", "climate"),
                    "system": "climate",
                    **{k: v for k, v in props.items() if k not in ("id", "name", "type", "system")},
                }
            })

        return {
            "system": "climate",
            "node_count": len(node_features),
            "connection_count": 0,
            "nodes": {"type": "FeatureCollection", "features": node_features},
            "connections": {"type": "FeatureCollection", "features": []},
        }

    system_nodes = [n for n in nodes_data if n.get('system') == system_name]

    node_features = []
    node_id_to_coords = {}

    for node in system_nodes:
        coords = node.get('coordinates', [0, 0])
        node_id_to_coords[node['id']] = coords
        node_features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": coords},
            "properties": {
                "id": node['id'],
                "name": node['name'],
                "type": node.get('type', system_name),
                "system": node['system'],
                **node.get('properties', {})
            }
        })

    all_node_coords = {n['id']: n.get('coordinates', [0, 0]) for n in nodes_data}
    system_connections = [c for c in connections_data if c.get('system') == system_name]
    connection_features = []

    for conn in system_connections:
        src = all_node_coords.get(conn['source_node_id'])
        tgt = all_node_coords.get(conn['target_node_id'])
        if not src or not tgt:
            continue
        connection_features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": [src, tgt]},
            "properties": {
                "id": conn.get('id', 0),
                "source_position": src,
                "target_position": tgt,
                "type": conn.get('type', 'connection'),
                "system": conn['system'],
                "intensity": conn.get('intensity', 1.0),
                **conn.get('properties', {})
            }
        })

    return {
        "system": system_name,
        "node_count": len(node_features),
        "connection_count": len(connection_features),
        "nodes": {"type": "FeatureCollection", "features": node_features},
        "connections": {"type": "FeatureCollection", "features": connection_features},
    }


def _build_conflict_features(events: list) -> list:
    features = []
    for e in events:
        coords = e.get('coordinates', [0, 0])
        if not coords or coords == [0.0, 0.0]:
            continue
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": coords},
            "properties": {
                "id": e.get('id'),
                "name": e.get('name'),
                "event_type": e.get('event_type', 'geopolitical'),
                "sub_type": e.get('sub_type', ''),
                "date": e.get('date'),
                "country": e.get('country'),
                "location": e.get('location'),
                "actors": e.get('actors', []),
                "fatalities": e.get('fatalities', 0),
                "severity": e.get('severity', 'low'),
                "description": e.get('description', ''),
                "source": e.get('source', 'Unknown'),
                "system": "conflicts",
                "type": "conflict_event",
                "coordinates": coords,
            }
        })
    return features


@app.get("/conflicts")
def get_conflicts(
    event_type: Optional[str] = None,
    country: Optional[str] = None,
    severity: Optional[str] = None,
    days: int = 500
):
    """Returns static curated conflict events (no network calls)."""
    cutoff = datetime.now() - timedelta(days=days)
    results = list(conflicts_data)
    if event_type:
        results = [e for e in results if e.get('event_type') == event_type]
    if country:
        results = [e for e in results if country.lower() in e.get('country', '').lower()]
    if severity:
        results = [e for e in results if e.get('severity') == severity]
    filtered = []
    for e in results:
        try:
            d = datetime.strptime(e.get('date', '2000-01-01'), '%Y-%m-%d')
            if d >= cutoff:
                filtered.append(e)
        except Exception:
            filtered.append(e)
    features = _build_conflict_features(filtered)
    return {"type": "FeatureCollection", "count": len(features), "features": features}


@app.get("/conflicts/realtime")
def get_conflicts_realtime():
    """Returns live conflict events from GDELT Project + curated events."""
    try:
        events = fetch_gdelt_live()
    except Exception as ex:
        print(f"GDELT fetch error: {ex}, using static fallback")
        events = conflicts_data
    features = _build_conflict_features(events)
    cache_age = 0
    if _gdelt_cache["fetched_at"]:
        cache_age = int((datetime.utcnow() - _gdelt_cache["fetched_at"]).total_seconds())
    return {
        "type": "FeatureCollection",
        "count": len(features),
        "features": features,
        "meta": {
            "source": "GDELT Project + Curated Events",
            "cache_age_seconds": cache_age,
            "last_updated": _gdelt_cache["fetched_at"].isoformat() if _gdelt_cache["fetched_at"] else None,
            "live": True,
        }
    }


# ── AI Analysis (Free teaser via Groq, Premium LOCKED) ───────

class AnalyzeRequest(BaseModel):
    node: dict
    premium: bool = False

@app.post("/analyze")
async def analyze_node(req: AnalyzeRequest):
    """
    Returns AI analysis of an infrastructure node.
    - Free: 1-sentence teaser via Groq (free LLM)
    - Premium: LOCKED — always returns lock message
    """
    node = req.node
    node_name = node.get('name', 'Unknown')
    system = node.get('system', 'infrastructure')

    # Premium is always locked
    if req.premium:
        return {
            "teaser": f"{node_name} is a critical node in the global {system} network.",
            "full_analysis": None,
            "has_api_key": False,
            "premium": False,
            "locked": True,
            "message": "Premium Intelligence Brief is a Pro feature. Upgrade to unlock."
        }

    # Free teaser — try Groq first, then static fallback
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        try:
            import httpx
            resp = httpx.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                json={
                    "model": "llama3-8b-8192",
                    "messages": [
                        {"role": "system", "content": "You are a concise geopolitical infrastructure analyst."},
                        {"role": "user", "content": f"In exactly one sentence, explain why {node_name} ({node.get('type','node')} in the global {system} network) is strategically important. Be specific and compelling."}
                    ],
                    "max_tokens": 80,
                    "temperature": 0.7,
                },
                timeout=10.0,
            )
            data = resp.json()
            text = data["choices"][0]["message"]["content"].strip()
            return {"teaser": text, "full_analysis": None, "has_api_key": False, "premium": False}
        except Exception as e:
            print(f"Groq teaser error: {e}")

    # Static fallback
    return {
        "teaser": f"{node_name} is a critical node in the global {system} network.",
        "full_analysis": None,
        "has_api_key": False,
        "premium": False,
    }
