import React, { useState, useEffect, useRef } from "react";
import { Play, SkipForward, ArrowRight, Radar, Aperture, Fingerprint } from "lucide-react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Sphere, MeshDistortMaterial } from "@react-three/drei";

interface OnboardingProps {
  onComplete: () => void;
}

const STEPS = [
  {
    title: "Global Infrastructure Sets",
    description: "Toggle critical infrastructure layers on and off. Monitor cables, energy grids, and food trade routes in real-time.",
    position: "left-12 top-1/4", // align near left layer panel
  },
  {
    title: "Strategic Threat Modes",
    description: "Switch between holistic systems view, specialized tech flows, and live geopolitical conflict tracking.",
    position: "top-20 left-1/2 -translate-x-1/2", // align under top nav
  },
  {
    title: "Spatial Projections",
    description: "Toggle between a 3D orbital globe and a 2D flat tactical map to visualize global supply chain choke points.",
    position: "bottom-24 left-1/2 -translate-x-1/2", // align above map toggle
  },
  {
    title: "AI Analysis Hub",
    description: "Select any node or conflict event on the map to generate a live intelligence brief powered by Groq AI.",
    position: "right-12 top-1/4", // align near right info panel
  }
];

const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*";

const AnimatedCore = () => {
  const materialRef = useRef<any>(null);
  const wireframeRef = useRef<any>(null);
  const light1Ref = useRef<any>(null);
  const light2Ref = useRef<any>(null);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    
    // Seamlessly morph colors mathematically based on time (Cyan -> Indigo -> Magenta -> Cyan)
    if (materialRef.current) {
      // hue range roughly between 0.45 (Cyan) and 0.85 (Magenta)
      const h = 0.65 + Math.sin(t * 0.2) * 0.2;
      materialRef.current.emissive.setHSL(h, 0.9, 0.4);
    }

    // Slowly spin the wireframe casing
    if (wireframeRef.current) {
      wireframeRef.current.rotation.y = t * 0.05;
      wireframeRef.current.rotation.z = t * 0.02;
    }

    // Orbit the point lights for dramatic, sweeping neon reflections across the liquid
    if (light1Ref.current) {
      light1Ref.current.position.x = Math.sin(t * 0.5) * 10;
      light1Ref.current.position.z = Math.cos(t * 0.5) * 10;
    }
    if (light2Ref.current) {
      light2Ref.current.position.x = Math.sin(t * 0.4 + Math.PI) * 10;
      light2Ref.current.position.z = Math.cos(t * 0.4 + Math.PI) * 10;
    }
  });

  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={2} color="#ffffff" />
      
      {/* Orbiting Neon Lights */}
      <pointLight ref={light1Ref} position={[-10, 0, -10]} intensity={15} color="#00ffff" />
      <pointLight ref={light2Ref} position={[10, -5, 10]} intensity={15} color="#818cf8" />
      <pointLight position={[0, 10, 0]} intensity={10} color="#ec4899" /> {/* Violet/Pink top fill */}
      
      {/* Vibrant dynamic holographic core */}
      <Sphere visible args={[1, 128, 128]} scale={2.4}>
        <MeshDistortMaterial
          ref={materialRef}
          color="#020617" // dark tactical background
          emissiveIntensity={0.6}
          attach="material"
          distort={0.45}
          speed={1.5}
          roughness={0.15}
          metalness={0.9}
        />
      </Sphere>
      
      {/* Rotating wireframe mesh shell */}
      <Sphere ref={wireframeRef} visible args={[1.04, 32, 32]} scale={2.4}>
          <meshBasicMaterial
          color="#38bdf8"
          wireframe={true}
          transparent={true}
          opacity={0.15}
          />
      </Sphere>
    </>
  );
};

const GlitchText = ({ text }: { text: string }) => {
  const [displayText, setDisplayText] = useState("");
  
  useEffect(() => {
    let iteration = 0;
    const interval = setInterval(() => {
      setDisplayText(text.split("").map((letter, index) => {
        if(index < iteration) {
          return text[index];
        }
        return chars[Math.floor(Math.random() * chars.length)];
      }).join(""));
      
      if(iteration >= text.length){
        clearInterval(interval);
      }
      iteration += 1 / 4; // slow down the decoding slightly
    }, 30);
    
    return () => clearInterval(interval);
  }, [text]);

  return <>{displayText}</>;
};

