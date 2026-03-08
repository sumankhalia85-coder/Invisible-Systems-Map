/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import React, { useEffect, useRef, useState } from 'react';

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
  climate:        '#2DD4BF',
};

// ── Cable rainbow — each cable gets a distinct luminous color ──────
const CABLE_RAINBOW = [
  '#FF4D4D', '#FF8C42', '#FFD166', '#06D6A0', '#118AB2',
  '#7C4DFF', '#E040FB', '#00BCD4', '#FFAB40', '#69F0AE',
  '#F06292', '#4FC3F7', '#AED581', '#FF7043', '#B39DDB',
  '#80CBC4', '#FFF176', '#CE93D8', '#80DEEA', '#FFCC02',
];

// ── Per-system arc visual signature ───────────────────────────────
const ARC_STYLE: Record<string, { stroke: number; alt: number; dashLen: number; dashGap: number; animMs: number }> = {
  cables:         { stroke: 0.4, alt: 0.35, dashLen: 0.4,  dashGap: 0.15, animMs: 3000 },
  shipping:       { stroke: 1.0, alt: 0.08, dashLen: 0.35, dashGap: 0.2,  animMs: 2500 },
  oil_gas:        { stroke: 1.0, alt: 0.06, dashLen: 0.4,  dashGap: 0.2,  animMs: 2800 },
  food:           { stroke: 0.6, alt: 0.12, dashLen: 0.3,  dashGap: 0.25, animMs: 3200 },
  minerals:       { stroke: 0.5, alt: 0.14, dashLen: 0.3,  dashGap: 0.2,  animMs: 3500 },
  semiconductors: { stroke: 0.4, alt: 0.20, dashLen: 0.35, dashGap: 0.15, animMs: 1800 },
  aviation:       { stroke: 0.5, alt: 0.45, dashLen: 0.5,  dashGap: 0.15, animMs: 1500 },
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
  { lat: 23.7861, lng: 120.9765, text: 'Taiwan', size: 0.6 }, // Fixed: swapped lat/lng
];

// ── Temperature → color ──────────────────────────────────────────
function tempColor(temp: number) {
  if (temp > 42) return '#DC2626';
  if (temp > 35) return '#F97316';
  if (temp > 25) return '#FBBF24';
  if (temp > 15) return '#34D399';
  if (temp > 5)  return '#2DD4BF';
  if (temp > -5) return '#38BDF8';
  return '#818CF8';
}

