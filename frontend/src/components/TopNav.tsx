"use client";

import React, { useState, useEffect } from 'react';
import { Globe, Wifi, Shield, Cloud, BarChart3, Volume2, VolumeX } from 'lucide-react';

interface TopNavProps {
  activeMode: string;
  onModeChange: (mode: string) => void;
}

const MODES = [
  { id: 'systems',   label: 'Global Systems',  icon: Globe,    color: '#22D3EE' },
  { id: 'conflicts', label: 'Conflict Intel',   icon: Shield,   color: '#EF4444' },
  { id: 'comms',     label: 'Cables & Comms',   icon: Wifi,     color: '#818CF8' },
  { id: 'climate',   label: 'Climate',          icon: Cloud,    color: '#34D399' },
  { id: 'data',      label: 'Data Flows',       icon: BarChart3,color: '#FBBF24' },
];

export default function TopNav({ activeMode, onModeChange }: TopNavProps) {
  const [audioEnabled, setAudioEnabled] = useState(false);

  useEffect(() => {
    let ctx: AudioContext;
    if (audioEnabled) {
      ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
      
      const gain = ctx.createGain();
      gain.gain.value = 0.03; // very soft ambient low hum
      gain.connect(ctx.destination);

      // Low A base
      const osc1 = ctx.createOscillator();
      osc1.type = 'sine';
      osc1.frequency.value = 55;
      osc1.connect(gain);
      
      // Slight detune for slow modulation
      const osc2 = ctx.createOscillator();
      osc2.type = 'triangle';
      osc2.frequency.value = 55.4;
      osc2.connect(gain);

      // E harmonic
      const osc3 = ctx.createOscillator();
      osc3.type = 'sine';
      osc3.frequency.value = 82.5; 
      const gain3 = ctx.createGain();
      gain3.gain.value = 0.01;
      gain3.connect(ctx.destination);
      osc3.connect(gain3);

      osc1.start();
      osc2.start();
      osc3.start();
    }
    return () => {
      if (ctx) ctx.close();
    };
  }, [audioEnabled]);

  return (
    <div className="absolute top-5 left-1/2 -translate-x-1/2 z-10 glass-panel rounded-2xl px-2 py-1.5 flex items-center gap-1 max-w-[calc(100vw-2rem)] overflow-x-auto scrollbar-hide">
      {MODES.map(m => {
        const Icon = m.icon;
        const isActive = activeMode === m.id;
        return (
          <button
            key={m.id}
            onClick={() => onModeChange(m.id)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition-all duration-200"
            style={{
              background: isActive ? `${m.color}18` : 'transparent',
              color: isActive ? m.color : '#64748b',
              border: isActive ? `1px solid ${m.color}30` : '1px solid transparent',
            }}
          >
            <Icon size={12} />
            <span className="hidden sm:inline">{m.label}</span>
          </button>
        );
      })}
      
      <div className="w-px h-6 bg-slate-700/50 mx-1 flex-shrink-0"></div>
      
      <button
        onClick={() => setAudioEnabled(!audioEnabled)}
        className="flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-xl text-slate-400 hover:text-cyan-400 hover:bg-cyan-900/20 transition-all duration-200"
        title="Toggle Ambient Audio"
      >
        {audioEnabled ? <Volume2 size={14} className="text-cyan-400" /> : <VolumeX size={14} />}
      </button>
    </div>
  );
}
