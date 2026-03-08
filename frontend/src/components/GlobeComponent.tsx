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

  // ── Single Unified Effect for Init & Sync ───────────────────────
  useEffect(() => {
    let cancelled = false;
    let globeInstance: any = null;

    const run = async () => {
      try {
        if (!containerRef.current) return;
        
        // 1. Dynamic Import
        const GlobeLib = (await import('globe.gl')).default;
        if (cancelled || !containerRef.current) return;

        // 2. Initialize Instance if needed
        const GlobeFactory = GlobeLib as any;
        const g = GlobeFactory()(containerRef.current);
        globeInstance = g;
        globeRef.current = g;

        const w = containerRef.current.clientWidth || window.innerWidth;
        const h = containerRef.current.clientHeight || window.innerHeight;

        g.width(w).height(h)
         .backgroundColor('#020617')
         .globeImageUrl('//unpkg.com/three-globe/example/img/earth-dark.jpg')
         .bumpImageUrl('//unpkg.com/three-globe/example/img/earth-topology.png')
         .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
         .showAtmosphere(true)
         .atmosphereColor('#4BB3FD')
         .atmosphereAltitude(0.08);

        // 3. Configure Layers (Empty initially)
        g.pointsData([]).pointLat('lat').pointLng('lng').pointColor('color').pointRadius('size').pointAltitude(0.01);
        g.ringsData([]).ringLat('lat').ringLng('lng').ringColor('color');
        g.arcsData([]).arcStartLat('startLat').arcStartLng('startLng').arcEndLat('endLat').arcEndLng('endLng').arcColor('color')
         .arcAltitude((d: any) => Math.max(0.1, d.alt ?? 0.25)).arcStroke((d: any) => d.stroke ?? 0.5);
        g.labelsData(COUNTRY_LABELS).labelLat('lat').labelLng('lng').labelText('text').labelSize('size').labelColor(() => 'rgba(255,255,255,0.4)');

        // 4. Build and Inject Data
        const isValid = (lat: number, lng: number) => !isNaN(lat) && !isNaN(lng) && Math.abs(lat) <= 90 && Math.abs(lng) <= 180;
        
        const pts: any[] = [];
        const rings: any[] = [];
        const arcs: any[] = [];

        // Conflicts
        if (activeSystems['conflicts']) {
          (conflictsData || []).forEach((f: any) => {
            const [lng, lat] = f.geometry.coordinates;
            if (isValid(lat, lng)) {
              const evt = f.properties.event_type || 'default';
              const sev = f.properties.severity || 'low';
              const color = CONFLICT_COLORS[evt] ?? '#FFFFFF';
              pts.push({ lat, lng, size: SEVERITY_SIZE[sev] ?? 0.4, color, props: f.properties });
              rings.push({ lat, lng, color: (t: number) => `${color}${Math.floor((1-t)*255).toString(16).padStart(2,'0')}` });
            }
          });
        }

        // Systems
        Object.keys(activeSystems).forEach(sys => {
          if (!activeSystems[sys] || sys === 'conflicts') return;
          const sd = layersData[sys];
          if (sd?.nodes?.features) {
            sd.nodes.features.forEach((f: any) => {
              const [lng, lat] = f.geometry.coordinates;
              if (isValid(lat, lng)) {
                pts.push({ lat, lng, size: 0.5, color: SYSTEM_COLORS[sys] ?? '#FFFFFF', props: f.properties });
              }
            });
          }
          if (sd?.connections?.features) {
            sd.connections.features.forEach((f: any) => {
              const src = f.properties.source_position;
              const tgt = f.properties.target_position;
              if (src && tgt && isValid(src[1], src[0]) && isValid(tgt[1], tgt[0])) {
                const style = ARC_STYLE[sys] || ARC_STYLE.shipping;
                arcs.push({
                  startLat: src[1], startLng: src[0], endLat: tgt[1], endLng: tgt[0],
                  color: SYSTEM_COLORS[sys] ?? '#FFFFFF', alt: style.alt, stroke: style.stroke
                });
              }
            });
          }
        });

        g.pointsData(pts);
        g.ringsData(rings);
        g.arcsData(arcs);

        console.error(`!!! GLOBE RENDER SUCCESS: ${pts.length} pts, ${arcs.length} arcs !!!`);
      } catch (err: any) {
        console.error("!!! GLOBE RENDER ERROR !!!", err);
      }
    };

    run();
    return () => {
      cancelled = true;
      if (globeInstance) {
        // cleanup if possible
      }
    };
  }, [layersData, activeSystems, conflictsData, onNodeClick]);

  return (
    <div ref={containerRef} style={{ width: '100vw', height: '100vh', background: '#010409' }} />
  );
}
