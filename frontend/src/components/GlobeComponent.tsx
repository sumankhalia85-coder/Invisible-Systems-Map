/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import React, { useEffect, useRef, useCallback } from 'react';

interface GlobeComponentProps {
  layersData: any;
  activeSystems: Record<string, boolean>;
  onNodeClick: (nodeInfo: any) => void;
  conflictsData?: any[];
}

// ── Per-system color definitions ──────────────────────────────────
const SYSTEM_COLORS: Record<string, string> = {
  shipping:       '#22D3EE',
  cables:         '#818CF8',
  energy:         '#FBBF24',
  minerals:       '#A78BFA',
  food:           '#34D399',
  oil_gas:        '#F97316',
  semiconductors: '#06B6D4',
  aviation:       '#8B5CF6',
};

// ── Cable rainbow — each cable gets a distinct luminous color ──────
const CABLE_RAINBOW = [
  '#FF4D4D', '#FF8C42', '#FFD166', '#06D6A0', '#118AB2',
  '#7C4DFF', '#E040FB', '#00BCD4', '#FFAB40', '#69F0AE',
  '#F06292', '#4FC3F7', '#AED581', '#FF7043', '#B39DDB',
  '#80CBC4', '#FFF176', '#CE93D8', '#80DEEA', '#FFCC02',
];

// ── Per-system arc visual signature ───────────────────────────────
// cables:   very thin, glowing, elegant sweeping curves
// shipping: thick, low, fast
const ARC_STYLE: Record<string, { stroke: number; alt: number; dashLen: number; dashGap: number; animMs: number }> = {
  cables:         { stroke: 0.2, alt: 0.35, dashLen: 0.1, dashGap: 0.05, animMs: 2000 },
  shipping:       { stroke: 0.8, alt: 0.08, dashLen: 0.05, dashGap: 0.8, animMs: 3000 },
  oil_gas:        { stroke: 0.9, alt: 0.06, dashLen: 0.06, dashGap: 0.8, animMs: 3500 },
  food:           { stroke: 0.4, alt: 0.12, dashLen: 0.08, dashGap: 0.6, animMs: 4000 },
  minerals:       { stroke: 0.3, alt: 0.14, dashLen: 0.07, dashGap: 0.7, animMs: 3800 },
  semiconductors: { stroke: 0.2, alt: 0.20, dashLen: 0.15, dashGap: 0.4, animMs: 1500 },
  aviation:       { stroke: 0.3, alt: 0.45, dashLen: 0.20, dashGap: 0.5, animMs: 2000 },
};

// ── Conflict colors by event type ────────────────────────────────
const CONFLICT_COLORS: Record<string, string> = {
  battle: '#EF4444', airstrike: '#F97316', missile: '#EAB308',
  bombing: '#A855F7', civilian_violence: '#EC4899', protest: '#3B82F6',
  riot: '#14B8A6', geopolitical: '#94A3B8', massacre: '#7F1D1D', default: '#FFFFFF',
};
const SEVERITY_SIZE: Record<string, number> = { low: 0.3, medium: 0.5, high: 0.8, critical: 1.3 };