export default function GlobeComponent({
  layersData, activeSystems, onNodeClick, conflictsData = []
}: GlobeComponentProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const globeRef = useRef<any>(null);
  const [globeReady, setGlobeReady] = useState(false);

  // ── Store props in refs so the async init closure always gets FRESH data ──
  const propsRef = useRef({ layersData, activeSystems, onNodeClick, conflictsData });
  propsRef.current = { layersData, activeSystems, onNodeClick, conflictsData };

  // ════════════════════════════════════════════════════════════
  // SYNC FUNCTION — builds all data from latest props & feeds to globe
  // ════════════════════════════════════════════════════════════
  const syncDataToGlobe = (g: any) => {
    const { layersData: ld, activeSystems: as2, conflictsData: cd } = propsRef.current;

    console.log("GLOBE SYNC TICK", { activeSystems: as2, layersDataKeys: Object.keys(ld), climateData: ld['climate'] });

    // ── Pre-Filter and Build Data Layers ──
    const isValidCoord = (lat: number, lng: number) => {
      return !isNaN(lat) && !isNaN(lng) && Math.abs(lat) <= 90 && Math.abs(lng) <= 180;
    };

    const pts: any[] = [];
    Object.keys(as2).forEach(sys => {
      if (!as2[sys] || sys === 'conflicts' || sys === 'energy') return;
      const sd = ld[sys];
      if (!sd?.nodes?.features) return;
      sd.nodes.features.forEach((f: any) => {
        const [lng, lat] = f.geometry.coordinates;
        if (!isValidCoord(lat, lng)) return;
        if (sys === 'climate') {
          const temp = f.properties.temperature_c ?? 20;
          pts.push({ lat, lng, size: 1.0, color: tempColor(temp), props: f.properties, system: sys });
        } else {
          pts.push({ lat, lng, size: 0.5, color: SYSTEM_COLORS[sys] ?? '#FFFFFF', props: f.properties, system: sys });
        }
      });
    });
    if (as2['conflicts']) {
      cd.forEach((f: any) => {
        const [lng, lat] = f.geometry.coordinates;
        if (!isValidCoord(lat, lng)) return;
        const evtType = f.properties.event_type || 'default';
        const sev = f.properties.severity || 'low';
        pts.push({ lat, lng, size: SEVERITY_SIZE[sev] ?? 0.4, color: CONFLICT_COLORS[evtType] ?? '#FFFFFF', props: f.properties, system: 'conflicts' });
      });
    }
    g.pointsData(pts);

    // ── Rings ──
    const rings: any[] = [];
    if (as2['conflicts']) {
      cd.forEach((f: any) => {
        const [lng, lat] = f.geometry.coordinates;
        if (!isValidCoord(lat, lng)) return;
        const evtType = f.properties.event_type || 'default';
        const hex = CONFLICT_COLORS[evtType] ?? '#FFFFFF';
        rings.push({ 
          lat, lng, maxRadius: 5, speed: 3, period: Math.random() * 500 + 1000, 
          color: (t: number) => {
            const alpha = Math.max(0, Math.min(255, Math.floor((1 - t) * 255)));
            return `${hex}${alpha.toString(16).padStart(2, '0')}`;
          }
        });
      });
    }
    Object.keys(as2).forEach(sys => {
      if (!as2[sys] || sys === 'conflicts' || sys === 'energy') return;
      const sd = ld[sys];
      if (!sd?.nodes?.features) return;
      sd.nodes.features.forEach((f: any) => {
        const [lng, lat] = f.geometry.coordinates;
        if (!isValidCoord(lat, lng)) return;
        if (sys === 'climate') {
          const temp = f.properties?.temperature_c ?? 20;
          const hex = tempColor(temp);
          // Large soft atmospheric heatmap
          rings.push({ 
            lat, lng, maxRadius: 15, speed: 0.15, period: 6000, 
            color: (t: number) => `${hex}28` // Fixed constant soft alpha (approx 40/255)
          });
          // Sharp infra glow
          rings.push({ 
            lat, lng, maxRadius: 3, speed: 1.5, period: 2000, 
            color: (t: number) => {
              const alpha = Math.max(0, Math.min(255, Math.floor((1 - t) * 150)));
              return `${hex}${alpha.toString(16).padStart(2, '0')}`;
            }
          });
        } else {
          const hex = SYSTEM_COLORS[sys] ?? '#FFFFFF';
          rings.push({ 
            lat, lng, maxRadius: 2.5, speed: 1.5, period: Math.random() * 1000 + 2000, 
            color: (t: number) => {
              const alpha = Math.max(0, Math.min(255, Math.floor((1 - t) * 150)));
              return `${hex}${alpha.toString(16).padStart(2, '0')}`;
            }
          });
        }
      });
    });
    g.ringsData(rings);

    // ── Arcs ──
    const arcs: any[] = [];
    let cableIdx = 0;
    Object.keys(as2).forEach(sys => {
      if (!as2[sys] || sys === 'conflicts' || sys === 'energy') return;
      const sd = ld[sys];
      if (!sd?.connections?.features) return;
      const style = ARC_STYLE[sys] || ARC_STYLE.shipping;
      sd.connections.features.forEach((f: any) => {
        const src = f.properties.source_position;
        const tgt = f.properties.target_position;
        if (!src || !tgt || !isValidCoord(src[1], src[0]) || !isValidCoord(tgt[1], tgt[0])) return;
        const arcColor = sys === 'cables'
          ? [CABLE_RAINBOW[cableIdx % CABLE_RAINBOW.length], CABLE_RAINBOW[(cableIdx+1) % CABLE_RAINBOW.length]]
          : SYSTEM_COLORS[sys] ?? '#FFFFFF';
        cableIdx++;
        arcs.push({
          startLat: src[1], startLng: src[0],
          endLat: tgt[1], endLng: tgt[0],
          color: arcColor, system: sys,
          stroke: style.stroke, alt: style.alt,
          dashLen: style.dashLen, dashGap: style.dashGap,
          animMs: style.animMs,
          fromName: f.properties.from_name || f.properties.cable_name || 'Origin',
          toName: f.properties.to_name || 'Destination',
          props: f.properties,
        });
      });
    });

    // ── Wind Particle Streams (Climate) ──
    if (as2['climate']) {
      for(let i=0; i<60; i++) {
         const lat1 = (Math.random() * 140) - 70;
         const lng1 = (Math.random() * 360) - 180;
         const lat2 = lat1 + (Math.random() * 10 - 5);
         let lng2 = lng1 + (Math.random() * 40 + 10);
         if (lng2 > 180) lng2 -= 360;
         arcs.push({
           startLat: lat1, startLng: lng1, endLat: lat2, endLng: lng2,
           color: ['#34D399', '#34D399'], // pure solid cyan/green wind
           system: 'climate_wind',
           stroke: Math.random() * 0.4 + 0.1,
           alt: Math.random() * 0.15 + 0.05,
           dashLen: 0.15, dashGap: 0.85,
           animMs: Math.random() * 3000 + 2000,
         });
      }
    }

    g.arcsData(arcs);
    console.log(`[Globe Debug] Sync complete: ${pts.length} pts, ${rings.length} rings, ${arcs.length} arcs`);

    // ── Energy & Carbon hexbins ──
    let hexPts: any[] = [];
    if (as2['energy']) {
      const sd = ld['energy'];
      if (sd?.nodes?.features) {
        sd.nodes.features.forEach((f: any) => {
          const [lng, lat] = f.geometry.coordinates;
          if (!isValidCoord(lat, lng)) return;
          const cap = Number(f.properties.capacity_mw || 100);
          hexPts.push({ lat, lng, weight: cap, type: 'energy', props: f.properties });
        });
      }
    }
    if (as2['climate']) {
      const sd = ld['climate'];
      if (sd?.nodes?.features) {
        sd.nodes.features.forEach((f: any) => {
          const [lng, lat] = f.geometry.coordinates;
          if (!isValidCoord(lat, lng)) return;
          const temp = f.properties.temperature_c ?? 20;
          // Carbon plumes: hotter/equator regions get taller plumes
          const carbon = Math.floor(Math.abs(lat) * 2 + Math.max(0, temp) * 10);
          hexPts.push({ lat, lng, weight: carbon * 20, type: 'carbon', props: f.properties });
        });
      }
    }
    g.hexBinPointsData(hexPts);

    // ── Atmosphere ──
    let atmoColor = '#4BB3FD';
    if (as2['conflicts']) atmoColor = '#DC2626';
    else if (as2['climate']) atmoColor = '#34D399'; // biosphere green
    else if (as2['food']) atmoColor = '#34D399';
    else if (as2['minerals']) atmoColor = '#A78BFA';
    else if (as2['energy']) atmoColor = '#FBBF24';
    else if (as2['cables']) atmoColor = '#818CF8';
    g.atmosphereColor(atmoColor);
    g.atmosphereAltitude(0.08); // Fixed low altitude so data stays visible
  };

  // ── Initialise globe once ──────────────────────────────────────
  useEffect(() => {
    let cancelled = false;

    const init = async () => {
      if (!containerRef.current) return;
      const GlobeLib = (await import('globe.gl')).default;
      if (cancelled || !containerRef.current) return;

      const w = containerRef.current.clientWidth || window.innerWidth;
      const h = containerRef.current.clientHeight || window.innerHeight;
      const nodeClick = propsRef.current.onNodeClick;

      const GlobeFactory = GlobeLib as any;
      const g = GlobeFactory()(containerRef.current)
        .width(w).height(h)
        .backgroundColor('#020617')
        .globeImageUrl('//unpkg.com/three-globe/example/img/earth-dark.jpg') // Restored dark map for country borders!
        .bumpImageUrl('//unpkg.com/three-globe/example/img/earth-topology.png')
        .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
        .showAtmosphere(true)
        .atmosphereColor('#4BB3FD')
        .atmosphereAltitude(0.02) // Ultra-low for debugging

        .pointsData([])
        .pointLat('lat').pointLng('lng')
        .pointColor('color').pointRadius('size')
        .pointAltitude(0.01).pointResolution(8)
        .onPointClick((p: any) => { if (p?.props) propsRef.current.onNodeClick({ ...p.props }); })
        .onPointHover((p: any) => {
          if (containerRef.current) (containerRef.current as any).style.cursor = p ? 'pointer' : 'default';
        })

        .ringsData([])
        .ringLat('lat').ringLng('lng')
        .ringColor('color')
        .ringMaxRadius('maxRadius')
        .ringPropagationSpeed('speed')
        .ringRepeatPeriod('period')

        .arcsData([])
        .arcStartLat('startLat').arcStartLng('startLng')
        .arcEndLat('endLat').arcEndLng('endLng')
        .arcColor('color')
        .arcAltitude((d: any) => Math.max(0.1, d.alt ?? 0.25)) // Guaranteed minimum altitude
        .arcStroke((d: any) => d.stroke ?? 0.5)
        .arcDashLength((d: any) => d.dashLen ?? 0.4)
        .arcDashGap((d: any) => d.dashGap ?? 0.2)
        .arcDashAnimateTime((d: any) => d.animMs ?? 2000)
        .onArcClick((arc: any) => {
          if (arc) {
            propsRef.current.onNodeClick({
              name: `${arc.fromName} → ${arc.toName}`,
              type: arc.system + ' route', system: arc.system,
              from: arc.fromName, to: arc.toName,
              coordinates: [arc.startLng, arc.startLat],
              ...arc.props,
            });
          }
        })
        .onArcHover((arc: any) => {
          if (containerRef.current) (containerRef.current as any).style.cursor = arc ? 'pointer' : 'default';
        })

        .hexBinPointsData([])
        .hexBinPointWeight('weight')
        .hexBinResolution(3)
        .hexTopColor((d: any) => {
          const type = d.points?.[0]?.type;
          const v = d.sumWeight;
          if (type === 'carbon') return '#A8A29E'; // stone/grey plume 
          if (v > 10000) return '#EF4444';
          if (v > 3000)  return '#F97316';
          if (v > 500)   return '#FBBF24';
          return '#FDE047';
        })
        .hexSideColor((d: any) => {
          const type = d.points?.[0]?.type;
          const v = d.sumWeight;
          if (type === 'carbon') return '#78716C'; // faint grey plume
          if (v > 10000) return '#EF4444';
          if (v > 3000)  return '#F97316';
          return '#FBBF24';
        })
        .hexBinMerge(true)
        .hexAltitude((d: any) => Math.min(0.80, d.sumWeight / 15000))
        .onHexBinClick((bin: any) => {
           if (bin?.points?.length > 0) {
              const pts = [...bin.points].sort((a: any, b: any) => b.weight - a.weight);
              if (pts[0].props) {
                const p = pts[0];
                propsRef.current.onNodeClick({ ...p.props, system: p.type === 'carbon' ? 'climate' : 'energy', coordinates: [p.lng, p.lat] });
              }
           }
        })
        .onHexBinHover((bin: any) => {
          if (containerRef.current) (containerRef.current as any).style.cursor = bin ? 'pointer' : 'default';
        })

        .labelsData(COUNTRY_LABELS)
        .labelLat('lat').labelLng('lng').labelText('text').labelSize('size')
        .labelColor(() => 'rgba(255,255,255,0.40)')
        .labelResolution(3).labelAltitude(0.01).labelDotRadius(0);

      globeRef.current = g;

      g.controls().autoRotate = true;
      g.controls().autoRotateSpeed = 0.5;
      g.controls().enableDamping = true;
      g.controls().dampingFactor = 0.05;
      g.controls().minDistance = 150;

      // Feed data RIGHT NOW using the ref (has latest props!)
      syncDataToGlobe(g);
      setGlobeReady(true);
    };

    init();
    return () => { cancelled = true; };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── Re-sync whenever props change AND globe is ready ─────────
  useEffect(() => {
    if (!globeReady || !globeRef.current) return;
    syncDataToGlobe(globeRef.current);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [globeReady, layersData, activeSystems, conflictsData]);

  return (
    <div ref={containerRef}
         style={{ width: '100vw', height: '100vh', background: '#020B18', overflow: 'hidden' }} />
  );
}
