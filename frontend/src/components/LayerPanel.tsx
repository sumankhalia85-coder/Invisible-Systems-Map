"use client";

import React, { useState, useEffect } from 'react';
import { Ship, Wifi, Zap, Mountain, Wheat, Siren, ChevronDown, ChevronUp, Info, X, Flame, Cpu, Plane, CloudRain } from 'lucide-react';

interface LayerPanelProps {
  activeSystems: Record<string, boolean>;
  toggleSystem: (system: string) => void;
  liveConflictCount?: number;
}

const SYSTEM_CONFIG = [
  {
    id: 'shipping', name: 'Global Shipping', icon: Ship, color: '#22D3EE', accent: 'rgba(34,211,238,0.15)',
    info: {
      title: 'Global Shipping Routes & Ports',
      desc: '61 major commercial ports and shipping lanes carrying ~90% of world trade by volume. Disruptions can halt supply chains within days.',
      source: 'NGA World Port Index',
    }
  },
  {
    id: 'cables', name: 'Submarine Cables', icon: Wifi, color: '#818CF8', accent: 'rgba(129,140,248,0.15)',
    info: {
      title: 'Submarine Internet Cables',
      desc: '700+ undersea fiber-optic cables carrying 99% of intercontinental internet traffic. A cable cut can reroute an entire region.',
      source: 'TeleGeography',
    }
  },
  {
    id: 'energy', name: 'Energy Grid', icon: Zap, color: '#FBBF24', accent: 'rgba(251,191,36,0.15)',
    info: {
      title: 'Global Power Plants & Infrastructure',
      desc: '300+ real power plants including nuclear, hydro, solar, wind, coal, gas. From Three Gorges Dam to Hornsdale Wind Farm.',
      source: 'WRI Global Power Plant Database (real data)',
    }
  },
  {
    id: 'minerals', name: 'Rare Earth & Critical Minerals', icon: Mountain, color: '#A78BFA', accent: 'rgba(167,139,250,0.15)',
    info: {
      title: 'Critical Mineral Supply Chain',
      desc: 'Lithium, cobalt, rare earth elements, copper, nickel mines. The raw materials for EVs, chips, and weapons. Most controlled by China.',
      source: 'USGS / Curated',
    }
  },
  {
    id: 'food', name: 'Food Trade Flows', icon: Wheat, color: '#34D399', accent: 'rgba(52,211,153,0.15)',
    info: {
      title: 'Global Food Supply Chains',
      desc: 'Grain terminals, export hubs, and trade routes. Ukraine + Russia = 30% of global wheat. Disruption = food crisis for 800M people.',
      source: 'FAO / UN Trade Data',
    }
  },
  {
    id: 'oil_gas', name: 'Oil & LNG Chokepoints', icon: Flame, color: '#F97316', accent: 'rgba(249,115,22,0.15)',
    info: {
      title: 'Oil, Gas & Strategic Chokepoints',
      desc: 'Every oil chokepoint (Hormuz, Malacca, Suez, Bab-el-Mandeb), major LNG export terminals (Ras Laffan, Sabine Pass), pipelines, and refineries. The arteries of modern civilization.',
      source: 'EIA / IEA / Curated Intelligence',
    }
  },
  {
    id: 'semiconductors', name: 'Semiconductor Supply Chain', icon: Cpu, color: '#06B6D4', accent: 'rgba(6,182,212,0.15)',
    info: {
      title: 'Chip Supply Chain — The New Oil',
      desc: 'TSMC, ASML, Samsung fabs, silicon wafer factories, EUV equipment makers. 90% of advanced chips come from Taiwan. Taiwan invasion = global tech famine.',
      source: 'SEMI / Public Filings',
    }
  },
  {
    id: 'aviation', name: 'Aviation Cargo Corridors', icon: Plane, color: '#8B5CF6', accent: 'rgba(139,92,246,0.15)',
    info: {
      title: 'Air Cargo Hubs & No-Fly Zones',
      desc: 'Top cargo airports (HKG, MEM, ICN), key air corridors, and active no-fly zones (Ukraine, Russia, Iran, Israel). Air freight = chips, pharma, perishables.',
      source: 'IATA / ICAO NOTAMs',
    }
  },
  {
    id: 'conflicts', name: 'Conflict Intelligence', icon: Siren, color: '#EF4444', accent: 'rgba(239,68,68,0.15)',
    info: {
      title: 'Real-Time Global Conflict Events',
      desc: 'Live geo-tagged conflict events: Iran-Israel war, Russia-Ukraine, Gaza, Red Sea Houthi attacks, Sudan, Myanmar. GDELT-powered + curated intelligence.',
      source: 'GDELT Project (Live) + Curated Intel',
    },
    isLive: true,
  },
  {
    id: 'climate', name: 'Climate Monitor', icon: CloudRain, color: '#2DD4BF', accent: 'rgba(45,212,191,0.15)',
    info: {
      title: 'Real-Time Climate & Weather',
      desc: 'Live temperature, wind, and precipitation data from 30+ global cities. Identifies heat waves, cold snaps, severe storms, and anomalies in real time.',
      source: 'Open-Meteo (Live)',
    },
    isLive: true,
  },
];

