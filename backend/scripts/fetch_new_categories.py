"""
fetch_new_categories.py — Oil/Gas Chokepoints, Semiconductors, Aviation
Run: python scripts/fetch_new_categories.py
This appends new nodes/connections to existing datasets.
"""

import json, os, requests, csv, io
from datetime import datetime

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
DATASETS_DIR = os.path.join(ROOT, 'datasets')
os.makedirs(DATASETS_DIR, exist_ok=True)

# Load existing data
nodes_path = os.path.join(DATASETS_DIR, 'nodes.json')
conn_path = os.path.join(DATASETS_DIR, 'connections.json')
nodes = json.load(open(nodes_path, encoding='utf-8')) if os.path.exists(nodes_path) else []
connections = json.load(open(conn_path, encoding='utf-8')) if os.path.exists(conn_path) else []

# Remove any old entries for these new systems so we don't duplicate
NEW_SYSTEMS = {'oil_gas', 'semiconductors', 'aviation'}
nodes = [n for n in nodes if n.get('system') not in NEW_SYSTEMS]
connections = [c for c in connections if c.get('system') not in NEW_SYSTEMS]

next_id = max((n['id'] for n in nodes), default=0) + 1
next_cid = max((c['id'] for c in connections), default=0) + 1

def nid():
    global next_id; n = next_id; next_id += 1; return n
def cid():
    global next_cid; n = next_cid; next_cid += 1; return n

def add_node(name, system, ntype, lng, lat, **props):
    n = {'id': nid(), 'name': name, 'system': system, 'type': ntype,
         'coordinates': [round(lng,4), round(lat,4)], 'properties': props}
    nodes.append(n); return n

def add_conn(src_id, tgt_id, system, from_name='', to_name='', **props):
    connections.append({'id': cid(), 'source_node_id': src_id, 'target_node_id': tgt_id,
                        'system': system,
                        'properties': dict(from_name=from_name, to_name=to_name, **props)})

def find_node(system, substr):
    for n in nodes:
        if n['system'] == system and substr.lower() in n['name'].lower():
            return n
    return None


# ═══════════════════════════════════════════
# 1. OIL & GAS CHOKEPOINTS + PIPELINES
# ═══════════════════════════════════════════
print("\n🛢️  Building Oil & Gas Chokepoints layer...")

