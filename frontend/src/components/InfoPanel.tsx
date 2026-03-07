/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import React, { useState, useEffect } from 'react';
import { X, MapPin, Users, Calendar, AlertTriangle, BrainCircuit, Shield, Crosshair, Lock, Sparkles, Radio, ChevronDown, ChevronUp } from 'lucide-react';

interface InfoPanelProps {
  node: Record<string, any> | null;
  onClose: () => void;
}

const SYSTEM_META: Record<string, { color: string; bg: string; label: string }> = {
  shipping:       { color: '#22D3EE', bg: 'rgba(34,211,238,0.1)',   label: 'Shipping' },
  cables:         { color: '#818CF8', bg: 'rgba(129,140,248,0.1)', label: 'Cables' },
  energy:         { color: '#FBBF24', bg: 'rgba(251,191,36,0.1)',  label: 'Energy' },
  minerals:       { color: '#A78BFA', bg: 'rgba(167,139,250,0.1)', label: 'Minerals' },
  food:           { color: '#34D399', bg: 'rgba(52,211,153,0.1)',  label: 'Food' },
  conflicts:      { color: '#EF4444', bg: 'rgba(239,68,68,0.1)',   label: 'Conflict' },
  oil_gas:        { color: '#F97316', bg: 'rgba(249,115,22,0.1)',  label: 'Oil & Gas' },
  semiconductors: { color: '#06B6D4', bg: 'rgba(6,182,212,0.1)',   label: 'Semiconductors' },
  aviation:       { color: '#8B5CF6', bg: 'rgba(139,92,246,0.1)', label: 'Aviation' },
};

const EVENT_TYPE_META: Record<string, { label: string; color: string }> = {
  battle:            { label: '⚔️ Battle', color: '#EF4444' },
  airstrike:         { label: '✈️ Air Strike', color: '#F97316' },
  missile:           { label: '🚀 Missile', color: '#EAB308' },
  bombing:           { label: '💣 Bombing', color: '#A855F7' },
  civilian_violence: { label: '🚨 Civil Violence', color: '#EC4899' },
  protest:           { label: '✊ Protest', color: '#3B82F6' },
  riot:              { label: '🔥 Riot', color: '#14B8A6' },
  geopolitical:      { label: '🌐 Geopolitical', color: '#94A3B8' },
  massacre:          { label: '💀 Massacre', color: '#7F1D1D' },
};

const SEVERITY_META: Record<string, { label: string; color: string }> = {
  low:      { label: 'Low', color: '#6B7280' },
  medium:   { label: 'Medium', color: '#F59E0B' },
  high:     { label: 'High', color: '#EF4444' },
  critical: { label: 'Critical ⚠️', color: '#DC2626' },
};

const SKIP_KEYS = new Set(['id','name','type','system','coordinates','event_type','severity','date','actors','fatalities','description','source','source_position','target_position','from','to','from_name','to_name','flow_type','route_type','intensity']);
const safeStr = (v: any) => typeof v === 'string' ? v.replace(/_/g,' ') : String(v ?? '');

