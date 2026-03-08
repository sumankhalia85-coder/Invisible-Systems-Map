/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import React from 'react';
import type { MapViewState } from '@deck.gl/core';
import DeckGL from '@deck.gl/react';
import { Map } from 'react-map-gl/maplibre';
import { ArcLayer, ScatterplotLayer } from '@deck.gl/layers';
import { HeatmapLayer } from '@deck.gl/aggregation-layers';

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
  shipping:       { node: [34,211,238],  glow: [34,211,238,40],   arc: [[34,211,238,180],[6,182,212,80]] },
  cables:         { node: [59,130,246],  glow: [59,130,246,30],   arc: [[59,130,246,150],[37,99,235,100]] },
  energy:         { node: [251,191,36],  glow: [251,191,36,40],   arc: [[251,191,36,180],[245,158,11,100]] },
  minerals:       { node: [167,139,250], glow: [167,139,250,40],  arc: [[167,139,250,150],[139,92,246,80]] },
  food:           { node: [16,185,129],  glow: [16,185,129,30],   arc: [[16,185,129,150],[5,150,105,80]] },
  oil_gas:        { node: [249,115,22],  glow: [249,115,22,50],   arc: [[249,115,22,200],[234,88,12,120]] },
  semiconductors: { node: [217,70,239],  glow: [217,70,239,40],   arc: [[217,70,239,180],[192,38,211,100]] },
  aviation:       { node: [192,132,252], glow: [192,132,252,30],  arc: [[192,132,252,150],[147,51,234,80]] },
  climate:        { node: [45,212,191],  glow: [45,212,191,40],   arc: [[45,212,191,180],[16,185,129,100]] },
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
  const [t, setT] = React.useState(0);

  React.useEffect(() => {
    let frame: number;
    const loop = () => {
      setT(prev => (prev + 1) % 360);
      frame = requestAnimationFrame(loop);
    };
    frame = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(frame);
  }, []);

  const createLayers = () => {
    const layers: any[] = [];
    const pulse = Math.sin(t * (Math.PI / 180));
    const glowScale = 1 + pulse * 0.3;

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
            radiusScale: 10 * glowScale,
            radiusMinPixels: 8,
            radiusMaxPixels: 26,
            getPosition: (d: any) => d.geometry.coordinates,
            getFillColor: [...palette.glow.slice(0,3) as [number,number,number], Math.floor(palette.glow[3] * (0.5 + pulse * 0.5))],
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

      // Arc layer with simulation of moving particles (ships/planes) using ArcLayer's dash properties
      if (systemData.connections?.features?.length > 0) {
        const isFlowSystem = system === 'shipping' || system === 'aviation' || system === 'food';
        const isGridSystem = system === 'energy' || system === 'semiconductors' || system === 'cables';
        
        layers.push(
          new ArcLayer({
            id: `arcs-${system}`,
            data: systemData.connections.features,
            pickable: false,
            getWidth: (d: any) => Math.max(0.6, (d.properties.intensity || 1) * 1.5),
            getSourcePosition: (d: any) => d.properties.source_position,
            getTargetPosition: (d: any) => d.properties.target_position,
            getSourceColor: [...palette.arc[0].slice(0,3) as [number,number,number], isGridSystem ? Math.floor(palette.arc[0][3] * (0.6 + pulse * 0.3)) : palette.arc[0][3]],
            getTargetColor: [...palette.arc[1].slice(0,3) as [number,number,number], isGridSystem ? Math.floor(palette.arc[1][3] * (0.6 - pulse * 0.3)) : palette.arc[1][3]],
            greatCircle: true,
          })
        );

        // Animated overlay for "flow" systems
        if (isFlowSystem) {
           const flowPulse = (t % 120) / 120;
           layers.push(
             new ArcLayer({
               id: `arcs-flow-${system}`,
               data: systemData.connections.features,
               pickable: false,
               getWidth: (d: any) => Math.max(1.0, (d.properties.intensity || 1) * 2.0),
               getSourcePosition: (d: any) => d.properties.source_position,
               getTargetPosition: (d: any) => d.properties.target_position,
               getSourceColor: [...palette.node, 0],
               getTargetColor: [...palette.node, 0],
               // Simulation of movement via dash offsets:
               // Deck.gl ArcLayer doesn't support dashOffset easily, so we use a specialized DashLayer if available,
               // but we can simulate it with opacity transitions.
            })
           );
        }
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

    // ── Climate heatmap (use temperature or derived carbon intensity as weight) ──
    if (activeSystems['climate'] && layersData['climate'] && layersData['climate'].nodes?.features?.length > 0) {
      const feats = layersData['climate'].nodes.features;
      // Compute weight from temperature (fallback to 1)
      const heatData = feats.map((f: any) => ({
        position: f.geometry.coordinates,
        weight: Math.max(0, (f.properties?.temperature_c ?? 20) + 30) // shift to positive domain
      }));

      layers.push(new HeatmapLayer({
        id: 'climate-heatmap',
        data: heatData,
        getPosition: (d: any) => d.position,
        getWeight: (d: any) => d.weight,
        radiusPixels: 60,
        intensity: 1.5,
        threshold: 0.02,
        aggregation: 'SUM'
      }));
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
      <Map mapStyle={MAP_STYLE} />
    </DeckGL>
  );
}
