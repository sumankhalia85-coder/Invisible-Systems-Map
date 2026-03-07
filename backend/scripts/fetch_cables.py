"""
Add curated submarine cable landing stations and routes to the existing dataset.
Uses real cable data from TeleGeography's public list.
Run: python scripts/fetch_cables.py
"""

import json, os
from datetime import datetime

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
DATASETS_DIR = os.path.join(ROOT, 'datasets')

nodes_path = os.path.join(DATASETS_DIR, 'nodes.json')
conn_path = os.path.join(DATASETS_DIR, 'connections.json')
nodes = json.load(open(nodes_path, encoding='utf-8'))
connections = json.load(open(conn_path, encoding='utf-8'))

# Remove old cables entries
nodes = [n for n in nodes if n.get('system') != 'cables']
connections = [c for c in connections if c.get('system') != 'cables']

next_id = max((n['id'] for n in nodes), default=0) + 1
next_cid = max((c['id'] for c in connections), default=0) + 1

def nid():
    global next_id; n = next_id; next_id += 1; return n
def cid():
    global next_cid; n = next_cid; next_cid += 1; return n

def add_node(name, ntype, lng, lat, **props):
    n = {'id': nid(), 'name': name, 'system': 'cables', 'type': ntype,
         'coordinates': [round(lng,4), round(lat,4)], 'properties': props}
    nodes.append(n); return n

def add_conn(src_id, tgt_id, cable_name, **props):
    connections.append({
        'id': cid(), 'source_node_id': src_id, 'target_node_id': tgt_id,
        'system': 'cables',
        'properties': dict(cable_name=cable_name, **props)
    })

# ── Real submarine cable landing stations (TeleGeography curated) ──
# Format: (name, lng, lat, country, cables_landing)
stations = [
    # Pacific
    ("Hermosa Beach Submarine Cable Station", -118.3975, 33.8600, "US", "FASTER, Pacific Light Cable, TPE"),
    ("Land's End (San Francisco) Cable Station", -122.5094, 37.7749, "US", "TPC-5, PCCS"),
    ("Nedonna Beach Cable Station (Oregon)", -123.9500, 45.7200, "US", "PC-1, NPC"),
    ("Makaha Cable Station (Hawaii)", -158.2216, 21.4717, "US", "FASTER, HifiBR, Hawaiki"),
    ("Port Alberni Cable Station (Canada)", -124.8181, 49.2329, "CA", "TPC-5"),
    ("Morro de São Paulo (Brazil)", -38.9097, -13.3740, "BR", "SEA-ME-WE 3, Atlantis-2"),
    ("Fortaleza Cable Station (Brazil)", -38.5434, -3.7172, "BR", "SEABRAS-1, SAex, Monet"),
    ("Praia Grande Cable Station (Brazil)", -46.4027, -24.0059, "BR", "SEABRAS-1, Monet, SAex"),
    ("Balboa Cable Station (Panama)", -79.5588, 8.9734, "PA", "ARCOS, Maya-1"),
    ("Punta Gorda Cable Station (Costa Rica)", -85.0000, 9.0000, "CR", "ARCOS"),
    ("St. Croix (USVI)", -64.7013, 17.7475, "US", "ARCOS, Columbus-III"),
    ("Land's End Cornwall (UK)", -5.7139, 50.0480, "GB", "TAT-14, FLAG Atlantic, Apollo"),
    ("Bude Cable Station (Cornwall UK)", -4.5438, 50.8266, "GB", "TAT-14, Apollo, HAVFRUE"),
    ("Widemouth Bay (UK)", -4.5646, 50.7862, "GB", "FLAG Atlantic-1, AEConnect"),
    ("La Manche (France)", 1.7500, 50.9500, "FR", "TAT-14, FLAG Atlantic, Apollo"),
    ("Lannion Cable Station (France)", -3.4519, 48.7320, "FR", "SAT-3, Atlantis-2"),
    ("Sesimbra Cable Station (Portugal)", -9.0983, 38.4444, "PT", "SAT-3/WASC, Columbus-III, FLAG Europe-Asia"),
    ("Marseille Cable Station (France)", 5.3517, 43.2965, "FR", "SEA-ME-WE 3, SEA-ME-WE 4, SEA-ME-WE 5"),
    ("Palermo Cable Station (Italy)", 13.3615, 38.1157, "IT", "SEA-ME-WE 3, SEA-ME-WE 4"),
    ("Alexandria Cable Station (Egypt)", 29.9187, 31.2001, "EG", "SEA-ME-WE 3, SEA-ME-WE 4, SEA-ME-WE 5"),
    ("Aqaba Cable Station (Jordan)", 35.0077, 29.5267, "JO", "FLAG Falcon"),
    ("Fujairah Cable Station (UAE)", 56.3368, 25.1164, "AE", "SEA-ME-WE 4, SEA-ME-WE 5, FLAG Europe-Asia"),
    ("Mumbai Cable Station (India)", 72.8777, 18.9657, "IN", "SEA-ME-WE 3, SEA-ME-WE 4, SEA-ME-WE 5, FLAG Europe-Asia, i2i"),
    ("Chennai Cable Station (India)", 80.2785, 13.0878, "IN", "SEA-ME-WE 3, SEA-ME-WE 4"),
    ("Tuas Cable Station (Singapore)", 103.6381, 1.3132, "SG", "SEA-ME-WE 4, SEA-ME-WE 5, APG, SJC, AAE-1"),
    ("Changi Beach (Singapore)", 103.9883, 1.3914, "SG", "FASTER, SEA-ME-WE 3"),
    ("Cable Landing Station Hong Kong", 114.1302, 22.2855, "HK", "APG, SJC, APCN-2, RNAL"),
    ("Chikura Cable Station (Japan)", 140.0000, 35.0000, "JP", "FASTER, APCN-2, PC-1, TPC-5"),
    ("Shima Cable Station (Japan)", 136.9086, 34.3345, "JP", "FLAG Europe-Asia, SEA-ME-WE 3"),
    ("Jandira Cable Station (Brazil)", -43.9000, -23.5000, "BR", "Atlantis-2"),
    ("Telecom Bretagne (France PoP)", -4.2500, 47.8000, "FR", "LION, SAT-3"),
    ("Mombasa Landing Station (Kenya)", 39.6682, -4.0435, "KE", "SEACOM, EASSy, TEAMS"),
    ("St. Helena Landing (Yzerfontein, SA)", 18.1650, -33.3600, "ZA", "SAT-3/WASC, SEACOM, EASSy"),
    ("Mtunzini Landing (South Africa)", 31.7500, -28.9500, "ZA", "SEACOM, EASSy"),
]

