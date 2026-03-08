import re
from typing import Dict, Any, Optional

# STEP 1: ALLOWED EVENT TYPES
VALID_CATEGORIES = [
    "Airstrike",
    "Missile Strike",
    "Drone Strike",
    "Bombing",
    "Armed Clash",
    "Battle",
    "Terrorist Attack",
    "Insurgent Attack",
    "Protest",
    "Riot",
    "Civil Unrest"
]

# STEP 2: REQUIRED ACTION VERBS
REQUIRED_VERBS = [
    # Military
    "launched airstrike", "fired missile", "missile strike", "bomb exploded", 
    "bombing attack", "artillery strike", "troops deployed", "armed clash", 
    "battle erupted", "gunfight", "military raid", "airstrike",
    # Civil unrest
    "protest erupted", "demonstrators gathered", "riot broke out", 
    "clashed with police", "crowd stormed", "violent protest"
]

# STEP 3: DOMAIN WHITELIST
DOMAIN_WHITELIST = [
    "reuters.com",
    "bbc.com",
    "apnews.com",
    "aljazeera.com",
    "cnn.com",
    "theguardian.com",
    "nytimes.com",
    "washingtonpost.com"
]

# STEP 5: ACTOR VALIDATION
VALID_ACTORS = [
    "military forces",
    "police",
    "government forces",
    "armed groups",
    "militias",
    "terrorist organizations",
    "idf", "irgc", "hamas", "hezbollah", "taliban", "pla", "army", "navy", "guard", "force", "rebel", "insurgent", "movement", "defense"
]

INVALID_ACTORS = [
    "delhi", "hospital", "student", "boss", "lawyer", "actor", "celebrity", "israeli", "expatriate", "american", "russian", "ukrainian"
]

def _compile_regex(word_list):
    pattern = r'\b(?:' + '|'.join(re.escape(word) for word in word_list) + r')\b'
    return re.compile(pattern, re.IGNORECASE)

VERB_REGEX = _compile_regex(REQUIRED_VERBS)
INVALID_ACTOR_REGEX = _compile_regex(INVALID_ACTORS)

def analyze_event(raw_event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # Combine text for searching
    text_content = f"{raw_event.get('name', '')} {raw_event.get('title', '')} {raw_event.get('summary', '')} {raw_event.get('description', '')} {raw_event.get('event_type', '')}".lower()

    # STEP 3: DOMAIN WHITELIST
    raw_src = raw_event.get('sources', raw_event.get('source', []))
    if isinstance(raw_src, str):
        sources = [s.strip() for s in raw_src.split(',')]
    else:
        sources = raw_src
    sources = [s for s in sources if s]

    domain_passed = False
    for src in sources:
        src_lower = src.lower()
        if any(domain in src_lower for domain in DOMAIN_WHITELIST):
            domain_passed = True
            break
            
    # Always allow our manually curated sources or structural ACLED data if it passed through
    for src in sources:
        src_lower = src.lower()
        if "acled" in src_lower or "isw" in src_lower or "idf" in src_lower or "un " in src_lower or "live news" in src_lower or "local intel" in src_lower:
            domain_passed = True
            
    if not domain_passed:
        return None

    # STEP 2: REQUIRED ACTION VERBS
    if not VERB_REGEX.search(text_content):
        return None

    # STEP 4: LOCATION VALIDATION
    location_name = raw_event.get('location', '')
    if not location_name:
        return None
        
    loc_lower = location_name.lower()
    if loc_lower not in text_content:
        parts = [p for p in loc_lower.split() if len(p) > 3]
        if not parts:
            if loc_lower not in text_content:
                return None
        else:
            if not any(p in text_content for p in parts):
                return None

    # STEP 5: ACTOR VALIDATION
    raw_actors = raw_event.get('actors', [])
    if isinstance(raw_actors, str):
        raw_actors = [raw_actors]
        
    valid_actors = []
    for actor in raw_actors:
        if not actor or len(actor) < 3:
            continue
        actor_lower = actor.lower()
        
        if INVALID_ACTOR_REGEX.search(actor_lower):
            continue
            
        is_valid = False
        if any(v in actor_lower for v in VALID_ACTORS):
            is_valid = True
                
        if is_valid:
            valid_actors.append(actor)
            
    if not valid_actors:
        return None
        
    # STEP 1: EVENT TYPE DETERMINATION
    evt_type_lower = raw_event.get("event_type", "").lower()
    best_category = None
    if "airstrike" in evt_type_lower: best_category = "Airstrike"
    elif "missile" in evt_type_lower: best_category = "Missile Strike"
    elif "drone" in evt_type_lower: best_category = "Drone Strike"
    elif "bombing" in evt_type_lower: best_category = "Bombing"
    elif "clash" in evt_type_lower: best_category = "Armed Clash"
    elif "battle" in evt_type_lower: best_category = "Battle"
    elif "terror" in evt_type_lower: best_category = "Terrorist Attack"
    elif "insurgent" in evt_type_lower: best_category = "Insurgent Attack"
    elif "protest" in evt_type_lower: best_category = "Protest"
    elif "riot" in evt_type_lower: best_category = "Riot"
    elif "unrest" in evt_type_lower: best_category = "Civil Unrest"
    else:
        if "airstrike" in text_content: best_category = "Airstrike"
        elif "missile" in text_content: best_category = "Missile Strike"
        elif "bombing" in text_content: best_category = "Bombing"
        elif "battle" in text_content: best_category = "Battle"
        elif "clash" in text_content: best_category = "Armed Clash"
        elif "riot" in text_content: best_category = "Riot"
        elif "protest" in text_content: best_category = "Protest"
        else:
            best_category = "Armed Clash"

    # STEP 7: FINAL EVENT CREATION
    severity = str(raw_event.get('severity', 'medium'))
    processed_event = {
        "id": raw_event.get('id', ''),
        "event_type": best_category,
        "location": location_name,
        "latitude": raw_event.get('coordinates', [0,0])[1] if 'coordinates' in raw_event else raw_event.get('latitude', 0),
        "longitude": raw_event.get('coordinates', [0,0])[0] if 'coordinates' in raw_event else raw_event.get('longitude', 0),
        "actors": valid_actors,
        "severity": severity,
        "sources": sources,
        "summary": raw_event.get('description', raw_event.get('summary', '')),
        # Backwards compatibility layer
        "name": raw_event.get('name', raw_event.get('title', f"{best_category} incident")),
        "description": raw_event.get('description', raw_event.get('summary', '')),
        "source": sources[0] if sources else "Unknown",
        "coordinates": raw_event.get('coordinates', [raw_event.get('longitude', 0), raw_event.get('latitude', 0)]),
        "date": raw_event.get('date', ''),
        "system": "conflicts"
    }

    return processed_event