// Color legend for all system types
const SYSTEM_COLORS = SYSTEM_CONFIG.map(s => ({ id: s.id, color: s.color, name: s.name.split(' ')[0] }));

export default function LayerPanel({ activeSystems, toggleSystem, liveConflictCount }: LayerPanelProps) {
  const [tooltip, setTooltip] = useState<string | null>(null);
  // Mobile: panel starts collapsed; Desktop: always expanded
  const [isMobile, setIsMobile] = useState(false);
  const [expanded, setExpanded] = useState(true);

  useEffect(() => {
    const check = () => {
      const mobile = window.innerWidth < 640;
      setIsMobile(mobile);
      if (mobile) setExpanded(false); // collapse on mobile by default
      else setExpanded(true);         // always open on desktop
    };
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  const toggleExpand = () => {
    if (isMobile) setExpanded(prev => !prev);
  };

  return (
    <div className={`absolute top-20 sm:top-5 left-2 sm:left-5 z-10 glass-panel rounded-2xl overflow-visible slide-in-left select-none flex flex-col
      ${isMobile ? 'w-[56px]' : 'w-64'}
      ${expanded && isMobile ? '!w-[calc(100vw-1rem)] max-h-[55vh]' : ''}
      transition-all duration-300`}
    >

      {/* Header — tappable on mobile to expand/collapse */}
      <button
        onClick={toggleExpand}
        className="glass-panel-header px-3 sm:px-4 py-3 flex items-center gap-2.5 w-full text-left"
      >
        <div className="w-7 h-7 rounded-xl flex items-center justify-center flex-shrink-0"
             style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.5), rgba(34,211,238,0.3))' }}>
          <Zap size={13} className="text-white" />
        </div>
        {(expanded || !isMobile) && (
          <div className="flex-1 min-w-0">
            <h2 style={{ fontFamily: 'var(--font-space-grotesk, sans-serif)' }}
                className="text-xs font-bold text-white tracking-widest uppercase leading-none">
              Invisible Systems
            </h2>
            <p className="text-[9px] text-slate-500 tracking-widest uppercase mt-0.5">Intelligence Platform</p>
          </div>
        )}
        {isMobile && (
          <div className="ml-auto flex-shrink-0">
            {expanded ? <ChevronUp size={12} className="text-slate-400" /> : <ChevronDown size={12} className="text-slate-400" />}
          </div>
        )}
        {!isMobile && <ChevronDown size={12} className="text-slate-600" />}
      </button>

      {/* Collapsible body */}
      {expanded && (
        <>
          <div className="px-2 py-1 border-b border-white/5">
            <p className="text-[9px] text-slate-600 uppercase tracking-widest px-1">Active Layers</p>
          </div>

          {/* Layer toggles */}
          <div className="p-1.5 space-y-0.5 overflow-y-auto custom-scrollbar flex-1 max-h-[35vh] sm:max-h-[55vh]">
            {SYSTEM_CONFIG.map((sys) => {
              const Icon = sys.icon;
              const isActive = activeSystems[sys.id];

              return (
                <div key={sys.id} className="relative">
                  <div className="flex items-center gap-0.5">
                    <button
                      onClick={() => toggleSystem(sys.id)}
                      className="flex-1 flex items-center gap-2 px-2.5 py-2 rounded-xl transition-all duration-200"
                      style={{
                        background: isActive ? sys.accent : 'transparent',
                        border: isActive ? `1px solid ${sys.color}25` : '1px solid transparent',
                      }}
                    >
                      <div className="w-6 h-6 rounded-lg flex items-center justify-center transition-all duration-200 flex-shrink-0"
                           style={{
                             background: isActive ? `${sys.color}28` : 'rgba(51,65,85,0.4)',
                             boxShadow: isActive ? `0 0 8px ${sys.color}25` : 'none',
                           }}>
                        <Icon size={11} style={{ color: isActive ? sys.color : '#475569' }} />
                      </div>
                      <div className="flex-1 min-w-0 text-left">
                        <span className="text-[11px] font-medium transition-colors duration-200 block leading-tight"
                              style={{ color: isActive ? '#e2e8f0' : '#64748b' }}>
                          {sys.name}
                        </span>
                        {sys.isLive && isActive && (
                          <span className="text-[9px] text-emerald-400 flex items-center gap-1 mt-0.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block animate-pulse" />
                            {sys.id === 'conflicts' && liveConflictCount ? `${liveConflictCount} events` : 'Live feed'}
                          </span>
                        )}
                      </div>
                      <div className="w-8 h-4 rounded-full relative flex-shrink-0 transition-all duration-300"
                           style={{ background: isActive ? sys.color : 'rgba(51,65,85,0.8)' }}>
                        <div className="absolute top-0.5 w-3 h-3 rounded-full bg-white shadow-sm transition-all duration-300"
                             style={{ left: isActive ? '17px' : '2px' }} />
                      </div>
                    </button>

                    <button
                      onClick={() => setTooltip(tooltip === sys.id ? null : sys.id)}
                      className="w-6 h-6 flex items-center justify-center rounded-lg text-slate-600 hover:text-slate-300 transition-colors"
                    >
                      <Info size={11} />
                    </button>
                  </div>

                  {/* Info tooltip — drops below on mobile, right on desktop */}
                  {tooltip === sys.id && (
                    <div className="absolute left-0 sm:left-full top-full sm:top-0 mt-1 sm:mt-0 sm:ml-2 z-[100] w-64 glass-panel rounded-xl p-3 slide-in-right shadow-xl"
                         style={{ border: `1px solid ${sys.color}30` }}>
                      <div className="flex justify-between items-start mb-2">
                        <h4 style={{ color: sys.color }} className="text-xs font-bold leading-snug flex-1">
                          {sys.info.title}
                        </h4>
                        <button onClick={() => setTooltip(null)} className="text-slate-600 hover:text-slate-300 ml-1">
                          <X size={11} />
                        </button>
                      </div>
                      <p className="text-[11px] text-slate-400 leading-relaxed mb-2">{sys.info.desc}</p>
                      <div className="flex items-center gap-1 text-[9px] text-slate-600">
                        <Info size={8} />
                        <span>{sys.info.source}</span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Layer color legend */}
          <div className="px-3 py-2 border-t border-white/5">
            <p className="text-[9px] text-slate-600 uppercase tracking-widest mb-2">Layer Colors</p>
            <div className="grid grid-cols-3 gap-x-2 gap-y-1">
              {SYSTEM_COLORS.map(s => (
                <div key={s.id} className="flex items-center gap-1">
                  <div className="w-2 h-2 rounded-full flex-shrink-0"
                       style={{ background: s.color, boxShadow: `0 0 4px ${s.color}80` }} />
                  <span className="text-[9px] text-slate-500 truncate">{s.name}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Conflict severity legend */}
          <div className="px-3 py-2 border-t border-white/5">
            <p className="text-[9px] text-slate-600 uppercase tracking-widest mb-1.5">Conflict Severity</p>
            <div className="flex items-center gap-2">
              {[
                { label: 'Low', color: '#6B7280', size: 'w-1.5 h-1.5' },
                { label: 'Med', color: '#F59E0B', size: 'w-2 h-2' },
                { label: 'High', color: '#EF4444', size: 'w-2.5 h-2.5' },
                { label: 'Crit', color: '#DC2626', size: 'w-3 h-3' },
              ].map(s => (
                <div key={s.label} className="flex items-center gap-1">
                  <div className={`${s.size} rounded-full`}
                       style={{ background: s.color, boxShadow: `0 0 4px ${s.color}80` }} />
                  <span className="text-[9px] text-slate-500">{s.label}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

    </div>
  );
}

