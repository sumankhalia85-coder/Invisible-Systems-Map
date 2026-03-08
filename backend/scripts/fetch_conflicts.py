import requests  # type: ignore[import-not-found]
import json, os, datetime, zipfile, io, csv, itertools, time, urllib.parse

DATASETS_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datasets'))
CONFLICTS_FILE = os.path.join(DATASETS_DIR, 'conflicts.json')
os.makedirs(DATASETS_DIR, exist_ok=True)
GEOCODE_CACHE_FILE = os.path.join(DATASETS_DIR, 'geocode_cache.json')


def _load_geocode_cache():
    try:
        if os.path.exists(GEOCODE_CACHE_FILE):
            with open(GEOCODE_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_geocode_cache(cache: dict):
    try:
        with open(GEOCODE_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


_GEOCODE_CACHE = _load_geocode_cache()


def geocode_place(place: str):
    """Best-effort geocode using Nominatim with a small cache.

    Returns (lat, lon) or (None, None).
    """
    if not place:
        return None, None
    key = place.strip().lower()
    if key in _GEOCODE_CACHE:
        v = _GEOCODE_CACHE[key]
        return v.get('lat'), v.get('lon')

    try:
        base = 'https://nominatim.openstreetmap.org/search'
        params = {'q': place, 'format': 'json', 'limit': 1}
        headers = {'User-Agent': 'Invisible-Systems-Map/1.0 (+https://example.com)'}
        url = base + '?' + urllib.parse.urlencode(params)
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        j = r.json()
        if isinstance(j, list) and j:
            lat = float(j[0].get('lat'))
            lon = float(j[0].get('lon'))
            _GEOCODE_CACHE[key] = {'lat': lat, 'lon': lon}
            _save_geocode_cache(_GEOCODE_CACHE)
            time.sleep(1.0)  # be polite to the service
            return lat, lon
    except Exception:
        pass
    # store negative cache to avoid repeated attempts
    _GEOCODE_CACHE[key] = {'lat': None, 'lon': None}
    _save_geocode_cache(_GEOCODE_CACHE)
    return None, None


def _is_valid_latlon(lat, lon):
    try:
        lat = float(lat); lon = float(lon)
    except Exception:
        return False
    if lat == 0.0 and lon == 0.0:
        return False
    return -90 <= lat <= 90 and -180 <= lon <= 180


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
        {'id': 'irn-missilesites', 'name': 'Missile & Drone Hubs Targeted', 'event_type': 'missile',
         'date': '2026-03-05', 'country': 'IR', 'location': 'Ahvaz / Karaj / Yazd', 'coordinates': [48.66, 31.32],
         'actors': ['US/Israel Armed Forces', 'IRGC'], 'fatalities': 15, 'severity': 'high',
         'description': 'Coordinated attacks on critical missile manufacturing and drone launch infrastructure.', 'source': 'Al Jazeera', 'system': 'conflicts'},
        {'id': 'twn-001', 'name': 'China PLA Exercises — Taiwan Strait', 'event_type': 'geopolitical',
         'date': '2024-03-01', 'country': 'TW', 'location': 'Taiwan Strait', 'coordinates': [120.5, 24.0],
         'actors': ['PLA Air Force', 'RoC Air Force'], 'fatalities': 0, 'severity': 'medium',
         'description': 'PLA conducts joint patrols encircling Taiwan.', 'source': 'MND Taiwan', 'system': 'conflicts'},
        {'id': 'yem-001', 'name': 'Houthi Missile — Red Sea Shipping', 'event_type': 'missile',
         'date': '2024-03-01', 'country': 'YE', 'location': 'Red Sea', 'coordinates': [43.0, 15.0],
         'actors': ['Houthi Movement'], 'fatalities': 0, 'severity': 'high',
         'description': 'Attacks on commercial vessels disrupting trade.', 'source': 'US CENTCOM', 'system': 'conflicts'},
        # --- NEW REAL-TIME SCENARIOS ---
        {'id': 'usa-001', 'name': 'Civil Unrest — Washington D.C.', 'event_type': 'protest',
         'date': '2026-03-08', 'country': 'US', 'location': 'Washington D.C.', 'coordinates': [-77.0369, 38.9072],
         'actors': ['Domestic Protest Groups', 'National Guard'], 'fatalities': 0, 'severity': 'high',
         'description': 'Massive demonstrations and standoff near federal buildings.', 'source': 'Live News', 'system': 'conflicts'},
        {'id': 'usa-002', 'name': 'Border Standoff — Eagle Pass, Texas', 'event_type': 'battle',
         'date': '2026-03-07', 'country': 'US', 'location': 'Eagle Pass, TX', 'coordinates': [-100.4913, 28.7091],
         'actors': ['Texas National Guard', 'Federal Agents'], 'fatalities': 0, 'severity': 'medium',
         'description': 'Escalating jurisdictional conflict over border infrastructure.', 'source': 'Local Intel', 'system': 'conflicts'},
        {'id': 'isr-001', 'name': 'Strategic Missile Interception — Tel Aviv', 'event_type': 'missile',
         'date': '2026-03-08', 'country': 'IL', 'location': 'Tel Aviv', 'coordinates': [34.7818, 32.0853],
         'actors': ['IDF Iron Dome', 'Regional Proxies'], 'fatalities': 2, 'severity': 'critical',
         'description': 'Multiple high-altitude interceptions over metropolitan area.', 'source': 'IDF', 'system': 'conflicts'},
        {'id': 'isr-002', 'name': 'Northern Front Skirmish — Kiryat Shmona', 'event_type': 'battle',
         'date': '2026-03-08', 'country': 'IL', 'location': 'Kiryat Shmona', 'coordinates': [35.5684, 33.2078],
         'actors': ['IDF', 'Hezbollah'], 'fatalities': 5, 'severity': 'high',
         'description': 'Heavy artillery exchanges and drone incursions across the Blue Line.', 'source': 'UNIFIL', 'system': 'conflicts'},
        {'id': 'irn-001', 'name': 'Cyber-Kinetic Strike — Natanz Power Grid', 'event_type': 'bombing',
         'date': '2026-03-08', 'country': 'IR', 'location': 'Natanz', 'coordinates': [51.72, 33.72],
         'actors': ['Unknown State Actor', 'IRGC'], 'fatalities': 0, 'severity': 'critical',
         'description': 'Severe damage to nuclear facility auxiliary power systems.', 'source': 'IAEA Watch', 'system': 'conflicts'},
    ]

def fetch_gdelt_csv():
    events = []
    try:
        r = requests.get('http://data.gdeltproject.org/gdeltv2/lastupdate.txt', timeout=15)
        # Fetch the most recent export CSV URLs
        urls: list[str] = [str(line.split(' ')[-1]) for line in r.text.split('\n') if 'export.CSV.zip' in line]
        if not urls: return []
        
        # Try up to 3 URLs in case the most recent published zip is corrupted
        for url in itertools.islice(urls, 3):
            try:
                print('Fetching fresh GDELT global exports:', url)
                r2 = requests.get(url, timeout=30)
                with zipfile.ZipFile(io.BytesIO(r2.content)) as z:
                    with z.open(z.namelist()[0]) as f:
                        content = f.read().decode('utf-8')
                        break # Success, break out of retry loop
            except Exception as zip_err:
                print(f'GDELT Archive {url} corrupt or unavailable: {zip_err}, trying next...')
                content = None
                
        if not content:
            raise Exception("All attempted GDELT zip archives failed.")
            
        for row in csv.reader(content.split('\n'), delimiter='\t'):
                    if len(row) < 61: continue
                    
                    root_code = row[28]
                    # Focus entirely on kinetic conflict and mass unrest
                    # 14=Protest, 18=Assault, 19=Fight, 20=Mass Violence
                    if root_code not in ['14', '18', '19', '20']: continue
                    
                    try:
                        lat, lng = float(row[39]), float(row[40]) # indices: 39=Lat, 40=Lon
                    except:
                        continue

                    # If coordinates are invalid, try geocoding from the place name
                    if not _is_valid_latlon(lat, lng):
                        location_name = row[36] or ''
                        print(f"  ⚠️ GDELT poisoning detected: Invalid coords [{lat}, {lng}] for row {row[0]} — attempting geocode '{location_name}'")
                        g_lat, g_lng = geocode_place(location_name)
                        if g_lat is not None and g_lng is not None and _is_valid_latlon(g_lat, g_lng):
                            lat, lng = g_lat, g_lng
                            print(f"    → geocode success: [{lat}, {lng}]")
                        else:
                            print(f"    → geocode failed for '{location_name}', skipping row {row[0]}")
                            continue
                    
                    # Determine specific type from base code
                    evt_type = 'protest' if root_code == '14' else 'battle'
                    if row[26] in ['183','193','202']: evt_type = 'missile' # drone/missile
                    elif row[26] in ['190','194','195']: evt_type = 'airstrike' 
                    
                    name_prefix = ''
                    if evt_type == 'protest': name_prefix = 'Political Protest'
                    elif evt_type == 'battle': name_prefix = 'Armed Clash'
                    elif evt_type == 'missile': name_prefix = 'Missile/Artillery Strike'
                    elif evt_type == 'airstrike': name_prefix = 'Airstrike incident'
                    
                    actor1 = row[6] or 'Unidentified Group'
                    actor2 = row[16] or ''
                    desc = f'Sources report an incident involving {actor1}'
                    if actor2: desc += f' and {actor2}.'
                    
                    location_name = row[36] or 'Unknown Location'
                    
                    events.append({
                        'id': f'gdelt-{row[0]}',
                        'name': f'{name_prefix} in {location_name}',
                        'event_type': evt_type,
                        'sub_type': row[26], # CAMEO base code
                        'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                        'country': row[37],
                        'location': location_name,
                        'coordinates': [lng, lat],
                        'actors': [a for a in [row[6], row[16]] if a],
                        'fatalities': 0,
                        'severity': 'high' if evt_type in ['missile', 'airstrike'] else 'medium',
                        'description': desc,
                        'source': row[60] if row[60] else 'GDELT Live',
                        'system': 'conflicts'
                    })
        print(f'✅ Parsed {len(events)} geolocated realtime events.')
    except Exception as e:
        print('GDELT Fetch Error:', e)
    return events


def fetch_gdelt_v2(query: str = "protest OR riot OR fight OR violence OR war OR strike OR missile", mode: str = "EventList", maxrecords: int = 1500):
    """Fetch events from the GDELT V2 API (best-effort adapter).

    Returns normalized pipeline events similar to the other adapters.
    """
    events = []
    try:
        host = "https://api.gdeltproject.org"
        # Try multiple endpoint paths and modes until one returns usable JSON
        candidate_paths = [
            "/api/v2/events/docdoc",
            "/api/v2/events/doc",
            "/api/v2/events/events",
            "/api/v2/doc/doc",
            "/api/v2/doc/docdoc",
            "/api/v2/events/search",
        ]

        modes = [mode, "EventList", "ArtList", "Timeline", "" ]
        data = None
        used_path = None
        used_mode = None
        print(f"Fetching GDELT V2: trying multiple endpoints for query='{query}' maxrecords={maxrecords}")
        for path in candidate_paths:
            for m in modes:
                params = {"query": query, "format": "json", "maxrecords": maxrecords}
                if m:
                    params["mode"] = m
                try:
                    url = host + path
                    r = requests.get(url, params=params, timeout=30)
                    if r.status_code == 404:
                        continue
                    r.raise_for_status()
                    j = r.json()
                    # Accept response if contains any list-like value
                    found_list = False
                    if isinstance(j, dict):
                        for v in j.values():
                            if isinstance(v, list) and len(v) > 0:
                                found_list = True
                                break
                    elif isinstance(j, list) and len(j) > 0:
                        found_list = True

                    if found_list:
                        data = j
                        used_path = path
                        used_mode = m
                        print(f"GDELT V2: using {path} mode={m}")
                        break
                except Exception:
                    continue
            if data is not None:
                break

        if data is None:
            raise Exception("No usable GDELT V2 endpoint responded with list data")

        # GDELT V2 responses vary by mode. Try to locate candidate items.
        items = []
        if isinstance(data, dict):
            for k in ("events", "data", "articles", "items", "results", "articles_list", "event_list"):
                if k in data and isinstance(data[k], list):
                    items = data[k]
                    break
            if not items:
                for v in data.values():
                    if isinstance(v, list):
                        items = v
                        break
        elif isinstance(data, list):
            items = data

        for it in items:
            try:
                # Normalize best-effort
                lat = None; lng = None
                date = None
                location_name = ""
                actors = []
                source = ''

                if isinstance(it, dict):
                    # common fields across modes
                    lat = it.get('lat') or it.get('latitude') or it.get('location_lat')
                    lng = it.get('lon') or it.get('longitude') or it.get('location_long')
                    if lat is not None and lng is not None:
                        try:
                            lat = float(lat); lng = float(lng)
                        except: lat = None; lng = None

                    date = it.get('event_date') or it.get('date') or it.get('published') or it.get('source_date')
                    location_name = it.get('location') or it.get('locations') or it.get('title') or ''
                    # actors: try actor1/actor2 or share text
                    a1 = it.get('actor1') or it.get('actor') or it.get('actor1name')
                    a2 = it.get('actor2') or it.get('actor2name')
                    if a1: actors.append(a1)
                    if a2: actors.append(a2)
                    source = it.get('source') or it.get('sourceurl') or it.get('domain') or ''

                if lat is None or lng is None:
                    # try location object lists
                    if isinstance(it, dict) and 'locations' in it and isinstance(it['locations'], list) and it['locations']:
                        loc0 = it['locations'][0]
                        lat = loc0.get('lat') or loc0.get('latitude')
                        lng = loc0.get('lon') or loc0.get('longitude')
                        if lat is not None and lng is not None:
                            try:
                                lat = float(lat); lng = float(lng)
                            except: lat = None; lng = None

                # If still invalid, attempt geocoding from location_name
                if not _is_valid_latlon(lat, lng):
                    location_name = location_name or (it.get('location') if isinstance(it, dict) else '')
                    g_lat, g_lng = geocode_place(location_name)
                    if g_lat is not None and g_lng is not None and _is_valid_latlon(g_lat, g_lng):
                        lat, lng = g_lat, g_lng
                    else:
                        continue

                evt_type = it.get('event') or it.get('event_type') or it.get('category') or 'protest'
                evt_id = it.get('id') or it.get('gid') or f'gdeltv2-{abs(hash(str(it)))%1000000}'

                events.append({
                    'id': evt_id,
                    'name': str(location_name)[:120] if location_name else f'GDELT {evt_type}',
                    'event_type': evt_type,
                    'sub_type': it.get('sub_event_type','') if isinstance(it, dict) else '',
                    'date': date or datetime.datetime.utcnow().strftime('%Y-%m-%d'),
                    'country': it.get('country') or it.get('countrycode') or '',
                    'location': location_name,
                    'coordinates': [lng, lat],
                    'actors': actors,
                    'fatalities': it.get('fatalities') or 0,
                    'severity': 'medium',
                    'description': it.get('summary') or it.get('notes') or it.get('description') or '',
                    'source': source or 'GDELT',
                    'system': 'conflicts'
                })
            except Exception:
                continue

        print(f'✅ Parsed {len(events)} GDELTv2 events (query={query}).')
    except Exception as e:
        print('GDELT V2 Fetch Error:', e)
    return events


def fetch_acled_official(acled_api_url: str, acled_api_key: str = None, limit: int = 2000):
    """Fetch events from the official ACLED API (best-effort adapter).

    This adapter expects an ACLED-style JSON response. We send a conservative
    request with a `limit` and attempt to normalize the returned records into
    the event shape used by the pipeline. If anything fails, return an empty list.
    """
    # Backward-compatible single-request adapter kept for small calls.
    # For larger pulls use `fetch_acled_paginated` or supply username/password to the pipeline.
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
                    elif "location" in it and isinstance(it.get("location"), dict) and "coordinates" in it.get("location"):
                        coords = it.get("location").get("coordinates")
                        if isinstance(coords, (list, tuple)) and len(coords) >= 2:
                            lng, lat = coords[0], coords[1]
                    elif "coordinates" in it and isinstance(it.get("coordinates"), (list, tuple)):
                        lng, lat = it.get("coordinates")[0], it.get("coordinates")[1]

                if lat is None or lng is None:
                    continue
                if lat == 0.0 and lng == 0.0:
                    continue
                if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                    continue

                evt_id = it.get("id") or it.get("event_id") or it.get("ACLED_ID") or f"acled-{len(out)}"
                evt_type = it.get("event_type") or it.get("event") or it.get("category") or "geopolitical"
                date = it.get("event_date") or it.get("date") or it.get("year") or ""
                country = it.get("country") or it.get("country_name") or it.get("admin1") or ""
                location_name = it.get("location") or it.get("location_name") or it.get("notes") or ""
                actors = it.get("actor1") or it.get("actors") or []
                fatalities = it.get("fatalities") or it.get("deaths") or 0
                severity = it.get("severity") or ("high" if evt_type in ["airstrike","missile","battle"] else "medium")
                description = it.get("notes") or it.get("description") or ""

                out.append({
                    'id': evt_id,
                    'name': str(location_name)[:120] if location_name else f"ACLED {evt_type}",
                    'event_type': evt_type,
                    'sub_type': it.get('sub_type',''),
                    'date': date,
                    'country': country,
                    'location': location_name,
                    'coordinates': [lng, lat],
                    'actors': actors if isinstance(actors, list) else [actors],
                    'fatalities': fatalities,
                    'severity': severity,
                    'description': description,
                    'source': it.get('source') or 'ACLED',
                    'system': 'conflicts'
                })
            except Exception:
                continue
        return out

    events = []
    try:
        params = {"limit": limit}
        headers = {}
        if acled_api_key:
            headers["Authorization"] = f"Bearer {acled_api_key}"
            params["token"] = acled_api_key

        print(f"Fetching ACLED official feed: {acled_api_url} (limit={limit})")
        r = requests.get(acled_api_url, headers=headers, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()

        # Extract items (supports several response shapes)
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
        print(f"✅ Parsed {len(events)} ACLED events.")
    except Exception as e:
        print(f"ACLED fetch error: {e}")

    return events


def get_acled_access_token(username: str, password: str, token_url: str = "https://acleddata.com/oauth/token") -> dict:
    """Exchange myACLED username/password for an access + refresh token."""
    try:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            'username': username,
            'password': password,
            'grant_type': 'password',
            'client_id': 'acled'
        }
        r = requests.post(token_url, headers=headers, data=data, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"ACLED token exchange failed: {e}")
        return {}


def fetch_acled_paginated(acled_api_url: str, access_token: str = None, username: str = None, password: str = None, limit: int = 5000, max_pages: int = 50, extra_params: dict = None):
    """Fetch ACLED results with pagination using OAuth access token.

    Behavior:
    - If `access_token` not provided, will attempt token exchange with `username`/`password`.
    - Paginate by sending `limit` and `page` params. Stops when a page returns fewer than `limit` items.
    - Returns normalized pipeline events (same shape as `fetch_acled_official`).
    """
    if extra_params is None:
        extra_params = {}

    if not access_token and username and password:
        tok = get_acled_access_token(username, password)
        access_token = tok.get('access_token')
        if not access_token:
            print('No access token obtained; aborting ACLED paginated fetch.')
            return []

    headers = {}
    if access_token:
        headers['Authorization'] = f"Bearer {access_token}"

    all_items = []
    page = 1
    seen = 0
    try:
        while page <= max_pages:
            params = {**extra_params, 'limit': limit, 'page': page}
            print(f'Fetching ACLED page {page} (limit={limit})')
            r = requests.get(acled_api_url, headers=headers, params=params, timeout=30)
            r.raise_for_status()
            data = r.json()

            # find array of items
            if isinstance(data, dict):
                if 'data' in data and isinstance(data['data'], list):
                    items = data['data']
                elif 'results' in data and isinstance(data['results'], list):
                    items = data['results']
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

            if not items:
                break

            all_items.extend(items)
            seen += len(items)
            print(f'  Retrieved {len(items)} items (total {seen}).')

            if len(items) < limit:
                break
            page += 1

    except Exception as e:
        print(f'ACLED paginated fetch error: {e}')

    # Normalize collected items into pipeline events
    try:
        normalized = []
        for it in all_items:
            try:
                lat = None; lng = None
                if isinstance(it, dict):
                    if "latitude" in it and "longitude" in it:
                        lat = float(it.get("latitude") or 0)
                        lng = float(it.get("longitude") or 0)
                    elif "lat" in it and ("lon" in it or "lng" in it):
                        lat = float(it.get("lat") or 0)
                        lng = float(it.get("lon") or it.get("lng") or 0)
                    elif "location" in it and isinstance(it.get("location"), dict) and "coordinates" in it.get("location"):
                        coords = it.get("location").get("coordinates")
                        if isinstance(coords, (list, tuple)) and len(coords) >= 2:
                            lng, lat = coords[0], coords[1]
                    elif "coordinates" in it and isinstance(it.get("coordinates"), (list, tuple)):
                        lng, lat = it.get("coordinates")[0], it.get("coordinates")[1]

                if lat is None or lng is None:
                    continue
                if lat == 0.0 and lng == 0.0:
                    continue
                if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                    continue

                evt_id = it.get("id") or it.get("event_id") or it.get("ACLED_ID") or f"acled-{len(normalized)}"
                evt_type = it.get("event_type") or it.get("event") or it.get("category") or "geopolitical"
                date = it.get("event_date") or it.get("date") or it.get("year") or ""
                country = it.get("country") or it.get("country_name") or it.get("admin1") or ""
                location_name = it.get("location") or it.get("location_name") or it.get("notes") or ""
                actors = it.get("actor1") or it.get("actors") or []
                fatalities = it.get("fatalities") or it.get("deaths") or 0
                severity = it.get("severity") or ("high" if evt_type in ["airstrike","missile","battle"] else "medium")
                description = it.get("notes") or it.get("description") or ""

                normalized.append({
                    'id': evt_id,
                    'name': str(location_name)[:120] if location_name else f"ACLED {evt_type}",
                    'event_type': evt_type,
                    'sub_type': it.get('sub_type',''),
                    'date': date,
                    'country': country,
                    'location': location_name,
                    'coordinates': [lng, lat],
                    'actors': actors if isinstance(actors, list) else [actors],
                    'fatalities': fatalities,
                    'severity': severity,
                    'description': description,
                    'source': it.get('source') or 'ACLED',
                    'system': 'conflicts'
                })
            except Exception:
                continue
        print(f'✅ Normalized {len(normalized)} ACLED events from {seen} raw items.')
        return normalized
    except Exception as e:
        print(f'ACLED normalization error: {e}')
        return []


def fetch_acled_cookie_paginated(acled_api_url: str, username: str, password: str, limit: int = 5000, max_pages: int = 50, extra_params: dict = None):
    """Fallback: authenticate via myACLED cookie-based login and paginate using the session.

    This posts to `/user/login?_format=json` with JSON {name, pass} to obtain a session cookie,
    then requests pages from the API using that session. Some accounts only support cookie-based access.
    """
    if extra_params is None:
        extra_params = {}

    session = requests.Session()
    login_url = 'https://acleddata.com/user/login?_format=json'
    try:
        payload = {'name': username, 'pass': password}
        print('Attempting cookie-based ACLED login...')
        r = session.post(login_url, json=payload, timeout=15)
        r.raise_for_status()
        # Successful login will set session cookies; proceed to paginate
    except Exception as e:
        print(f'ACLED cookie login failed: {e}')
        return []

    all_items = []
    page = 1
    seen = 0
    try:
        while page <= max_pages:
            params = {**extra_params, 'limit': limit, 'page': page}
            print(f'Fetching ACLED (cookie) page {page} (limit={limit})')
            r = session.get(acled_api_url, params=params, timeout=30)
            r.raise_for_status()
            data = r.json()

            if isinstance(data, dict):
                if 'data' in data and isinstance(data['data'], list):
                    items = data['data']
                elif 'results' in data and isinstance(data['results'], list):
                    items = data['results']
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

            if not items:
                break

            all_items.extend(items)
            seen += len(items)
            print(f'  Retrieved {len(items)} items (total {seen}).')

            if len(items) < limit:
                break
            page += 1

    except Exception as e:
        print(f'ACLED cookie-paginated fetch error: {e}')

    # Normalize like in `fetch_acled_paginated`
    try:
        normalized = []
        for it in all_items:
            try:
                lat = None; lng = None
                if isinstance(it, dict):
                    if "latitude" in it and "longitude" in it:
                        lat = float(it.get("latitude") or 0)
                        lng = float(it.get("longitude") or 0)
                    elif "lat" in it and ("lon" in it or "lng" in it):
                        lat = float(it.get("lat") or 0)
                        lng = float(it.get("lon") or it.get("lng") or 0)
                    elif "location" in it and isinstance(it.get("location"), dict) and "coordinates" in it.get("location"):
                        coords = it.get("location").get("coordinates")
                        if isinstance(coords, (list, tuple)) and len(coords) >= 2:
                            lng, lat = coords[0], coords[1]
                    elif "coordinates" in it and isinstance(it.get("coordinates"), (list, tuple)):
                        lng, lat = it.get("coordinates")[0], it.get("coordinates")[1]

                if lat is None or lng is None:
                    continue
                if lat == 0.0 and lng == 0.0:
                    continue
                if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                    continue

                evt_id = it.get("id") or it.get("event_id") or it.get("ACLED_ID") or f"acled-{len(normalized)}"
                evt_type = it.get("event_type") or it.get("event") or it.get("category") or "geopolitical"
                date = it.get("event_date") or it.get("date") or it.get("year") or ""
                country = it.get("country") or it.get("country_name") or it.get("admin1") or ""
                location_name = it.get("location") or it.get("location_name") or it.get("notes") or ""
                actors = it.get("actor1") or it.get("actors") or []
                fatalities = it.get("fatalities") or it.get("deaths") or 0
                severity = it.get("severity") or ("high" if evt_type in ["airstrike","missile","battle"] else "medium")
                description = it.get("notes") or it.get("description") or ""

                normalized.append({
                    'id': evt_id,
                    'name': str(location_name)[:120] if location_name else f"ACLED {evt_type}",
                    'event_type': evt_type,
                    'sub_type': it.get('sub_type',''),
                    'date': date,
                    'country': country,
                    'location': location_name,
                    'coordinates': [lng, lat],
                    'actors': actors if isinstance(actors, list) else [actors],
                    'fatalities': fatalities,
                    'severity': severity,
                    'description': description,
                    'source': it.get('source') or 'ACLED',
                    'system': 'conflicts'
                })
            except Exception:
                continue
        print(f'✅ Normalized {len(normalized)} ACLED events from {seen} raw items (cookie).')
        return normalized
    except Exception as e:
        print(f'ACLED cookie normalization error: {e}')
        return []


if __name__ == "__main__":
    print('🔴 Conflict Intelligence Ingestion Pipeline')
    new_events = get_curated_conflicts()
    new_events.extend(fetch_gdelt_csv())
    # Also attempt GDELT V2 API to get more focused realtime events
    try:
        new_events.extend(fetch_gdelt_v2(query='protest OR riot OR fight OR violence', mode='EventList', maxrecords=500))
    except Exception as e:
        print(f'GDELT V2 adapter failed: {e}')

    # Optionally fetch ACLED official feed if configured via environment
    acled_url = os.getenv('ACLED_API_URL')
    acled_key = os.getenv('ACLED_API_KEY')
    acled_user = os.getenv('ACLED_USERNAME')
    acled_pass = os.getenv('ACLED_PASSWORD')
    if acled_url:
        try:
            # Prefer OAuth username/password for programmatic access (paginated)
            if acled_user and acled_pass:
                print('ACLED credentials detected; performing OAuth + paginated fetch')
                acled_events = fetch_acled_paginated(acled_url, username=acled_user, password=acled_pass, limit=5000, max_pages=50)
            elif acled_key:
                # If user supplied a bearer token previously obtained, use paginated fetch with it
                print('ACLED access token detected; performing paginated fetch')
                acled_events = fetch_acled_paginated(acled_url, access_token=acled_key, limit=5000, max_pages=50)
            else:
                # Conservative single-request fallback
                print('ACLED URL present but no credentials; using single-request adapter (limit=500)')
                acled_events = fetch_acled_official(acled_url, acled_key, limit=500)

            if acled_events:
                new_events.extend(acled_events)
            else:
                # If OAuth paginated returned nothing or was forbidden, try cookie-based session as a fallback
                if acled_user and acled_pass:
                    print('Paginated OAuth returned no events — trying cookie-based ACLED fetch as fallback')
                    try:
                        cookie_events = fetch_acled_cookie_paginated(acled_url, acled_user, acled_pass, limit=5000, max_pages=50)
                        if cookie_events:
                            new_events.extend(cookie_events)
                    except Exception as e:
                        print(f'Cookie-based ACLED fallback failed: {e}')
        except Exception as e:
            print(f"Warning: ACLED adapter failed: {e}")
    
    # Load existing cache to preserve known live events if GDELT fails temporarily
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
    
    # deduplicate by coordinates and event_type to prevent overlapping visual clutter
    seen = set(); unique = []
    for e in events:
        uniq_key = str(e['coordinates']) + e['event_type']
        if uniq_key not in seen:
            seen.add(uniq_key)
            unique.append(e)
    
    with open(CONFLICTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)
        
    print(f'✅ Wrote {len(unique)} total events to JSON.')

