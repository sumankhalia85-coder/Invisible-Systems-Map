/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import React, { useState, useEffect } from "react";
import dynamic from 'next/dynamic';
import LayerPanel from "@/components/LayerPanel";
import InfoPanel from "@/components/InfoPanel";
import TopNav from "@/components/TopNav";
import { Globe2, Map } from 'lucide-react';

// Dynamically import heavy 3D/map components (no SSR)
const MapComponent = dynamic(() => import('@/components/MapComponent'), {
  ssr: false,
  loading: () => <LoadingScreen />,
});

import GlobeComponent from '@/components/GlobeComponent';

function LoadingScreen() {
  return (
    <div className="h-screen w-full bg-slate-950 flex flex-col items-center justify-center">
      <div className="relative w-16 h-16 mb-6">
        <div className="absolute inset-0 border-2 border-cyan-500/10 rounded-full animate-ping" />
        <div className="absolute inset-2 border-2 border-cyan-500/30 rounded-full animate-spin" style={{ animationDuration: '2s' }} />
        <div className="absolute inset-4 border-2 border-cyan-400 rounded-full animate-spin" style={{ animationDuration: '0.9s' }} />
      </div>
      <p className="text-[10px] uppercase tracking-widest text-slate-500">Initialising Intelligence Engine...</p>
    </div>
  );
}

type SystemsState = { [key: string]: boolean };

export default function Home() {
  const [activeSystems, setActiveSystems] = useState<SystemsState>({
    shipping: true, cables: true, energy: false,
    minerals: false, food: false, conflicts: false,
    oil_gas: false, semiconductors: false, aviation: false,
    climate: false,
  });
  const [layersData, setLayersData] = useState<Record<string, any>>({});
  const [conflictsData, setConflictsData] = useState<any[]>([]);
  const [conflictMeta, setConflictMeta] = useState<any>(null);
  const [selectedNode, setSelectedNode] = useState<Record<string, any> | null>(null);
  const [activeMode, setActiveMode] = useState('systems');
  const [viewMode, setViewMode] = useState<'2d' | '3d'>('2d');  // 2D flat map or 3D globe
  // dataLoaded could be used for a loading overlay in future

  const toggleSystem = (id: string) =>
    setActiveSystems(prev => ({ ...prev, [id]: !prev[id] }));

  const handleModeChange = (mode: string) => {
    setActiveMode(mode);
    const off = { shipping: false, cables: false, energy: false, minerals: false, food: false, conflicts: false, oil_gas: false, semiconductors: false, aviation: false, climate: false };
    if (mode === 'conflicts')
      setActiveSystems({ ...off, conflicts: true });
    else if (mode === 'systems')
      setActiveSystems({ ...off, shipping: true, cables: true });
    else if (mode === 'comms')
      setActiveSystems({ ...off, cables: true });
    else if (mode === 'climate')
      setActiveSystems({ ...off, energy: true, food: true, climate: true });
    else if (mode === 'data')
      setActiveSystems({ ...off, oil_gas: true, semiconductors: true, aviation: true });
  };

  // Fetch all backend data in parallel
  useEffect(() => {
    const systems = ['shipping', 'cables', 'energy', 'minerals', 'food', 'oil_gas', 'semiconductors', 'aviation', 'climate'];
    const store: Record<string, any> = {};

    // Auto-detect production backend (Railway) if not localhost
    const isLocal = typeof window !== 'undefined' && window.location.hostname === 'localhost';
    const fallbackApiUrl = isLocal ? 'http://localhost:8000' : 'https://invisible-systems-map-production.up.railway.app';
    const API_URL = process.env.NEXT_PUBLIC_API_URL || fallbackApiUrl;

    const fetchAll = async () => {
      await Promise.all(systems.map(async sys => {
        try {
          const r = await fetch(`${API_URL}/systems/${sys}`);
          store[sys] = r.ok ? await r.json() : { nodes: { features: [] }, connections: { features: [] } };
        } catch {
          store[sys] = { nodes: { features: [] }, connections: { features: [] } };
        }
      }));
      setLayersData(store);

      // Real-time conflicts from GDELT / Pipeline
      try {
        const r = await fetch(`${API_URL}/conflicts/realtime?t=${Date.now()}`, { cache: 'no-store' });
        if (r.ok) {
          const d = await r.json();
          setConflictsData(d.features || []);
          setConflictMeta(d.meta || null);
        }
      } catch {
        // fallback to static
        try {
          const r = await fetch(`${API_URL}/conflicts`);
          if (r.ok) { const d = await r.json(); setConflictsData(d.features || []); }
        } catch { /* ignore */ }
      }

    };

    fetchAll();
  }, []);

  const sharedProps = {
    layersData,
    activeSystems,
    onNodeClick: setSelectedNode,
    conflictsData,
  };

  return (
    <main className="relative w-screen h-screen overflow-hidden bg-slate-950">

      {/* Map / Globe */}
      {viewMode === '2d'
        ? <MapComponent {...sharedProps} />
        : <GlobeComponent {...sharedProps} />
      }

      {/* Top nav */}
      <TopNav activeMode={activeMode} onModeChange={handleModeChange} />

      {/* Left layer panel */}
      <LayerPanel
        activeSystems={activeSystems}
        toggleSystem={toggleSystem}
        liveConflictCount={conflictsData.length}
      />

      {/* Right info panel */}
      <InfoPanel node={selectedNode} onClose={() => setSelectedNode(null)} />

      {/* 2D / 3D view toggle (bottom-center) */}
      <div className="absolute bottom-12 left-1/2 -translate-x-1/2 z-10 flex items-center gap-1 glass-panel rounded-full p-1">
        <button
          onClick={() => setViewMode('2d')}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200"
          style={{
            background: viewMode === '2d' ? 'rgba(34,211,238,0.2)' : 'transparent',
            color: viewMode === '2d' ? '#22D3EE' : '#64748b',
          }}
        >
          <Map size={12} /> Flat Map
        </button>
        <button
          onClick={() => setViewMode('3d')}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200"
          style={{
            background: viewMode === '3d' ? 'rgba(99,102,241,0.2)' : 'transparent',
            color: viewMode === '3d' ? '#818CF8' : '#64748b',
          }}
        >
          <Globe2 size={12} /> 3D Globe
        </button>
      </div>

      {/* Attribution + live indicator */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-10">
        <div className="glass-panel rounded-full px-3 py-1 text-[9px] text-slate-500 tracking-wider flex items-center gap-2">
          {conflictMeta?.live ? (
            <><span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              GDELT Live · Updated {conflictMeta.cache_age_seconds < 60 ? 'just now' : `${Math.floor(conflictMeta.cache_age_seconds / 60)}m ago`}</>
          ) : (
            <><span className="w-1.5 h-1.5 rounded-full bg-amber-400" /> Intelligence Feed · TeleGeography · WRI · GDELT</>
          )}
        </div>
      </div>

    </main>
  );
}
