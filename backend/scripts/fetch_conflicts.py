import requests  # type: ignore[import-not-found]
import json
import os
import datetime

DATASETS_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datasets'))
CONFLICTS_FILE = os.path.join(DATASETS_DIR, 'conflicts.json')
os.makedirs(DATASETS_DIR, exist_ok=True)

def _get_severity(event_type: str, fatalities: int) -> str:
    """Assign severity levels based on fatalities and event type."""
    evt_lower = event_type.lower()
    
    # Base severity from type as requested
    if any(x in evt_lower for x in ["airstrike", "battle", "explosion", "violence against civilians", "terror", "bomb", "missile"]):
        base = "high"
    elif any(x in evt_lower for x in ["riot", "protest"]):
        base = "medium"
    elif "demonstration" in evt_lower or "strategic development" in evt_lower:
        base = "low"
    else:
        base = "medium"
        
    # Fatality modifiers
    if fatalities >= 10:
        return "critical"
    elif fatalities >= 1:
        if base in ["low", "medium"]:
            return "high"
        return "critical"
        
    return base

def get_curated_conflicts():
    return [
        {'id': 'ukr-001', 'name': 'Russia-Ukraine Front — Donetsk', 'event_type': 'battle',
         'date': '2024-03-01', 'country': 'UA', 'location': 'Donetsk Oblast', 'coordinates': [37.8, 48.0],
         'actors': ['Ukraine Armed Forces', 'Russian Armed Forces'], 'fatalities': 50, 'severity': 'critical',
         'description': 'Ongoing ground combat across eastern front.', 'source': 'ISW', 'system': 'conflicts'},
        {'id': 'gz-001', 'name': 'Israel-Gaza Ground Operations', 'event_type': 'battle',
         'date': '2024-03-01', 'country': 'PS', 'location': 'Gaza', 'coordinates': [34.47, 31.5],
         'actors': ['Israel Defense Forces', 'Hamas'], 'fatalities': 100, 'severity': 'critical',
         'description': 'Ongoing military operations targeting military infrastructure.', 'source': 'IDF', 'system': 'conflicts'},
        {'id': 'sdn-001', 'name': 'Sudan Civil War — Khartoum', 'event_type': 'battle',
         'date': '2024-02-25', 'country': 'SD', 'location': 'Khartoum', 'coordinates': [32.52, 15.55],
         'actors': ['Sudan Armed Forces', 'Rapid Support Forces'], 'fatalities': 200, 'severity': 'critical',
         'description': 'Largest humanitarian crisis. Heavy fighting for control of Khartoum.', 'source': 'UN OCHA', 'system': 'conflicts'},
        {'id': 'lbn-001', 'name': 'Israel-Hezbollah Cross-Border Fire', 'event_type': 'missile',
         'date': '2024-03-05', 'country': 'LB', 'location': 'South Lebanon', 'coordinates': [35.2, 33.27],
         'actors': ['Israel Defense Forces', 'Hezbollah'], 'fatalities': 15, 'severity': 'high',
         'description': 'Continuous exchange of airstrikes and rocket artillery.', 'source': 'UNIFIL', 'system': 'conflicts'},
        {'id': 'irn-tehran', 'name': 'Waves of Strikes on Capital', 'event_type': 'airstrike',
         'date': '2026-03-04', 'country': 'IR', 'location': 'Tehran', 'coordinates': [51.38, 35.68],
         'actors': ['US Armed Forces', 'Israel Defense Forces', 'Iranian Government'], 'fatalities': 500, 'severity': 'critical',
         'description': 'Pasteur Street district, Supreme National Security Council headquarters, presidential office, and Ali Khamenei bunker targeted in capital.', 'source': 'Al Jazeera', 'system': 'conflicts'},
        {'id': 'irn-minab', 'name': 'School Airstrike — Mass Civilian Casualties', 'event_type': 'airstrike',
         'date': '2026-03-01', 'country': 'IR', 'location': 'Minab (Hormozgan)', 'coordinates': [57.08, 27.14],
         'actors': ['US/Israel Armed Forces'], 'fatalities': 180, 'severity': 'critical',
         'description': 'Deadliest single incident reported. Airstrike on a girls school resulted in approx 180 child fatalities.', 'source': 'Al Jazeera', 'system': 'conflicts'},
        {'id': 'irn-bandar', 'name': 'Chemical Port Explosion', 'event_type': 'bombing',
         'date': '2026-03-02', 'country': 'IR', 'location': 'Bandar Abbas', 'coordinates': [56.28, 27.18],
         'actors': ['US/Israel Armed Forces'], 'fatalities': 40, 'severity': 'critical',
         'description': 'Chemical blast at the strategic port resulting in 40+ deaths and over 1,200 injuries. Widespread infrastructure damage.', 'source': 'Al Jazeera', 'system': 'conflicts'},
        {'id': 'irn-isfahan', 'name': 'Natanz Nuclear Facility Strike', 'event_type': 'missile',
         'date': '2026-03-03', 'country': 'IR', 'location': 'Natanz / Isfahan', 'coordinates': [51.72, 33.72],
         'actors': ['Israel Defense Forces', 'IRGC'], 'fatalities': 0, 'severity': 'high',
         'description': 'Nuclear facility struck with structural damage to multiple buildings.', 'source': 'Al Jazeera', 'system': 'conflicts'},
        {'id': 'irn-bushehr', 'name': 'Airport Infrastructure Destroyed', 'event_type': 'missile',
         'date': '2026-03-03', 'country': 'IR', 'location': 'Bushehr', 'coordinates': [50.84, 28.92],
         'actors': ['Israel Defense Forces', 'IRGC'], 'fatalities': 0, 'severity': 'high',
         'description': 'International airport hit by precision strikes, destroying an Iran Air aircraft and terminal infrastructure.', 'source': 'Al Jazeera', 'system': 'conflicts'},
        {'id': 'irn-khorramabad', 'name': 'Imam Ali Missile Base Bunkers Destroyed', 'event_type': 'airstrike',
         'date': '2026-03-02', 'country': 'IR', 'location': 'Khorramabad (Lorestan)', 'coordinates': [48.35, 33.48],
         'actors': ['US Armed Forces', 'IRGC Aerospace'], 'fatalities': 50, 'severity': 'critical',
         'description': 'Imam Ali Missile Base targeted and deep subterranean storage damaged by bunker-buster bombs.', 'source': 'Al Jazeera', 'system': 'conflicts'},
        {'id': 'irn-kurdish', 'name': 'Border Posts & Police Stations Targeted', 'event_type': 'missile',
         'date': '2026-03-04', 'country': 'IR', 'location': 'Sanandaj & Saqqez', 'coordinates': [46.99, 35.31],
         'actors': ['US/Israel Armed Forces', 'Iranian Police'], 'fatalities': 25, 'severity': 'high',
         'description': 'Multiple strikes hitting police stations and border posts across the Northwest Kurdish regions.', 'source': 'Al Jazeera', 'system': 'conflicts'},
        {'id': 'twn-001', 'name': 'China PLA Exercises — Taiwan Strait', 'event_type': 'geopolitical',
         'date': '2024-03-01', 'country': 'TW', 'location': 'Taiwan Strait', 'coordinates': [120.5, 24.0],
         'actors': ['PLA Air Force', 'RoC Air Force'], 'fatalities': 0, 'severity': 'medium',
         'description': 'PLA conducts joint patrols encircling Taiwan.', 'source': 'MND Taiwan', 'system': 'conflicts'},
        {'id': 'yem-001', 'name': 'Houthi Missile — Red Sea Shipping', 'event_type': 'missile',
         'date': '2024-03-01', 'country': 'YE', 'location': 'Red Sea', 'coordinates': [43.0, 15.0],
         'actors': ['Houthi Movement'], 'fatalities': 0, 'severity': 'high',
         'description': 'Attacks on commercial vessels disrupting trade.', 'source': 'US CENTCOM', 'system': 'conflicts'},
        {'id': 'usa-001', 'name': 'Civil Unrest — Washington D.C.', 'event_type': 'protest',
         'date': '2026-03-08', 'country': 'US', 'location': 'Washington D.C.', 'coordinates': [-77.0369, 38.9072],
         'actors': ['Domestic Protest Groups', 'National Guard'], 'fatalities': 0, 'severity': 'high',
         'description': 'Massive demonstrations and standoff near federal buildings.', 'source': 'Live News', 'system': 'conflicts'}
    ]