oil_nodes = [
    # ── Strategic Chokepoints ──
    ("Strait of Hormuz", "oil_gas", "chokepoint", 56.4500, 26.5600, "Iran/Oman",
     "21M bbl/day", "World's most critical oil chokepoint. Iran can blockade at will. 21% of global petroleum transit."),
    ("Strait of Malacca", "oil_gas", "chokepoint", 103.5000, 1.2600, "Singapore/Malaysia/Indonesia",
     "16M bbl/day", "Southeast Asia's oil artery. All Chinese/Japanese import tankers pass through. Piracy risk zone."),
    ("Suez Canal", "oil_gas", "chokepoint", 32.3492, 30.5852, "Egypt",
     "5.5M bbl/day", "Egypt's canal connects Red Sea to Mediterranean. Ever Given blockade showed its fragility."),
    ("Bab el-Mandeb Strait", "oil_gas", "chokepoint", 43.4100, 12.5800, "Yemen/Djibouti",
     "6.2M bbl/day", "Red Sea southern gate. Houthi attacks have diverted 50% of shipping around Africa."),
    ("Turkish Straits (Bosphorus)", "oil_gas", "chokepoint", 29.0200, 41.0700, "Turkey",
     "3M bbl/day", "Russian Black Sea oil export route. Turkey controls all tanker passage."),
    ("Danish Straits (Baltic)", "oil_gas", "chokepoint", 12.0000, 56.2000, "Denmark/Sweden",
     "3M bbl/day", "Russian Baltic oil/LNG export route via Primorsk and Ust-Luga ports."),
    ("Panama Canal", "oil_gas", "chokepoint", -79.9192, 9.0800, "Panama",
     "1M bbl/day", "LNG super-tankers from US Gulf now cannot transit due to drought-driven water shortages."),
    ("Cape of Good Hope", "oil_gas", "route_point", 18.4741, -34.3568, "South Africa",
     "~8M bbl/day (diverted)", "Alternative route for tankers avoiding Suez/Hormuz. 14-day longer transit."),

    # ── Major LNG Export Terminals ──
    ("Ras Laffan LNG (Qatar)", "oil_gas", "lng_terminal", 51.5430, 25.8715, "Qatar",
     "77M tonnes/yr", "World's largest LNG export terminal. Qatar supplies Europe, Japan, South Korea."),
    ("Sabine Pass LNG (USA)", "oil_gas", "lng_terminal", -93.8757, 29.7340, "USA",
     "30M tonnes/yr", "Largest US LNG exporter. Critical for European energy independence from Russia."),
    ("Corpus Christi LNG (USA)", "oil_gas", "lng_terminal", -97.3850, 27.7836, "USA",
     "15M tonnes/yr", "Second major US LNG export hub serving Europe and Asia."),
    ("Prelude FLNG (Australia)", "oil_gas", "lng_terminal", 127.0000, -14.0000, "Australia",
     "3.6M tonnes/yr", "World's largest floating LNG facility. Shell operates offshore WA."),
    ("Tangguh LNG (Indonesia)", "oil_gas", "lng_terminal", 133.5000, -2.8000, "Indonesia",
     "7.6M tonnes/yr", "Western Papua LNG. Supplies Japan, China, South Korea."),
    ("Yamal LNG (Russia)", "oil_gas", "lng_terminal", 72.0000, 71.5000, "Russia",
     "16.5M tonnes/yr", "Arctic LNG terminal. Heavily sanctioned. Russia redirecting to Asia via NSR."),
    ("South Hook LNG (UK)", "oil_gas", "lng_terminal", -5.0369, 51.6917, "UK",
     "20.8M bcm/yr capacity", "Wales regasification terminal. UK's primary LNG import hub."),
    ("Brunsbuttel LNG (Germany)", "oil_gas", "lng_terminal", 9.1500, 53.8900, "Germany",
     "5B m³/yr", "Germany's new LNG import terminal replacing Russian pipeline gas."),

    # ── Critical Pipelines (midpoints) ──
    ("Nord Stream Sabotage Site", "oil_gas", "pipeline_damaged", 15.5700, 55.4700, "International Waters",
     "0 (destroyed)", "Nord Stream 1&2 pipelines blown up in 2022. Attribution disputed (US/UK/Ukraine)."),
    ("Trans-Anatolian Pipeline (TANAP)", "oil_gas", "pipeline", 43.5000, 39.5000, "Turkey",
     "16B m³/yr", "Azerbaijani gas corridor to Europe. Bypasses Russia via Turkey to Greece/Italy."),
    ("BTC Pipeline (Baku-Tbilisi-Ceyhan)", "oil_gas", "pipeline", 41.0000, 40.5000, "Georgia",
     "1.2M bbl/day", "Caspian oil artery. Kazakhstan and Azerbaijan oil to Mediterranean via Georgia."),
    ("East Siberia-Pacific Ocean Pipeline", "oil_gas", "pipeline", 130.0000, 57.0000, "Russia",
     "1.6M bbl/day", "Russia's primary oil export pipeline to China and Pacific markets."),
    ("Keystone XL Route", "oil_gas", "pipeline", -100.0000, 49.0000, "USA/Canada",
     "830K bbl/day", "Canadian oil sands to US refineries. Keystone XL cancelled; original Keystone active."),

    # ── Major Refineries ──
    ("Ras Tanura Refinery (Saudi)", "oil_gas", "refinery", 50.1600, 26.7200, "Saudi Arabia",
     "550K bbl/day", "Saudi Aramco's flagship refinery. World's largest oil export terminal complex."),
    ("Ruwais Refinery (UAE)", "oil_gas", "refinery", 52.7300, 24.1100, "UAE",
     "837K bbl/day", "ADNOC refinery complex. Middle East's largest."),
    ("Abadan Refinery (Iran)", "oil_gas", "refinery", 48.2600, 30.3400, "Iran",
     "429K bbl/day", "Iran's largest refinery. Heavily sanctioned. Partially struck in 2025."),
    ("Jamnagar Refinery (India)", "oil_gas", "refinery", 70.0900, 22.4700, "India",
     "1.24M bbl/day", "World's largest oil refinery. Reliance Industries. Now processes discounted Russian oil."),
    ("Baytown Refinery (USA)", "oil_gas", "refinery", -94.9700, 29.7300, "USA",
     "584K bbl/day", "ExxonMobil's flagship US Gulf Coast refinery."),
]

