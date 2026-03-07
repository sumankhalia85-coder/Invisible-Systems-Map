import requests  # type: ignore[import-not-found]
import json, os, datetime, zipfile, io, csv, itertools

DATASETS_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datasets'))
CONFLICTS_FILE = os.path.join(DATASETS_DIR, 'conflicts.json')
os.makedirs(DATASETS_DIR, exist_ok=True)


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
         'description': 'Attacks on commercial vessels disrupting trade.', 'source': 'US CENTCOM', 'system': 'conflicts'}
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
                        if lat == 0.0 and lng == 0.0: continue
                    except: continue
                    
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


if __name__ == "__main__":
    print('🔴 Conflict Intelligence Ingestion Pipeline')
    new_events = get_curated_conflicts()
    new_events.extend(fetch_gdelt_csv())
    
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