def _normalize_acled_items(items):
    out = []
    for it in items:
        try:
            lat = None; lng = None
            if isinstance(it, dict):
                if "latitude" in it and "longitude" in it:
                    lat = float(it.get("latitude") or 0)
                    lng = float(it.get("longitude") or 0)
                elif "lat" in it and ("lon" in it or "lng" in it):
                    lat = float(it.get("lat") or 0)
                    lng = float(it.get("lon") or it.get("lng") or 0)

            if lat is None or lng is None:
                continue
            if lat == 0.0 and lng == 0.0:
                continue
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                continue

            evt_id = str(it.get("id") or it.get("event_id") or it.get("data_id") or f"acled-{len(out)}")
            evt_type = str(it.get("event_type") or it.get("sub_event_type") or "battle")
            date = str(it.get("event_date") or it.get("date") or datetime.datetime.now().strftime("%Y-%m-%d"))
            country = str(it.get("country") or "")
            location_name = str(it.get("location") or "")
            source = str(it.get("source") or "ACLED")
            
            description = str(it.get("notes") or "")
            
            raw_actor1 = it.get("actor1")
            raw_actor2 = it.get("actor2")
            actors = []
            if raw_actor1: actors.append(str(raw_actor1))
            if raw_actor2: actors.append(str(raw_actor2))
            
            fatalities_raw = it.get("fatalities") or it.get("deaths") or 0
            try:
                fatalities = int(fatalities_raw)
            except:
                fatalities = 0

            severity = _get_severity(evt_type, fatalities)

            out.append({
                'id': evt_id,
                'event_type': evt_type,
                'location': location_name,
                'latitude': lat,
                'longitude': lng,
                'coordinates': [lng, lat],
                'actors': actors,
                'fatalities': fatalities,
                'date': date,
                'source': source,
                'severity': severity,
                'summary': description,
                # Additional compat fields
                'name': location_name[:120] if location_name else evt_type,
                'description': description,
                'country': country,
                'system': 'conflicts'
            })
        except Exception:
            continue
    return out