// ── Country labels visible on zoom ───────────────────────────────
const COUNTRY_LABELS = [
  { lat: 37.1, lng: -95.7, text: 'United States', size: 1.0 },
  { lat: 56.1, lng: -106.3, text: 'Canada', size: 0.9 },
  { lat: -14.2, lng: -51.9, text: 'Brazil', size: 0.95 },
  { lat: 51.2, lng: 10.4, text: 'Germany', size: 0.8 },
  { lat: 46.2, lng: 2.2, text: 'France', size: 0.8 },
  { lat: 55.4, lng: -3.4, text: 'UK', size: 0.8 },
  { lat: 55.3, lng: 37.6, text: 'Russia', size: 1.0 },
  { lat: 35.9, lng: 104.2, text: 'China', size: 1.0 },
  { lat: 36.2, lng: 138.3, text: 'Japan', size: 0.85 },
  { lat: 20.6, lng: 78.9, text: 'India', size: 0.95 },
  { lat: -25.3, lng: 133.8, text: 'Australia', size: 0.9 },
  { lat: 9.1, lng: 40.5, text: 'Ethiopia', size: 0.7 },
  { lat: 26.8, lng: 30.8, text: 'Egypt', size: 0.75 },
  { lat: 33.9, lng: 9.5, text: 'Libya', size: 0.65 },
  { lat: 48.1, lng: 31.2, text: 'Ukraine', size: 0.75 },
  { lat: 25.0, lng: 45.0, text: 'Saudi Arabia', size: 0.85 },
  { lat: 35.9, lng: 14.4, text: 'Iran', size: 0.75 },
  { lat: 30.4, lng: 69.3, text: 'Pakistan', size: 0.7 },
  { lat: 1.4, lng: 104.0, text: 'Singapore', size: 0.6 },
  { lat: 36.6, lng: 127.9, text: 'S. Korea', size: 0.7 },
  { lat: -1.9, lng: 29.9, text: 'DRC', size: 0.65 },
  { lat: 15.6, lng: 32.5, text: 'Sudan', size: 0.65 },
  { lat: 31.0, lng: 34.9, text: 'Israel', size: 0.6 },
  { lat: 15.8, lng: -90.2, text: 'Mexico', size: 0.7 },
  { lat: 120.9765, lng: 24.7861, text: 'Taiwan', size: 0.6 },
];