export default function Onboarding({ onComplete }: OnboardingProps) {
  const [hasStarted, setHasStarted] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const hasSeen = localStorage.getItem("invisible_systems_onboarding");
    if (hasSeen === "true") {
      setHasStarted(true);
      onComplete();
    }
  }, [onComplete]);

  const handleInitialize = () => {
    setHasStarted(true);
  };

  const handleComplete = () => {
    localStorage.setItem("invisible_systems_onboarding", "true");
    onComplete();
  };

  if (!mounted) return null;

  // 1. Futuristic Entry Page
  if (!hasStarted) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-1000">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-cyan-500/10 rounded-full blur-[120px] mix-blend-screen" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-500/10 rounded-full blur-[100px] mix-blend-screen" />
        </div>

        {/* 3D Liquid Sphere Animation */}
        <div className="absolute inset-0 pointer-events-none opacity-90 flex items-center justify-center">
          <Canvas camera={{ position: [0, 0, 4] }}>
            <AnimatedCore />
          </Canvas>
        </div>

        {/* Removed the solid UI rectangle to let the sphere shine directly behind the text */}
        <div className="relative z-10 max-w-4xl w-full mx-4 p-4 text-center animate-in zoom-in-95 duration-700 delay-300 fill-mode-both">
          
          <div className="flex justify-center gap-8 mb-8 text-cyan-400">
            <Aperture size={32} className="opacity-80 animate-[spin_6s_linear_infinite]" />
            <Radar size={32} className="opacity-80 animate-[spin_3s_linear_infinite] text-indigo-400" />
            <Fingerprint size={32} className="opacity-80 animate-pulse" />
          </div>

          <h1 style={{ fontFamily: 'var(--font-jetbrains-mono, monospace)', minHeight: '60px', textShadow: '0 0 30px rgba(6,182,212,0.6)' }} 
              className="text-3xl sm:text-4xl md:text-6xl font-black text-transparent bg-clip-text bg-gradient-to-br from-white via-cyan-100 to-indigo-300 mb-6 uppercase tracking-[0.2em]">
            <GlitchText text="INVISIBLE SYSTEMS" />
          </h1>
          
          <p className="text-slate-200 text-xs sm:text-sm md:text-lg leading-relaxed mb-12 max-w-2xl mx-auto font-light tracking-wide rounded-xl bg-slate-950/40 backdrop-blur-md p-4 sm:p-6 border border-cyan-500/20 shadow-lg">
            Welcome to the terminal. This platform provides real-time visualization and intelligence on the covert infrastructure networks that power our world from submarine data conduits and energy grids to live geopolitical conflicts.
          </p>

          <div className="relative inline-flex group">
            <div className="absolute transition-all duration-1000 opacity-70 inset-0 bg-cyan-500 rounded-full blur-md group-hover:opacity-100 group-hover:-inset-1 group-hover:duration-200 animate-[pulse_2s_cubic-bezier(0.4,0,0.6,1)_infinite]"></div>
            <button 
              onClick={() => setHasStarted(true)}
              className="relative inline-flex items-center gap-3 px-6 sm:px-8 py-3 sm:py-4 bg-slate-950/90 border border-cyan-400/50 hover:bg-cyan-950/80 hover:border-cyan-300 text-cyan-300 rounded-full text-xs sm:text-sm font-bold tracking-widest uppercase transition-all duration-300"
            >
              <Play size={16} className="text-cyan-400 group-hover:text-cyan-300" />
              Initialize System
            </button>
          </div>
        </div>
      </div>
    );
  }

  // 2. Walkthrough Steps
  const step = STEPS[currentStep];

  return (
    <div className="fixed inset-0 z-50 pointer-events-none">
      {/* Darken background slightly to highlight UI elements */}
      <div className="absolute inset-0 bg-slate-950/40 backdrop-blur-[2px] pointer-events-auto transition-all duration-500" />
      
      {/* Step Card */}
      <div className={`absolute ${step.position} w-80 glass-panel border-cyan-500/40 p-5 rounded-xl text-left pointer-events-auto shadow-[0_0_30px_rgba(6,182,212,0.15)] animate-in fade-in slide-in-from-bottom-4 duration-500 transition-all`}>
        
        <div className="flex items-center justify-between mb-3">
          <span className="text-[10px] font-bold text-cyan-400 tracking-widest uppercase bg-cyan-500/10 px-2 py-1 rounded">
            Step {currentStep + 1} of {STEPS.length}
          </span>
          <button 
            onClick={onComplete}
            className="text-[10px] text-slate-500 hover:text-red-400 transition-colors flex items-center gap-1 uppercase tracking-wider font-bold"
          >
            <SkipForward size={10} /> Skip
          </button>
        </div>

        <h3 style={{ fontFamily: 'var(--font-space-grotesk, sans-serif)' }} 
            className="text-lg font-bold text-white mb-2">
          {step.title}
        </h3>
        
        <p className="text-xs text-slate-300 leading-relaxed mb-5">
          {step.description}
        </p>

        <div className="flex items-center justify-between">
          <div className="flex gap-1.5">
            {STEPS.map((_, i) => (
              <div key={i} className={`w-1.5 h-1.5 rounded-full transition-colors ${i === currentStep ? 'bg-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.8)]' : 'bg-slate-700'}`} />
            ))}
          </div>
          
          <button 
            onClick={() => {
              if (currentStep < STEPS.length - 1) {
                setCurrentStep(c => c + 1);
              } else {
                onComplete();
              }
            }}
            className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white rounded-lg text-xs font-bold transition-all shadow-lg shadow-cyan-500/20 active:scale-95"
          >
            {currentStep < STEPS.length - 1 ? 'Next Phase' : 'Access Map'}
            <ArrowRight size={14} />
          </button>
        </div>
      </div>
    </div>
  );
}