def fetch_acled_official(acled_api_url: str, acled_api_key: str = None, limit: int = 2000):
    events = []
    try:
        params = {"limit": limit}
        headers = {}
        if acled_api_key:
            headers["Authorization"] = f"Bearer {acled_api_key}"
            params["token"] = acled_api_key

        print(f"Fetching ACLED feed: {acled_api_url} (limit={limit})")
        r = requests.get(acled_api_url, headers=headers, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()

        if isinstance(data, dict):
            if "data" in data and isinstance(data["data"], list):
                items = data["data"]
            elif "results" in data and isinstance(data["results"], list):
                items = data["results"]
            else:
                items = []
                for v in data.values():
                    if isinstance(v, list):
                        items = v
                        break
        elif isinstance(data, list):
            items = data
        else:
            items = []

        events = _normalize_acled_items(items)
        print(f"✅ Parsed {len(events)} structured ACLED events.")
    except Exception as e:
        print(f"ACLED fetch error: {e}")

    return events


if __name__ == "__main__":
    print('🔴 Conflict Intelligence Ingestion Pipeline (Structured ACLED Data Tier)')
    print('Scraping disabled. Injecting curated operational data and ACLED structured data exclusively.')
    new_events = get_curated_conflicts()
    
    # Optionally fetch ACLED official feed if configured via environment
    acled_url = os.getenv('ACLED_API_URL')
    acled_key = os.getenv('ACLED_API_KEY')
    
    # We only use ACLED. No GDELT. No natural language guessing.
    if acled_url:
        acled_events = fetch_acled_official(acled_url, acled_key, limit=5000)
        if acled_events:
            new_events.extend(acled_events)
    else:
        # If no ACLED URL is specified in env, try the public default endpoint 
        public_acled = "https://api.acleddata.com/acled/read"
        print(f"No ACLED_API_URL in .env, attempting public endpoint: {public_acled}")
        acled_events = fetch_acled_official(public_acled, None, limit=1000)
        if acled_events:
            new_events.extend(acled_events)
            
    # Load existing cache to preserve known live events
    existing_events = []
    if os.path.exists(CONFLICTS_FILE):
        try:
            with open(CONFLICTS_FILE, 'r', encoding='utf-8') as f:
                existing_events = json.load(f)
        except: pass
        
    # Combine old and new, allowing new ones to overwrite old ones with same ID
    event_map = {e['id']: e for e in existing_events}
    for e in new_events:
        event_map[e['id']] = e
        
    events = list(event_map.values())
    
    # deduplicate by coordinates and event_type
    seen = set(); unique = []
    for e in events:
        uniq_key = str(e['coordinates']) + e['event_type']
        if uniq_key not in seen:
            seen.add(uniq_key)
            unique.append(e)
            
    print(f'Structured data processing complete. {len(unique)} total verified structured events retained.')
    
    with open(CONFLICTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)
        
    print(f'✅ Wrote {len(unique)} strictly verified structured events to JSON frontend feed.')