oil_node_objs = {}
for item in oil_nodes:
    name, sys, ntype, lng, lat, country, capacity, desc = item
    n = add_node(name, sys, ntype, lng, lat, country=country, capacity=capacity, description=desc, last_updated=datetime.now().strftime("%Y-%m"))
    oil_node_objs[name] = n

# LNG trade routes (source → destination)
lng_routes = [
    ("Ras Laffan LNG", "South Hook LNG"),
    ("Ras Laffan LNG", "Brunsbuttel LNG"),
    ("Sabine Pass LNG", "South Hook LNG"),
    ("Corpus Christi LNG", "Brunsbuttel LNG"),
    ("Prelude FLNG", "Tangguh LNG"),  # Australia → Indonesia (example route)
]
for (a, b) in lng_routes:
    na = find_node('oil_gas', a); nb = find_node('oil_gas', b)
    if na and nb:
        add_conn(na['id'], nb['id'], 'oil_gas',
                 from_name=na['name'], to_name=nb['name'], flow_type='lng_trade')

print(f"  ✅ {sum(1 for n in nodes if n['system']=='oil_gas')} oil/gas nodes")


# ═══════════════════════════════════════════
# 2. SEMICONDUCTOR SUPPLY CHAIN
# ═══════════════════════════════════════════
print("\n💻 Building Semiconductor Supply Chain layer...")

