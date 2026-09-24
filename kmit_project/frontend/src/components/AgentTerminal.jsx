import React, { useState } from 'react';
import { Terminal, ChevronDown, ChevronUp, Cpu, Check, AlertCircle, ShieldAlert, Sparkles } from 'lucide-react';

export default function AgentTerminal({ traces = [], isRunning = false }) {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!traces || traces.length === 0) {
    if (!isRunning) return null;
  }

  const getStepIcon = (status) => {
    switch (status) {
      case 'SUCCESS':
        return <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />;
      case 'WARNING':
        return <AlertCircle className="w-3.5 h-3.5 text-amber-400 shrink-0" />;
      case 'PROTECTED':
        return <ShieldAlert className="w-3.5 h-3.5 text-[#68c7ff] shrink-0" />;
      default:
        return <Cpu className="w-3.5 h-3.5 text-[#6f55ef] shrink-0" />;
    }
  };

  return (
    <div className="veri-card mb-8 overflow-hidden font-mono text-xs border border-white/90 shadow-[0_10px_30px_rgba(23,19,45,0.06)]">
      {/* VeriVision Terminal Titlebar */}
      <div 
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between px-5 py-3.5 bg-white/70 backdrop-blur-md border-b border-[#6f55ef]/15 cursor-pointer select-none"
      >
        <div className="flex items-center gap-3">
          <div className="flex gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#ff3c6e]/80" />
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400/80" />
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400/80" />
          </div>
          <span className="text-[#17132d] font-[800] tracking-[1px] uppercase ml-1 flex items-center gap-2 font-sans text-xs">
            <Terminal className="w-4 h-4 text-[#6f55ef]" />
            Guardian Forensic Telemetry & Reasoning Pipeline
          </span>
          {isRunning && (
            <span className="flex items-center gap-1.5 text-[9px] px-2.5 py-0.5 rounded-full bg-[#6f55ef]/15 text-[#6f55ef] border border-[#6f55ef]/30 font-[900] tracking-[1px] uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-[#6f55ef] animate-ping" />
              SCANNING IN PROGRESS
            </span>
          )}
        </div>
        <div className="flex items-center gap-3 text-[#17132d]/60 font-sans">
          <span className="text-[10px] font-[800] tracking-[1px] uppercase bg-[#6f55ef]/10 text-[#6f55ef] px-2.5 py-0.5 rounded-md border border-[#6f55ef]/20">
            {traces.length} Traces Logged
          </span>
          {isExpanded ? <ChevronUp className="w-4 h-4 text-[#6f55ef]" /> : <ChevronDown className="w-4 h-4 text-[#6f55ef]" />}
        </div>
      </div>

      {/* VeriVision Midnight Console Area */}
      {isExpanded && (
        <div className="relative p-5 max-h-64 overflow-y-auto space-y-2.5 bg-[#17132d] text-[#ede8ff] selection:bg-[#6f55ef]/40">
          {/* Animated Purple Scan Line */}
          {isRunning && <div className="scan-line pointer-events-none" />}

          {traces.length === 0 && isRunning && (
            <div className="flex items-center gap-2.5 text-[#6f55ef] font-[700] py-3 tracking-wide">
              <div className="w-3.5 h-3.5 border-2 border-[#6f55ef] border-t-transparent rounded-full animate-spin" />
              <span>Orchestrator pipeline executing financial forensics...</span>
            </div>
          )}

          {traces.map((trace, idx) => (
            <div key={idx} className="flex items-start gap-2.5 leading-relaxed font-mono">
              <span className="text-[#17132d]/40 text-slate-400 shrink-0 text-[11px] font-sans">
                {trace.timestamp || '00:00'}
              </span>
              <div className="mt-0.5">{getStepIcon(trace.status)}</div>
              <span className="text-[#6f55ef] shrink-0 font-[800]">
                [{trace.step}]
              </span>
              <span className={`break-words ${
                trace.status === 'WARNING' ? 'text-amber-300' :
                trace.status === 'PROTECTED' ? 'text-[#68c7ff]' :
                'text-[#f4f1ff]'
              }`}>
                {trace.message}
              </span>
            </div>
          ))}

          {isRunning && (
            <div className="flex items-center gap-2 text-[#6f55ef] pt-1">
              <span className="animate-ping text-[#6f55ef]">_</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
