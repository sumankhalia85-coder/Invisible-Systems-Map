import json
import os
import sys

# Add parent dir to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session  # type: ignore[import-not-found]
from app.database import engine, SessionLocal  # type: ignore[import-not-found]
from app.models import Node, Connection, Base  # type: ignore[import-not-found]

def load_data():
    db = SessionLocal()
    
    try:
        # Recreate tables (drop all) for clean ingestion
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("Recreated database tables.")

        datasets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'datasets')
        
        # 1. Load Nodes
        nodes_path = os.path.join(datasets_dir, 'nodes.json')
        with open(nodes_path, 'r') as f:
            nodes_data = json.load(f)
            
        print(f"Loading {len(nodes_data)} nodes...")
        for n in nodes_data:
            lng, lat = n['coordinates']
            # PostGIS expects POINT(lon lat)
            point_wkt = f"POINT({lng} {lat})"
            
            db_node = Node(
                id=n['id'], # Forcing ID for relationships
                name=n['name'],
                type=n['type'],
                system=n['system'],
                location=point_wkt,
                properties=n.get('properties', {})
            )
            db.add(db_node)
            
        db.commit()
        print("Nodes loaded successfully.")

        # 2. Load Connections
        connections_path = os.path.join(datasets_dir, 'connections.json')
        with open(connections_path, 'r') as f:
            conns_data = json.load(f)
            
        print(f"Loading {len(conns_data)} connections...")
        for c in conns_data:
            db_conn = Connection(
                source_node_id=c['source_node_id'],
                target_node_id=c['target_node_id'],
                type=c['type'],
                system=c['system'],
                intensity=c.get('intensity', 1.0),
                properties=c.get('properties', {})
            )
            db.add(db_conn)
            
        db.commit()
        print("Connections loaded successfully.")
        
    except Exception as e:
        print(f"Error during ingestion: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    load_data()