semi_nodes = [
    # ── Silicon Feedstock ──
    ("Spruce Pine Quartz Mine (NC, USA)", "semiconductors", "raw_material", -82.0650, 35.9204, "USA",
     "Ultra-pure quartz", "Only source of hyper-pure quartz sand needed for silicon wafer crucibles. A storm here stops global chip production."),
    ("Hemlock Semiconductor (USA)", "semiconductors", "polysilicon", -84.2334, 43.4136, "USA",
     "20K MT/yr", "Primary polysilicon producer for US chip industry. Joint venture (Dow/Corning)."),
    ("GCL-Poly Polysilicon (China)", "semiconductors", "polysilicon", 116.3912, 39.9075, "China",
     "100K MT/yr", "China produces 80% of world polysilicon. Xinjiang supply chain controversy."),

    # ── Wafer Manufacturers ──
    ("Siltronic (Germany)", "semiconductors", "wafer", 12.7222, 48.0900, "Germany",
     "300mm silicon wafers", "Leading European silicon wafer supplier to Samsung, Intel, TSMC."),
    ("Shin-Etsu Chemical (Japan)", "semiconductors", "wafer", 136.9066, 35.1815, "Japan",
     "30% global share", "World's largest silicon wafer manufacturer. Based in Naoetsu, Japan."),
    ("SK Siltron (South Korea)", "semiconductors", "wafer", 128.3300, 35.8700, "South Korea",
     "300mm wafers", "Samsung subsidiary. Major wafer supplier."),

    # ── Chip Fabs (most critical) ──
    ("TSMC Fab 18 (3nm, Taiwan)", "semiconductors", "fab", 120.2000, 24.7500, "Taiwan",
     "3nm/2nm advanced", "Most advanced chips on Earth. Makes chips for Apple A17, Nvidia H100. Taiwan invasion = global tech crisis."),
    ("TSMC Fab — Hsinchu Science Park", "semiconductors", "fab", 120.9765, 24.7861, "Taiwan",
     "5nm-28nm", "TSMC headquarters complex. Produces 60%+ of world's advanced logic chips."),
    ("TSMC Arizona Fab (Phoenix)", "semiconductors", "fab", -112.0740, 33.4484, "USA",
     "4nm/3nm (2025)", "First advanced TSMC fab in USA. $40B investment. First 4nm chips expected 2025."),
    ("Samsung S3 Fab (Hwaseong)", "semiconductors", "fab", 126.9758, 37.2000, "South Korea",
     "3nm GAA", "Samsung's most advanced fab. World's first 3nm GAA production."),
    ("Samsung Taylor Fab (Texas)", "semiconductors", "fab", -97.4097, 30.5724, "USA",
     "4nm/2nm (planned)", "Samsung's $17B Texas fab. First chips expected 2026."),
    ("Intel Fab 34 (Ireland)", "semiconductors", "fab", -6.9370, 53.3498, "Ireland",
     "Intel 4 (7nm)", "Intel's European advanced fab. Key for EU chip sovereignty."),
    ("Intel Arizona Fab 52/62", "semiconductors", "fab", -112.0740, 33.4484, "USA",
     "Intel 18A (2024)", "Intel's $20B US fab investment. Targeting '18A' process leadership vs TSMC."),
    ("SMIC N+1 Fab (Shanghai)", "semiconductors", "fab", 121.4737, 31.2304, "China",
     "7nm (unofficial)", "China's most advanced fab. Limited to 7nm without ASML EUV. Embargo-constrained."),
    ("GlobalFoundries Dresden", "semiconductors", "fab", 13.7372, 51.0504, "Germany",
     "22nm/12nm", "Key European fab for automotive chips. 40% of European auto chip supply."),
    ("SK Hynix Fab (Icheon)", "semiconductors", "fab", 127.4429, 37.2750, "South Korea",
     "HBM3E DRAM", "World's largest HBM3 memory chip producer. Provides memory for Nvidia H100."),
    ("Micron Fab (Boise, Idaho)", "semiconductors", "fab", -116.1629, 43.6150, "USA",
     "DRAM/NAND", "Major US DRAM and NAND memory producer. $15B Idaho expansion."),

    # ── Critical Equipment Makers ──
    ("ASML HQ (Veldhoven, Netherlands)", "semiconductors", "equipment", 5.4069, 51.4168, "Netherlands",
     "EUV lithography", "ONLY maker of EUV lithography machines. Without ASML, no chips < 7nm anywhere on Earth. Export-controlled."),
    ("Tokyo Electron (Japan)", "semiconductors", "equipment", 139.7671, 35.6762, "Japan",
     "Etch/deposition", "World's second largest semiconductor equipment maker. Critical for all fab processes."),
    ("Applied Materials (USA)", "semiconductors", "equipment", -121.9886, 37.3861, "USA",
     "Deposition/CMP", "Silicon Valley's largest chipmaking equipment company."),
    ("KLA Corporation (USA)", "semiconductors", "equipment", -121.9620, 37.3539, "USA",
     "Inspection/metrology", "Quality control equipment maker. Can't make chips without KLA machines."),
    ("Lam Research (USA)", "semiconductors", "equipment", -121.9620, 37.5400, "USA",
     "Etch systems", "Critical etch equipment. Export-restricted to China."),

    # ── Package/Assembly ──
    ("ASE Group (Kaohsiung, Taiwan)", "semiconductors", "assembly", 120.3005, 22.6273, "Taiwan",
     "OSAT #1", "World's largest chip packaging/testing house. All advanced chips pass through here."),
    ("Amkor Technology (Philippines)", "semiconductors", "assembly", 120.9842, 14.5995, "Philippines",
     "OSAT #3", "Major chip assembly site in Manila. Risk from Philippines-China tension."),

    # ── Regional Cluster Hubs ──
    ("Silicon Valley Cluster", "semiconductors", "cluster", -122.0862, 37.3861, "USA",
     "NVIDIA/Intel/AMD/Qualcomm/Apple", "Design hub for world's most advanced chips. Fabless companies."),
    ("Hsinchu Science Park (Taiwan)", "semiconductors", "cluster", 120.9765, 24.7861, "Taiwan",
     "TSMC/MediaTek/UMC", "World's most strategically important 1km² patch of land for global tech."),
    ("Dresden Silicon Saxony (Germany)", "semiconductors", "cluster", 13.7372, 51.0504, "Germany",
     "TSMC/Infineon/GlobalFoundries", "EU's largest semiconductor cluster. Intel and TSMC investing €40B+."),
]

