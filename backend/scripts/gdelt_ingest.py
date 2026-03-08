import csv
import json
import os
import sys

DATASETS_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datasets'))
CONFLICTS_FILE = os.path.join(DATASETS_DIR, 'conflicts.json')

def parse_date(sqldate):
    if not sqldate or len(sqldate) != 8:
        return sqldate or ""
    return f"{sqldate[0:4]}-{sqldate[4:6]}-{sqldate[6:8]}"

def get_severity(event_code):
    try:
        code = int(event_code)
        if code >= 190: return "High"
        if code >= 170: return "Medium"
        if code >= 140: return "Low"
    except:
        pass
    return "Medium"

def get_event_type(event_code):
    try:
        code = int(event_code)
        if 190 <= code <= 200: return "Military Conflict / Attack"
        if 160 <= code <= 180: return "Violent Action"
        if 140 <= code <= 145: return "Protest / Demonstration"
    except:
        pass
    return "Conflict Event"

def process_gdelt(file_path):
    print(f"Processing GDELT file: {file_path}")
    events = []
    
    # Common GDELT indices
    IDX_ID = 0
    IDX_DATE = 1
    IDX_A1 = 6
    IDX_A2 = 16
    IDX_CODE = 26
    IDX_LOC = 36
    IDX_LAT = 39
    IDX_LON = 40
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f, delimiter='\t')
        
        has_header = False
        headers = []
        
        for i, row in enumerate(reader):
            if i == 0 and len(row) > 0 and "GLOBALEVENTID" in row[0].upper():
                headers = [h.upper().strip() for h in row]
                has_header = True
                continue
                
            if has_header:
                try:
                    glob_id = row[headers.index("GLOBALEVENTID")] if "GLOBALEVENTID" in headers else row[IDX_ID]
                    sql_date = row[headers.index("SQLDATE")] if "SQLDATE" in headers else row[IDX_DATE]
                    a1 = row[headers.index("ACTOR1NAME")] if "ACTOR1NAME" in headers else row[IDX_A1]
                    a2 = row[headers.index("ACTOR2NAME")] if "ACTOR2NAME" in headers else row[IDX_A2]
                    code = row[headers.index("EVENTCODE")] if "EVENTCODE" in headers else row[IDX_CODE]
                    lat_str = row[headers.index("ACTIONGEO_LAT")] if "ACTIONGEO_LAT" in headers else row[IDX_LAT]
                    lon_str = row[headers.index("ACTIONGEO_LONG")] if "ACTIONGEO_LONG" in headers else row[IDX_LON]
                    loc_name = row[headers.index("ACTIONGEO_FULLNAME")] if "ACTIONGEO_FULLNAME" in headers else row[IDX_LOC]
                    source = row[headers.index("SOURCEURL")] if "SOURCEURL" in headers else (row[-1] if len(row) > 57 else "")
                except (ValueError, IndexError):
                    continue
            else:
                if len(row) < 41: continue
                glob_id = row[IDX_ID]
                sql_date = row[IDX_DATE]
                a1 = row[IDX_A1]
                a2 = row[IDX_A2]
                code = row[IDX_CODE]
                lat_str = row[IDX_LAT]
                lon_str = row[IDX_LON]
                loc_name = row[IDX_LOC]
                source = row[-1] if len(row) > 57 else ""

            # STEP 2 — FILTER EVENTS
            try:
                code_val = int(code)
                if not ((140 <= code_val <= 145) or (160 <= code_val <= 180) or (190 <= code_val <= 200)):
                    continue
            except: continue

            # STEP 3 — REMOVE INVALID LOCATIONS
            if not lat_str or not lon_str:
                continue
            try:
                lat = float(lat_str)
                lon = float(lon_str)
            except:
                continue

            # STEP 4 — CREATE EVENT OBJECTS
            evt_type = get_event_type(code)
            
            actors = []
            if a1: actors.append(a1.title())
            if a2: actors.append(a2.title())
            
            event = {
                "id": f"gdelt-{glob_id}",
                "date": parse_date(sql_date),
                "latitude": lat,
                "longitude": lon,
                "event_type": evt_type,
                "actor1": a1.title() if a1 else None,
                "actor2": a2.title() if a2 else None,
                "source": source,
                "severity": get_severity(code),
                # Compatibility fields for globe rendering
                "location": loc_name,
                "coordinates": [lon, lat],
                "actors": actors,
                "sources": [source] if source else [],
                "name": f"{evt_type} in {loc_name or 'Unknown Location'}",
                "description": f"Incident involving {a1 or 'Unknown'} and {a2 or 'Unknown'}",
                "system": "conflicts"
            }
            events.append(event)
            
    # STEP 7 — LIMIT EVENT COUNT
    events.sort(key=lambda x: str(x['date']), reverse=True)
    events = events[:1000]
    
    os.makedirs(DATASETS_DIR, exist_ok=True)
    with open(CONFLICTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Ingested {len(events)} valid conflict events to {CONFLICTS_FILE}")
    return events

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_gdelt(sys.argv[1])
    else:
        print("Usage: python gdelt_ingest.py <path_to_csv>")
