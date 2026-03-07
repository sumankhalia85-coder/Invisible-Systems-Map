/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import React from 'react';
import type { MapViewState } from '@deck.gl/core';
import DeckGL from '@deck.gl/react';
import { Map } from 'react-map-gl/maplibre';
import { ArcLayer, ScatterplotLayer } from '@deck.gl/layers';

interface MapComponentProps {
  layersData: any;
  activeSystems: Record<string, boolean>;
  onNodeClick: (nodeInfo: any) => void;
  conflictsData?: any[];
}

const INITIAL_VIEW_STATE: MapViewState = {
  longitude: 10,
  latitude: 20,
  zoom: 1.8,
  pitch: 25,
  bearing: 0
};

// Deep cinematic dark map — navy ocean, muted land
const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json';

// Cinematic color palettes per system [r,g,b] node · [r,g,b,a] glow · [[r,g,b,a],[r,g,b,a]] arc
const SYSTEM_PALETTE: Record<string, { node: [number,number,number], glow: [number,number,number,number], arc: [[number,number,number,number],[number,number,number,number]] }> = {
  shipping:       { node: [34,211,238],  glow: [34,211,238,40],   arc: [[34,211,238,210],[6,182,212,130]] },
  cables:         { node: [99,102,241],  glow: [99,102,241,40],   arc: [[99,102,241,200],[129,140,248,120]] },
  energy:         { node: [251,191,36],  glow: [251,191,36,40],   arc: [[251,191,36,210],[245,158,11,130]] },
  minerals:       { node: [167,139,250], glow: [167,139,250,40],  arc: [[167,139,250,200],[196,181,253,120]] },
  food:           { node: [52,211,153],  glow: [52,211,153,40],   arc: [[52,211,153,200],[16,185,129,120]] },
  oil_gas:        { node: [249,115,22],  glow: [249,115,22,40],   arc: [[249,115,22,220],[234,88,12,140]] },   // orange fire
  semiconductors: { node: [6,182,212],   glow: [6,182,212,40],    arc: [[6,182,212,200],[8,145,178,120]] },    // electric cyan
  aviation:       { node: [139,92,246],  glow: [139,92,246,40],   arc: [[139,92,246,180],[109,40,217,100]] },  // purple
};

// Conflict event type → color [r,g,b,a]
const CONFLICT_COLORS: Record<string, [number,number,number,number]> = {
  battle:            [239, 68,  68,  230],
  airstrike:         [249, 115, 22,  230],
  missile:           [234, 179, 8,   230],
  bombing:           [168, 85,  247, 230],
  civilian_violence: [236, 72,  153, 230],
  protest:           [59,  130, 246, 230],
  riot:              [20,  184, 166, 230],
  geopolitical:      [148, 163, 184, 200],
  massacre:          [127, 29,  29,  230],
  default:           [255, 255, 255, 180],
};

const SEVERITY_RADIUS: Record<string, number> = {
  low: 6, medium: 9, high: 14, critical: 20
};

export default function MapComponent({ layersData, activeSystems, onNodeClick, conflictsData = [] }: MapComponentProps) {

  const createLayers = () => {
    const layers: any[] = [];

    // ── Infrastructure layers ──
    Object.keys(activeSystems).forEach(system => {
      if (system === 'conflicts') return;
      if (!activeSystems[system]) return;
      const systemData = layersData[system];
      if (!systemData) return;
      const palette = SYSTEM_PALETTE[system];
      if (!palette) return;

      // Outer glow layer (bigger, semi-transparent)
      if (systemData.nodes?.features?.length > 0) {
        layers.push(
          new ScatterplotLayer({
            id: `glow-${system}`,
            data: systemData.nodes.features,
            pickable: false,
            opacity: 0.35,
            stroked: false,
            filled: true,
            radiusScale: 10,
            radiusMinPixels: 8,
            radiusMaxPixels: 26,
            getPosition: (d: any) => d.geometry.coordinates,
            getFillColor: palette.glow,
          })
        );
        // Inner bright node
        layers.push(
          new ScatterplotLayer({
            id: `nodes-${system}`,
            data: systemData.nodes.features,
            pickable: true,
            opacity: 1,
            stroked: true,
            filled: true,
            radiusScale: 6,
            radiusMinPixels: 4,
            radiusMaxPixels: 14,
            lineWidthMinPixels: 1,
            getPosition: (d: any) => d.geometry.coordinates,
            getFillColor: palette.node,
            getLineColor: [255, 255, 255, 100],
          })
        );
      }

      // Arc layer with the palette colors
      if (systemData.connections?.features?.length > 0) {
        layers.push(
          new ArcLayer({
            id: `arcs-${system}`,
            data: systemData.connections.features,
            pickable: false,
            getWidth: (d: any) => Math.max(0.5, (d.properties.intensity || 1) * 1.5),
            getSourcePosition: (d: any) => d.properties.source_position,
            getTargetPosition: (d: any) => d.properties.target_position,
            getSourceColor: palette.arc[0],
            getTargetColor: palette.arc[1],
            greatCircle: true,
          })
        );
      }
    });

    // ── Conflict layer with glow + sized by severity ──
    if (activeSystems['conflicts'] && conflictsData.length > 0) {
      // Outer pulse glow
      layers.push(
        new ScatterplotLayer({
          id: 'conflict-glow',
          data: conflictsData,
          pickable: false,
          opacity: 0.25,
          stroked: false,
          filled: true,
          radiusMinPixels: 10,
          radiusMaxPixels: 42,
          getPosition: (d: any) => d.geometry.coordinates,
          getRadius: (d: any) => (SEVERITY_RADIUS[d.properties.severity || 'low'] ?? 8) * 2.5,
          getFillColor: (d: any) => {
            const c = CONFLICT_COLORS[d.properties.event_type] ?? CONFLICT_COLORS.default;
            return [c[0], c[1], c[2], 60];
          },
        })
      );
      // Inner hot dot
      layers.push(
        new ScatterplotLayer({
          id: 'conflict-events',
          data: conflictsData,
          pickable: true,
          opacity: 1,
          stroked: true,
          filled: true,
          radiusMinPixels: 5,
          radiusMaxPixels: 22,
          lineWidthMinPixels: 1.5,
          getPosition: (d: any) => d.geometry.coordinates,
          getRadius: (d: any) => SEVERITY_RADIUS[d.properties.severity || 'low'] ?? 6,
          getFillColor: (d: any) => CONFLICT_COLORS[d.properties.event_type] ?? CONFLICT_COLORS.default,
          getLineColor: [255, 255, 255, 80],
        })
      );
    }

    return layers;
  };

  const handleDeckClick = (info: any) => {
    if (info.object && info.object.properties) {
      const props = info.object.properties;
      onNodeClick({
        ...props,
        // Expose from/to for arc clicks
        from: props.from_name || props.from || props.source,
        to: props.to_name || props.to || props.target,
        coordinates: info.object.geometry?.coordinates || [info.coordinate?.[0], info.coordinate?.[1]]
      });
    }
  };

  return (
    <DeckGL
      initialViewState={INITIAL_VIEW_STATE}
      controller={true}
      layers={createLayers()}
      onClick={handleDeckClick}
      getCursor={({ isHovering }) => isHovering ? 'pointer' : 'default'}
    >
      <Map reuseMaps mapStyle={MAP_STYLE} />
    </DeckGL>
  );
}