for item in semi_nodes:
    name, sys, ntype, lng, lat, country, capacity, desc = item
    add_node(name, sys, ntype, lng, lat, country=country, spec=capacity, description=desc,
             last_updated=datetime.now().strftime("%Y-%m"))

# Supply chain flows
semi_flows = [
    ("Spruce Pine Quartz", "Shin-Etsu Chemical"),
    ("Shin-Etsu Chemical", "TSMC Fab 18"),
    ("ASML HQ", "TSMC Fab 18"),
    ("ASML HQ", "Samsung S3"),
    ("TSMC Fab 18", "ASE Group"),
    ("TSMC Fab — Hsinchu", "ASE Group"),
    ("Samsung S3", "Silicon Valley Cluster"),
    ("TSMC Arizona", "Silicon Valley Cluster"),
    ("SK Hynix Fab", "Silicon Valley Cluster"),
    ("SMIC N+1", "Hsinchu Science Park"),
]
for (a, b) in semi_flows:
    na = find_node('semiconductors', a); nb = find_node('semiconductors', b)
    if na and nb:
        add_conn(na['id'], nb['id'], 'semiconductors',
                 from_name=na['name'], to_name=nb['name'], flow_type='supply_chain')

print(f"  ✅ {sum(1 for n in nodes if n['system']=='semiconductors')} semiconductor nodes")


# ═══════════════════════════════════════════
# 3. AVIATION CARGO CORRIDORS
# ═══════════════════════════════════════════
print("\n✈️  Building Aviation Cargo Corridors layer...")

aviation_nodes = [
    # ── Top Cargo Airports ──
    ("Hong Kong International (HKG)", "aviation", "cargo_hub", 113.9145, 22.3080, "Hong Kong",
     "4.9M MT/yr", "World's busiest cargo airport. Gateway for Chinese electronics to the world."),
    ("Memphis International (MEM)", "aviation", "cargo_hub", -89.9767, 35.0424, "USA",
     "4.3M MT/yr", "FedEx World Hub. US domestic distribution backbone."),
    ("Shanghai Pudong (PVG)", "aviation", "cargo_hub", 121.8083, 31.1434, "China",
     "3.8M MT/yr", "China's primary air cargo hub. Tesla, Apple exports."),
    ("Anchorage (ANC)", "aviation", "cargo_hub", -149.9961, 61.1744, "USA",
     "2.9M MT/yr", "The world's fuel stop. Arctic great-circle routes between Asia and NA pass through Anchorage."),
    ("Incheon International (ICN)", "aviation", "cargo_hub", 126.4509, 37.4602, "South Korea",
     "3.1M MT/yr", "Northeast Asia cargo hub. Samsung/LG electronics exports to US/Europe."),
    ("Dubai World Central (DWC)", "aviation", "cargo_hub", 55.1712, 24.8969, "UAE",
     "2.7M MT/yr", "Emirates SkyCargo hub. Middle East-Asia-Africa distribution center."),
    ("Frankfurt Airport (FRA)", "aviation", "cargo_hub", 8.5622, 50.0379, "Germany",
     "2.2M MT/yr", "Europe's largest cargo airport. Pharma cold chain hub (Pfizer, BioNTech)."),
    ("Louisville (SDF)", "aviation", "cargo_hub", -85.7366, 38.1744, "USA",
     "2.6M MT/yr", "UPS Worldport — world's largest automated package handling facility."),
    ("Chicago O'Hare (ORD)", "aviation", "cargo_hub", -87.9048, 41.9742, "USA",
     "1.8M MT/yr", "US Midwest cargo hub. Critical for agricultural commodity air freight."),
    ("Singapore Changi (SIN)", "aviation", "cargo_hub", 103.9915, 1.3644, "Singapore",
     "2.1M MT/yr", "Southeast Asia cargo center. Pharma, electronics cold chain."),
    ("Tokyo Narita (NRT)", "aviation", "cargo_hub", 140.3929, 35.7720, "Japan",
     "2.0M MT/yr", "Japan cargo hub. Auto parts, electronics, seafood exports."),
    ("Los Angeles (LAX)", "aviation", "cargo_hub", -118.4085, 33.9425, "USA",
     "2.5M MT/yr", "Asia-Pacific US gateway. Amazon air freight hub."),
    ("Amsterdam Schiphol (AMS)", "aviation", "cargo_hub", 4.7638, 52.3105, "Netherlands",
     "1.7M MT/yr", "Flowers, pharma. Air France-KLM Cargo major hub."),
    ("Doha Hamad (DOH)", "aviation", "cargo_hub", 51.6082, 25.2731, "Qatar",
     "1.4M MT/yr", "Qatar Airways cargo hub. Middle East pharma and luxury goods."),
    ("Liege Airport (LGG)", "aviation", "cargo_hub", 5.6433, 50.6374, "Belgium",
     "1.2M MT/yr", "Amazon, TNT, DHL European hub. Night flight unrestricted."),
    ("Zhengzhou (CGO)", "aviation", "cargo_hub", 113.8408, 34.5197, "China",
     "1.1M MT/yr", "iPhone shipping hub — Foxconn factory next to airport."),

    # ── No-Fly Zones (shown as warning markers) ──
    ("Ukraine Airspace — Active No-Fly Zone", "aviation", "no_fly_zone", 31.0000, 49.0000, "Ukraine",
     "CLOSED since 2022", "Ukrainian airspace closed since Russian invasion. Major European routing disruption."),
    ("Russian Airspace — Banned for NATO", "aviation", "no_fly_zone", 60.0000, 58.0000, "Russia",
     "CLOSED for Western airlines", "EU/US airlines banned from Russian airspace. 30% longer routes to Asia. $2B/yr extra fuel costs."),
    ("Iran Airspace — Partially Closed", "aviation", "no_fly_zone", 53.0000, 32.5000, "Iran",
     "NOTAM ACTIVE", "Iran-Israel-US war: NOTAM active closing Iranian airspace. Major Gulf route disruptions."),
    ("Israeli Airspace — Military Ops", "aviation", "no_fly_zone", 35.0000, 31.5000, "Israel",
     "Commercial NOTAM active", "Israeli military ops: civilian airspace restrictions active. Airlines rerouting."),
    ("Houthi Threat Zone — Red Sea", "aviation", "threat_zone", 43.0000, 15.0000, "Yemen",
     "Risk Advisory", "Houthi missiles can reach 40,000ft. Airlines avoiding Red Sea corridor. SIGMET issued."),
]