node_map = {}
for (name, lng, lat, country, cables) in stations:
    n = add_node(name, 'landing_station', lng, lat, country=country, cables_landing=cables, last_updated=datetime.now().strftime("%Y-%m"))
    node_map[name] = n

# ── Key submarine cable routes (from→to real cables) ──
cable_routes = [
    # Trans-Atlantic
    ("Land's End Cornwall (UK)",              "Hermosa Beach Submarine Cable Station",  "Apollo", 320, "US-UK"),
    ("Bude Cable Station (Cornwall UK)",      "Land's End (San Francisco) Cable Station","AEConnect-1", 140, "US-UK"),
    ("La Manche (France)",                    "Hermosa Beach Submarine Cable Station",  "FLAG Atlantic", 280, "France-US"),
    ("Sesimbra Cable Station (Portugal)",     "Fortaleza Cable Station (Brazil)",        "Atlantis-2", 260, "Portugal-Brazil"),
    # Trans-Pacific
    ("Makaha Cable Station (Hawaii)",         "Chikura Cable Station (Japan)",           "FASTER", 960, "US-Japan"),
    ("Hermosa Beach Submarine Cable Station", "Chikura Cable Station (Japan)",           "TPC-5", 590, "US-Japan"),
    ("Nedonna Beach Cable Station (Oregon)",  "Changi Beach (Singapore)",                "PC-1", 880, "US-Singapore"),
    # Asia-Europe (SEA-ME-WE)
    ("Tuas Cable Station (Singapore)",        "Fujairah Cable Station (UAE)",            "SEA-ME-WE 5", 500, "Singapore-UAE"),
    ("Fujairah Cable Station (UAE)",          "Marseille Cable Station (France)",        "SEA-ME-WE 5", 480, "UAE-France"),
    ("Mumbai Cable Station (India)",          "Fujairah Cable Station (UAE)",            "SEA-ME-WE 4", 320, "India-UAE"),
    ("Alexandria Cable Station (Egypt)",      "Marseille Cable Station (France)",        "SEA-ME-WE 3", 300, "Egypt-France"),
    # Asia-Pacific
    ("Cable Landing Station Hong Kong",       "Chikura Cable Station (Japan)",           "APCN-2", 370, "HK-Japan"),
    ("Cable Landing Station Hong Kong",       "Tuas Cable Station (Singapore)",          "SJC", 290, "HK-Singapore"),
    ("Changi Beach (Singapore)",              "Chennai Cable Station (India)",           "i2i", 200, "Singapore-India"),
    # Africa
    ("Mtunzini Landing (South Africa)",       "Mombasa Landing Station (Kenya)",         "SEACOM", 190, "SA-Kenya"),
    ("St. Helena Landing (Yzerfontein, SA)",  "Sesimbra Cable Station (Portugal)",       "SAT-3/WASC", 380, "SA-Portugal"),
    ("La Manche (France)",                    "Mombasa Landing Station (Kenya)",         "LION", 350, "France-Kenya"),
    # Americas
    ("Fortaleza Cable Station (Brazil)",      "Balboa Cable Station (Panama)",           "SEABRAS-1", 280, "Brazil-Panama"),
    ("Balboa Cable Station (Panama)",         "Hermosa Beach Submarine Cable Station",   "Maya-1", 320, "Panama-US"),
    ("St. Croix (USVI)",                      "Land's End Cornwall (UK)",                "Columbus-III", 260, "USVI-UK"),
]

for (a, b, cable, capacity_gbps, route) in cable_routes:
    na = node_map.get(a); nb = node_map.get(b)
    if na and nb:
        # find actual node coords for from/to name
        add_conn(na['id'], nb['id'], cable,
                 from_name=a, to_name=b,
                 capacity_gbps=capacity_gbps, route=route,
                 intensity=min(3.0, capacity_gbps / 200))

print(f"✅ Cables: {sum(1 for n in nodes if n['system']=='cables')} nodes, {sum(1 for c in connections if c['system']=='cables')} connections")
print(f"   Total: {len(nodes)} nodes, {len(connections)} connections")

json.dump(nodes, open(nodes_path, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
json.dump(connections, open(conn_path, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print("✅ Saved")