export default function GlobeComponent({
  layersData, activeSystems, onNodeClick, conflictsData = []
}: GlobeComponentProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const globeRef = useRef<any>(null);

  // ── Build flat points array for non-energy systems ─────────────
  const buildPoints = useCallback(() => {
    const pts: any[] = [];
    Object.keys(activeSystems).forEach(sys => {
      if (!activeSystems[sys] || sys === 'conflicts' || sys === 'energy') return;
      const sd = layersData[sys];
      if (!sd?.nodes?.features) return;
      sd.nodes.features.forEach((f: any) => {
        const [lng, lat] = f.geometry.coordinates;
        pts.push({ lat, lng, size: 0.5, color: SYSTEM_COLORS[sys] ?? '#FFFFFF', props: f.properties, system: sys });
      });
    });
    // Conflict events
    if (activeSystems['conflicts']) {
      conflictsData.forEach((f: any) => {
        const [lng, lat] = f.geometry.coordinates;
        if (!lat || !lng) return;
        const evtType = f.properties.event_type || 'default';
        const sev = f.properties.severity || 'low';
        pts.push({ lat, lng, size: SEVERITY_SIZE[sev] ?? 0.4, color: CONFLICT_COLORS[evtType] ?? '#FFFFFF', props: f.properties, system: 'conflicts' });
      });
    }
    return pts;
  }, [layersData, activeSystems, conflictsData]);

  // ── Build Pulsing Rings for nodes ──────────
  const buildRings = useCallback(() => {
    const rings: any[] = [];
    if (activeSystems['conflicts']) {
      conflictsData.forEach((f: any) => {
        const [lng, lat] = f.geometry.coordinates;
        if (!lat || !lng) return;
        const evtType = f.properties.event_type || 'default';
        const hex = CONFLICT_COLORS[evtType] ?? '#FFFFFF';
        rings.push({ lat, lng, maxRadius: 5, speed: 3, period: Math.random() * 500 + 1000, color: (t: number) => `${hex}${Math.floor((1-t)*255).toString(16).padStart(2, '0')}` });
      });
    }
    Object.keys(activeSystems).forEach(sys => {
      if (!activeSystems[sys] || sys === 'conflicts' || sys === 'energy') return;
      const sd = layersData[sys];
      if (!sd?.nodes?.features) return;
      sd.nodes.features.forEach((f: any) => {
        const [lng, lat] = f.geometry.coordinates;
        const hex = SYSTEM_COLORS[sys] ?? '#FFFFFF';
        rings.push({ lat, lng, maxRadius: 2.5, speed: 1.5, period: Math.random() * 1000 + 2000, color: (t: number) => `${hex}${Math.floor((1-t)*150).toString(16).padStart(2, '0')}` });
      });
    });
    return rings;
  }, [layersData, activeSystems, conflictsData]);

  // ── Dynamic Atmosphere Color ──────────
  const getAtmosphereColor = useCallback(() => {
    if (activeSystems['conflicts']) return '#DC2626'; // crimson
    if (activeSystems['food']) return '#34D399';      // soft green
    if (activeSystems['minerals']) return '#A78BFA';  // soft purple
    if (activeSystems['energy']) return '#FBBF24';    // amber
    if (activeSystems['cables']) return '#818CF8';    // electric blue
    return '#4BB3FD'; // default
  }, [activeSystems]);

  // ── Build energy hexbin points (for 3D bar extrusion) ──────────
  const buildEnergyHexPoints = useCallback(() => {
    if (!activeSystems['energy']) return [];
    const sd = layersData['energy'];
    if (!sd?.nodes?.features) return [];
    return sd.nodes.features.map((f: any) => {
      const [lng, lat] = f.geometry.coordinates;
      const cap = Number(f.properties.capacity_mw || 100);
      return { lat, lng, weight: cap, props: f.properties };
    });
  }, [layersData, activeSystems]);

  // ── Build unified arcs array (all systems, differentiated by style) ─
  const buildArcs = useCallback(() => {
    const arcs: any[] = [];
    let cableIdx = 0;
    Object.keys(activeSystems).forEach(sys => {
      if (!activeSystems[sys] || sys === 'conflicts' || sys === 'energy') return;
      const sd = layersData[sys];
      if (!sd?.connections?.features) return;
      const style = ARC_STYLE[sys] || ARC_STYLE.shipping;
      sd.connections.features.forEach((f: any) => {
        const src = f.properties.source_position;
        const tgt = f.properties.target_position;
        if (!src || !tgt) return;
        // Cables get a glowing gradient or a distinct vibrant color
        const arcColor = sys === 'cables'
          ? [CABLE_RAINBOW[cableIdx % CABLE_RAINBOW.length], CABLE_RAINBOW[(cableIdx+1) % CABLE_RAINBOW.length]]
          : SYSTEM_COLORS[sys] ?? '#FFFFFF';
        cableIdx++;
        arcs.push({
          startLat: src[1], startLng: src[0],
          endLat: tgt[1], endLng: tgt[0],
          color: arcColor,
          system: sys,
          stroke: style.stroke,
          alt: style.alt,
          dashLen: style.dashLen,
          dashGap: style.dashGap,
          animMs: style.animMs,
          fromName: f.properties.from_name || f.properties.cable_name || 'Origin',
          toName: f.properties.to_name || 'Destination',
          props: f.properties,
        });
      });
    });
    return arcs;
  }, [layersData, activeSystems]);

  // ── Initialise globe once ──────────────────────────────────────
  useEffect(() => {
    let cancelled = false;

    const init = async () => {
      if (!containerRef.current) return;
      const GlobeLib = (await import('globe.gl')).default;
      if (cancelled || !containerRef.current) return;

      const w = containerRef.current.clientWidth || window.innerWidth;
      const h = containerRef.current.clientHeight || window.innerHeight;

      const GlobeFactory = GlobeLib as any;
      const g = GlobeFactory()(containerRef.current)
        .width(w).height(h)
        .backgroundColor('#020617')

        // ── Sleek dark data-viz globe with stars & atmosphere ──
        .globeImageUrl('//unpkg.com/three-globe/example/img/earth-dark.jpg')
        .bumpImageUrl('//unpkg.com/three-globe/example/img/earth-topology.png')
        .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
        .showAtmosphere(true)
        .atmosphereColor('#4BB3FD')
        .atmosphereAltitude(0.25)

        // ── Points (shrink energy to nothing; it gets hex-bars instead) ──
        .pointsData([])
        .pointLat('lat').pointLng('lng')
        .pointColor('color').pointRadius('size')
        .pointAltitude(0.01).pointResolution(8)
        .onPointClick((p: any) => { if (p?.props) onNodeClick({ ...p.props }); })
        .onPointHover((p: any) => {
          if (containerRef.current) (containerRef.current as any).style.cursor = p ? 'pointer' : 'default';
        })
        
        // ── Pulsing Rings around Nodes ──
        .ringsData([])
        .ringLat('lat').ringLng('lng')
        .ringColor('color')
        .ringMaxRadius('maxRadius')
        .ringPropagationSpeed('speed')
        .ringRepeatPeriod('period')

        // ── Unified arcs with per-arc accessor functions ──
        .arcsData([])
        .arcStartLat('startLat').arcStartLng('startLng')
        .arcEndLat('endLat').arcEndLng('endLng')
        .arcColor('color')
        .arcAltitude((d: any) => d.alt ?? 0.15)
        .arcStroke((d: any) => d.stroke ?? 0.5)
        .arcDashLength((d: any) => d.dashLen ?? 0.4)
        .arcDashGap((d: any) => d.dashGap ?? 0.2)
        .arcDashAnimateTime((d: any) => d.animMs ?? 2000)
        .onArcClick((arc: any) => {
          if (arc) {
            onNodeClick({
              name: `${arc.fromName} → ${arc.toName}`,
              type: arc.system + ' route',
              system: arc.system,
              from: arc.fromName,
              to: arc.toName,
              coordinates: [arc.startLng, arc.startLat],
              ...arc.props,
            });
          }
        })
        .onArcHover((arc: any) => {
          if (containerRef.current) (containerRef.current as any).style.cursor = arc ? 'pointer' : 'default';
        })

        // ── Energy: 3D extruded hexagonal bars (Spikes) ──
        // High resolution for needle-like spikes, colored by intensity
        .hexBinPointsData([])
        .hexBinPointWeight('weight')
        .hexBinResolution(3)
        .hexTopColor((d: any) => {
          const v = d.sumWeight;
          if (v > 10000) return '#EF4444';    // pure red
          if (v > 3000)  return '#F97316';    // intense orange
          if (v > 500)   return '#FBBF24';    // bright amber
          return '#FDE047';                   // yellow 
        })
        .hexSideColor((d: any) => {
          const v = d.sumWeight;
          if (v > 10000) return 'rgba(239,68,68,0.6)';
          if (v > 3000)  return 'rgba(249,115,22,0.6)';
          return 'rgba(251,191,36,0.3)';
        })
        .hexBinMerge(true)
        .hexAltitude((d: any) => Math.min(0.80, d.sumWeight / 15000))   // much taller spikes
        .onHexBinClick((bin: any) => {
           // Provide info for the heaviest energy node in that bin
           if (bin?.points?.length > 0) {
              const pts = [...bin.points].sort((a,b) => b.weight - a.weight);
              if (pts[0].props) onNodeClick(pts[0].props);
           }
        })
        .onHexBinHover((bin: any) => {
          if (containerRef.current) (containerRef.current as any).style.cursor = bin ? 'pointer' : 'default';
        })

        // ── Country labels (visible on zoom) ──
        .labelsData(COUNTRY_LABELS)
        .labelLat('lat').labelLng('lng').labelText('text').labelSize('size')
        .labelColor(() => 'rgba(255,255,255,0.40)')
        .labelResolution(3).labelAltitude(0.01).labelDotRadius(0);

      globeRef.current = g;

      // Deep space inertia and auto-rotate
      g.controls().autoRotate = true;
      g.controls().autoRotateSpeed = 0.5;
      g.controls().enableDamping = true;
      g.controls().dampingFactor = 0.05;
      g.controls().minDistance = 150;
    };

    init();
    return () => { cancelled = true; };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── Reactively update every data layer when dependencies change ─
  useEffect(() => {
    if (!globeRef.current) return;
    globeRef.current.pointsData(buildPoints());
    globeRef.current.ringsData(buildRings());
    globeRef.current.arcsData(buildArcs());
    globeRef.current.hexBinPointsData(buildEnergyHexPoints());
    globeRef.current.atmosphereColor(getAtmosphereColor());
  }, [buildPoints, buildRings, buildArcs, buildEnergyHexPoints, getAtmosphereColor]);

  return (
    <div ref={containerRef}
         style={{ width: '100vw', height: '100vh', background: '#020B18', overflow: 'hidden' }} />
  );
}