export default function InfoPanel({ node, onClose }: InfoPanelProps) {
  const [teaser, setTeaser] = useState<string | null>(null);
  const [fullAnalysis, setFullAnalysis] = useState<string | null>(null);
  const [loadingFree, setLoadingFree] = useState(false);
  const [loadingPremium, setLoadingPremium] = useState(false);
  const [hasApiKey, setHasApiKey] = useState(false);
  const [premiumExpanded, setPremiumExpanded] = useState(false);

  // Reset on new node, fetch free teaser
  useEffect(() => {
    if (!node) return;
    // Resetting state for new node selection — intentional
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setTeaser(null);
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setFullAnalysis(null);
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setPremiumExpanded(false);
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoadingFree(true);

    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ node, premium: false })
    })
      .then(r => r.json())
      .then(d => {
        setTeaser(d.teaser);
        setHasApiKey(d.has_api_key);
        setLoadingFree(false);
      })
      .catch(() => setLoadingFree(false));
  }, [node]);

  const fetchPremium = () => {
    if (!node || loadingPremium || fullAnalysis) return;
    setLoadingPremium(true);
    setPremiumExpanded(true);
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ node, premium: true })
    })
      .then(r => r.json())
      .then(d => { setFullAnalysis(d.full_analysis); setLoadingPremium(false); })
      .catch(() => setLoadingPremium(false));
  };

  if (!node) return null;

  const system = node.system || 'unknown';
  const meta = SYSTEM_META[system] || { color: '#94A3B8', bg: 'rgba(148,163,184,0.1)' };
  const isConflict = system === 'conflicts';
  const coords = node.coordinates || [0, 0];
  const latStr = `${Math.abs(coords[1] ?? 0).toFixed(3)}°${(coords[1] ?? 0) >= 0 ? 'N' : 'S'}`;
  const lngStr = `${Math.abs(coords[0] ?? 0).toFixed(3)}°${(coords[0] ?? 0) >= 0 ? 'E' : 'W'}`;
  const evtMeta = EVENT_TYPE_META[node.event_type || ''];
  const sevMeta = SEVERITY_META[node.severity || ''];

  return (
    <div
      className="absolute bottom-0 sm:bottom-5 right-0 sm:right-5 z-20 glass-panel rounded-t-2xl sm:rounded-2xl rounded-b-none sm:rounded-b-2xl overflow-hidden slide-in-right w-full sm:w-[340px]"
      style={{ maxHeight: '80vh', overflowY: 'auto' }}
    >

      {/* ── Header band ── */}
      <div className="px-5 pt-4 pb-3 border-b border-white/5" style={{ background: `linear-gradient(135deg, ${meta.bg}, transparent)` }}>
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap gap-1 mb-2">
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full"
                    style={{ color: meta.color, background: meta.bg, border: `1px solid ${meta.color}30` }}>
                {safeStr(node.system)}
              </span>
              {isConflict && evtMeta && (
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full"
                      style={{ color: evtMeta.color, background: `${evtMeta.color}18`, border: `1px solid ${evtMeta.color}30` }}>
                  {evtMeta.label}
                </span>
              )}
              {!isConflict && node.type && (
                <span className="text-[10px] px-2 py-0.5 rounded-full text-slate-400 bg-slate-800/60 border border-slate-700/40">
                  {safeStr(node.type)}
                </span>
              )}
            </div>
            <h3 style={{ fontFamily: 'var(--font-space-grotesk, sans-serif)' }}
                className="font-bold text-white text-sm leading-snug">
              {node.name || 'Unknown'}
            </h3>
          </div>
          <button onClick={onClose}
            className="w-7 h-7 rounded-lg flex items-center justify-center text-slate-500 hover:text-white transition-colors flex-shrink-0 bg-slate-800/50">
            <X size={13} />
          </button>
        </div>
      </div>

      <div className="px-5 py-4 space-y-3">

        {/* Coordinates + Country */}
        <div className="flex items-center gap-2">
          <MapPin size={12} className="text-slate-500" />
          <span className="text-xs font-mono text-slate-400">{latStr}, {lngStr}</span>
          {node.country && <span className="ml-auto text-xs text-slate-400">{node.country}</span>}
        </div>

        {/* ── Conflict-specific ── */}
        {isConflict && (
          <div className="space-y-2">
            {/* Severity + Fatalities */}
            <div className="grid grid-cols-2 gap-2">
              {sevMeta && (
                <div className="rounded-xl p-2.5 border border-white/5" style={{ background: `${sevMeta.color}12` }}>
                  <div className="text-[9px] text-slate-500 uppercase tracking-wider flex items-center gap-1 mb-0.5">
                    <Shield size={8}/> Severity
                  </div>
                  <div className="text-xs font-bold" style={{ color: sevMeta.color }}>{sevMeta.label}</div>
                </div>
              )}
              <div className="rounded-xl p-2.5 border border-white/5 bg-slate-800/30">
                <div className="text-[9px] text-slate-500 uppercase tracking-wider flex items-center gap-1 mb-0.5">
                  <AlertTriangle size={8}/> Fatalities
                </div>
                <div className="text-xs font-bold text-slate-200">
                  {(node.fatalities ?? 0) > 0 ? `~${Number(node.fatalities).toLocaleString()}` : 'Unknown'}
                </div>
              </div>
            </div>

            {/* Date + Source */}
            {node.date && (
              <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                <Calendar size={10}/>
                <span>{node.date}</span>
                {node.source && <span className="ml-auto text-slate-500">via {node.source}</span>}
              </div>
            )}

            {/* Actors */}
            {Array.isArray(node.actors) && node.actors.length > 0 && (
              <div className="rounded-xl p-2.5 bg-slate-800/30 border border-white/5">
                <div className="text-[9px] text-slate-500 uppercase tracking-wider flex items-center gap-1 mb-1.5"><Users size={8}/> Actors</div>
                <div className="flex flex-wrap gap-1">
                  {node.actors.slice(0,4).map((a: string, i: number) => (
                    <span key={i} className="text-[10px] px-1.5 py-0.5 rounded-md bg-slate-700/60 text-slate-300">{a}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Description */}
            {node.description && node.description.length > 5 && (
              <div className="rounded-xl p-2.5 bg-slate-800/20 border border-white/5">
                <div className="text-[9px] text-slate-500 flex items-center gap-1 mb-1"><Crosshair size={8}/> Summary</div>
                <p className="text-[11px] text-slate-300 leading-relaxed">{node.description}</p>
              </div>
            )}
          </div>
        )}

        {/* ── Route/flow-specific display (for arc clicks) ── */}
        {(node.from || node.to) && (
          <div className="rounded-xl p-3 border border-white/10 space-y-2" style={{ background: `${meta.bg}` }}>
            <div className="text-[9px] text-slate-500 uppercase tracking-widest font-bold flex items-center gap-1">
              <span style={{ color: meta.color }}>▶</span> Flow Route
            </div>
            {node.from && (
              <div className="flex items-start gap-2">
                <span className="text-[9px] text-slate-500 uppercase w-12 flex-shrink-0 mt-0.5">From</span>
                <span className="text-[11px] text-slate-200 leading-snug font-medium">{node.from}</span>
              </div>
            )}
            <div className="w-full flex items-center gap-1.5">
              <div className="flex-1 h-px" style={{ background: `linear-gradient(90deg, ${meta.color}60, ${meta.color}20)` }} />
              <span className="text-[9px]" style={{ color: meta.color }}>→</span>
              <div className="flex-1 h-px" style={{ background: `linear-gradient(90deg, ${meta.color}20, ${meta.color}60)` }} />
            </div>
            {node.to && (
              <div className="flex items-start gap-2">
                <span className="text-[9px] text-slate-500 uppercase w-12 flex-shrink-0 mt-0.5">To</span>
                <span className="text-[11px] text-slate-200 leading-snug font-medium">{node.to}</span>
              </div>
            )}
          </div>
        )}

        {/* ── Non-conflict extra props ── */}
        {!isConflict && (
          <div className="space-y-1.5 border-t border-white/5 pt-2">
            {Object.entries(node)
              .filter(([k]) => !SKIP_KEYS.has(k))
              .slice(0, 6)
              .map(([k, v]) => (
                <div key={k} className="flex justify-between items-start gap-2">
                  <span className="text-[10px] text-slate-500 uppercase tracking-wide capitalize flex-shrink-0 w-24">{k.replace(/_/g,' ')}</span>
                  <span className="text-[11px] text-slate-300 text-right font-medium">
                    {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                  </span>
                </div>
              ))
            }
          </div>
        )}

        {/* ══════════════════════════════════════════
            FREE TIER — AI Teaser
        ══════════════════════════════════════════ */}
        <div className="border-t border-white/5 pt-3 space-y-2">
          <div className="flex items-center gap-2">
            <Radio size={10} className="text-indigo-400" />
            <span style={{ fontFamily: 'var(--font-space-grotesk, sans-serif)' }}
                  className="text-[9px] font-bold uppercase tracking-widest text-slate-500">
              Pulse Intelligence
            </span>
          </div>

          {loadingFree ? (
            <div className="space-y-1.5">
              {[1, 0.75].map((w, i) => <div key={i} className="shimmer h-2 rounded-full" style={{ width: `${w*100}%` }} />)}
            </div>
          ) : (
            teaser && (
              <p className="text-[11px] text-slate-400 leading-relaxed italic border-l-2 border-indigo-500/40 pl-2">
                {teaser}
              </p>
            )
          )}
        </div>

        {/* ══════════════════════════════════════════
            PREMIUM TIER — Full AI Brief
        ══════════════════════════════════════════ */}
        <div className="rounded-xl overflow-hidden border border-indigo-500/20"
             style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.08), rgba(139,92,246,0.05))' }}>

          {/* Header */}
          <div className="px-3 py-2.5 flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <Sparkles size={11} className="text-indigo-400" />
              <span style={{ fontFamily: 'var(--font-space-grotesk, sans-serif)' }}
                    className="text-[10px] font-bold text-indigo-300 uppercase tracking-widest">
                Pulse Pro Brief
              </span>
              <span className="text-[9px] bg-indigo-500/30 text-indigo-300 px-1.5 py-0.5 rounded-full font-bold">PRO</span>
            </div>
            {fullAnalysis && (
              <button onClick={() => setPremiumExpanded(e => !e)}
                      className="text-slate-500 hover:text-slate-300 transition-colors">
                {premiumExpanded ? <ChevronUp size={12}/> : <ChevronDown size={12}/>}
              </button>
            )}
          </div>

          {/* Content */}
          <div className="px-3 pb-3">
            {!hasApiKey ? (
              /* No API key — show lock */
              <div className="text-center py-3">
                <Lock size={18} className="text-slate-600 mx-auto mb-1.5" />
                <p className="text-[10px] text-slate-500">Set <code className="text-indigo-400">OPENAI_API_KEY</code> in <code className="text-slate-400">.env</code> to unlock</p>
              </div>
            ) : loadingPremium ? (
              <div className="space-y-1.5">
                {[1, 0.9, 0.8, 0.6].map((w, i) => <div key={i} className="shimmer h-2 rounded-full" style={{ width: `${w*100}%` }} />)}
              </div>
            ) : fullAnalysis && premiumExpanded ? (
              <p className="text-[11px] text-slate-300 leading-relaxed whitespace-pre-wrap">{fullAnalysis}</p>
            ) : !fullAnalysis ? (
              /* CTA to unlock */
              <button onClick={fetchPremium}
                      className="w-full py-2 rounded-lg text-xs font-semibold transition-all duration-200 flex items-center justify-center gap-2"
                      style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.4), rgba(139,92,246,0.4))', color: '#C7D2FE', border: '1px solid rgba(99,102,241,0.4)' }}>
                <BrainCircuit size={13} />
                Generate Full Intelligence Brief
              </button>
            ) : null}
          </div>
        </div>

      </div>
    </div>
  );
}