for item in aviation_nodes:
    name, sys, ntype, lng, lat, country, vol, desc = item
    add_node(name, sys, ntype, lng, lat, country=country, annual_cargo_volume=vol, description=desc,
             last_updated=datetime.now().strftime("%Y-%m"))

# Major air cargo corridors
air_corridors = [
    ("Hong Kong International", "Los Angeles"),
    ("Shanghai Pudong", "Anchorage"),
    ("Anchorage", "Memphis International"),
    ("Incheon International", "Los Angeles"),
    ("Dubai World Central", "Frankfurt Airport"),
    ("Frankfurt Airport", "Hong Kong International"),
    ("Singapore Changi", "Dubai World Central"),
    ("Shanghai Pudong", "Frankfurt Airport"),
    ("Hong Kong International", "Amsterdam Schiphol"),
    ("Zhengzhou", "Louisville"),
    ("Tokyo Narita", "Anchorage"),
    ("Louisville", "Frankfurt Airport"),
]
for (a, b) in air_corridors:
    na = find_node('aviation', a); nb = find_node('aviation', b)
    if na and nb:
        add_conn(na['id'], nb['id'], 'aviation',
                 from_name=na['name'], to_name=nb['name'], flow_type='air_corridor',
                 intensity=2.0, route_type='great_circle')

print(f"  ✅ {sum(1 for n in nodes if n['system']=='aviation')} aviation nodes")

# ═══════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════
print(f"\n📊 Grand total: {len(nodes)} nodes, {len(connections)} connections")
json.dump(nodes, open(nodes_path, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
json.dump(connections, open(conn_path, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print("✅ Saved nodes.json and connections.json")

by_sys = {}
for n in nodes:
    s = n['system']; by_sys[s] = by_sys.get(s, 0) + 1
for s, c in sorted(by_sys.items()):
    print(f"   {s}: {c}")
