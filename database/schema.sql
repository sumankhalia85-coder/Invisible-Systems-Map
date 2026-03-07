-- database/schema.sql
-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Table for system nodes (ports, mines, power plants, etc.)
CREATE TABLE IF NOT EXISTS nodes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- e.g., 'port', 'mine', 'data_center', 'power_plant'
    system VARCHAR(50) NOT NULL, -- e.g., 'shipping', 'energy', 'minerals', 'cables', 'food'
    location GEOMETRY(Point, 4326) NOT NULL,
    properties JSONB DEFAULT '{}'::jsonb
);

-- Note: We create indexes for spatial queries
CREATE INDEX IF NOT EXISTS nodes_location_idx ON nodes USING GIST (location);
CREATE INDEX IF NOT EXISTS nodes_system_idx ON nodes (system);

-- Table for system connections (shipping routes, cables, etc.)
CREATE TABLE IF NOT EXISTS connections (
    id SERIAL PRIMARY KEY,
    source_node_id INTEGER REFERENCES nodes(id),
    target_node_id INTEGER REFERENCES nodes(id),
    type VARCHAR(50) NOT NULL,
    system VARCHAR(50) NOT NULL,
    path GEOMETRY(LineString, 4326), -- Optional: precise path if known, otherwise inferred
    intensity FLOAT DEFAULT 1.0, -- Representing volume/capacity
    properties JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS connections_path_idx ON connections USING GIST (path);
CREATE INDEX IF NOT EXISTS connections_system_idx ON connections (system);
