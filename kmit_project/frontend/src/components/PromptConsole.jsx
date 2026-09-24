import React, { useState } from 'react';
import { 
  Sparkles, 
  Send, 
  Bot, 
  Zap, 
  HelpCircle, 
  CheckCircle, 
  AlertTriangle, 
  ShieldCheck, 
  X,
  Clock,
  ArrowRight,
  RotateCcw
} from 'lucide-react';

export default function PromptConsole({ 
  onExecutePrompt, 
  isProcessing = false, 
  promptResponse = null, 
  onClearResponse = () => {},
  onOpenApprovals = () => {}
}) {
  const [promptInput, setPromptInput] = useState('');
  const [promptHistory, setPromptHistory] = useState([
    "Audit my subscriptions and cancel inactive ones under guardrail limits",
    "What is my total monthly spend and active burn rate?",
    "Scan for price hikes and email alerts"
  ]);

  const suggestedPrompts = [
    {
      label: "Input 1: StreamFlix Inactive (Auto-Cancel)",
      prompt: "INPUT 1: StreamFlix unused 187 days, under limit, auto-cancel",
      type: "auto-cancel"
    },
    {
      label: "Input 2: TuneWave vs MusicBox (Ambiguity)",
      prompt: "INPUT 2: TuneWave vs MusicBox duplicate category, escalate to human",
      type: "duplicate"
    },
    {
      label: "Input 3: HealthGuard Insurance (Protected)",
      prompt: "INPUT 3: HealthGuard Insurance in protected category, block autonomy",
      type: "protected"
    },
    {
      label: "Scan Price Hikes",
      prompt: "Which subscriptions have unscheduled price hikes?",
      type: "inquiry"
    },
    {
      label: "Total Monthly Spend",
      prompt: "What is my total monthly recurring spend?",
      type: "inquiry"
    },
    {
      label: "Savings Summary",
      prompt: "How much money am I saving each month?",
      type: "inquiry"
    },
    {
      label: "Check Guardrails",
      prompt: "What are my currently configured safety guardrails?",
      type: "inquiry"
    }
  ];

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    const clean = promptInput.trim();
    if (!clean || isProcessing) return;

    // Add to history
    if (!promptHistory.includes(clean)) {
      setPromptHistory(prev => [clean, ...prev.slice(0, 4)]);
    }

    onExecutePrompt(clean);
  };

  const handleSelectPrompt = (p) => {
    setPromptInput(p);
    if (!isProcessing) {
      if (!promptHistory.includes(p)) {
        setPromptHistory(prev => [p, ...prev.slice(0, 4)]);
      }
      onExecutePrompt(p);
    }
  };

  return (
    <div className="veri-card mb-8">
      {/* Header telemetry */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-purple-100/60">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#6f55ef] to-[#5136db] flex items-center justify-center text-white shadow-md shadow-[#6f55ef]/20">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-[800] uppercase tracking-[2px] text-[#6f55ef]">
                Autonomous Prompt Interface
              </span>
              <span className="text-[9px] bg-[#6f55ef]/10 text-[#6f55ef] px-2 py-0.5 rounded-full font-mono font-[800] tracking-wider uppercase border border-[#6f55ef]/20">
                Natural Language Engine
              </span>
            </div>
            <h3 className="text-base font-[900] text-[#17132d] tracking-tight">
              SpendGuardian Prompt Console
            </h3>
          </div>
        </div>

        <div className="flex items-center gap-2 bg-[#f8f6ff] border border-purple-100 px-3 py-1.5 rounded-full">
          <span className="hud-dot" />
          <span className="text-[10px] font-[800] tracking-[1px] text-[#17132d] uppercase">
            {isProcessing ? "Processing Telemetry..." : "Online • Ready For Input"}
          </span>
        </div>
      </div>

      {/* Main Prompt Input Box */}
      <form onSubmit={handleSubmit} className="mb-4">
        <div className="relative flex items-center bg-white/90 border border-purple-200/80 rounded-2xl p-2 shadow-[0_4px_16px_rgba(111,85,239,0.06)] focus-within:border-[#6f55ef] focus-within:ring-4 focus-within:ring-[#6f55ef]/15 transition-all">
          <div className="pl-3 pr-2 text-[#6f55ef]">
            <Sparkles className="w-5 h-5 animate-pulse" />
          </div>

          <input
            type="text"
            value={promptInput}
            onChange={(e) => setPromptInput(e.target.value)}
            disabled={isProcessing}
            placeholder="Type an instruction or question (e.g. 'Audit my subscriptions', 'Cancel StreamFlix', 'What is my total spend?')..."
            className="flex-1 bg-transparent px-2 py-2 text-xs sm:text-sm text-[#17132d] placeholder-[#17132d]/40 font-medium focus:outline-none disabled:opacity-60"
          />

          {promptInput && !isProcessing && (
            <button
              type="button"
              onClick={() => setPromptInput('')}
              className="p-1.5 mr-1 text-[#17132d]/40 hover:text-[#17132d] rounded-lg transition-colors"
              title="Clear input"
            >
              <X className="w-4 h-4" />
            </button>
          )}

          <button
            type="submit"
            disabled={isProcessing || !promptInput.trim()}
            className="bg-gradient-to-r from-[#6f55ef] to-[#5136db] hover:opacity-95 text-white font-[800] text-xs uppercase tracking-[1px] px-5 py-2.5 rounded-xl shadow-md shadow-[#6f55ef]/25 flex items-center gap-2 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
          >
            {isProcessing ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Executing...</span>
              </>
            ) : (
              <>
                <Send className="w-3.5 h-3.5" />
                <span>Run Prompt</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Suggested Fast-Click Prompt Pills */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-[800] uppercase tracking-[1.5px] text-[#17132d]/50">
            Suggested Prompts & Problem Scenarios:
          </span>
        </div>

        <div className="flex flex-wrap gap-2">
          {suggestedPrompts.map((s, idx) => {
            let badgeColor = "bg-white/80 hover:bg-[#6f55ef]/10 border-purple-200/70 text-[#17132d]";
            if (s.type === "auto-cancel") {
              badgeColor = "bg-white/80 hover:bg-emerald-500/10 border-emerald-200 text-emerald-900";
            } else if (s.type === "duplicate") {
              badgeColor = "bg-white/80 hover:bg-amber-500/10 border-amber-200 text-amber-900";
            } else if (s.type === "protected") {
              badgeColor = "bg-white/80 hover:bg-[#68c7ff]/20 border-cyan-200 text-[#5136db]";
            }

            return (
              <button
                key={idx}
                type="button"
                onClick={() => handleSelectPrompt(s.prompt)}
                disabled={isProcessing}
                className={`px-3 py-1.5 rounded-xl text-[11px] font-[700] border transition-all active:scale-95 shadow-xs flex items-center gap-1.5 ${badgeColor}`}
              >
                <Zap className="w-3 h-3 text-[#6f55ef]" />
                {s.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Real-Time Agent Response Card */}
      {promptResponse && (
        <div className="mt-5 p-4 rounded-2xl bg-[#f8f6ff]/90 border border-purple-200/80 shadow-[0_8px_24px_rgba(111,85,239,0.06)] relative animate-in fade-in slide-in-from-top-2 duration-300">
          <button
            onClick={onClearResponse}
            className="absolute top-3 right-3 p-1 rounded-lg text-[#17132d]/40 hover:text-[#17132d] hover:bg-purple-100/50 transition-colors"
            title="Dismiss response"
          >
            <X className="w-4 h-4" />
          </button>

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2 pb-2 border-b border-purple-100/60 pr-8">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-[800] uppercase tracking-[1.5px] text-[#6f55ef] bg-[#ede8ff] px-2.5 py-0.5 rounded-md border border-purple-200/60">
                {promptResponse.intent || 'AGENT RESPONSE'}
              </span>
              <span className="text-xs text-[#17132d]/60 font-medium truncate max-w-md">
                Prompt: "{promptResponse.prompt}"
              </span>
            </div>

            {promptResponse.monthly_savings > 0 && (
              <span className="text-[11px] font-[800] text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full">
                +{promptResponse.currency || '₹'}{promptResponse.monthly_savings.toLocaleString()}/mo Saved
              </span>
            )}
          </div>

          <div className="text-xs sm:text-sm text-[#17132d] font-medium leading-relaxed whitespace-pre-line">
            {promptResponse.reply}
          </div>

          {/* Quick Action Navigation if escalation or audit took place */}
          {promptResponse.intent === 'AUDIT_EXECUTION' && (
            <div className="mt-3 pt-2.5 border-t border-purple-100/60 flex items-center justify-between">
              <span className="text-[11px] text-[#17132d]/60 font-medium">
                Audit results applied across all monitored cards below
              </span>
              <button
                onClick={onOpenApprovals}
                className="text-[11px] font-[800] text-[#6f55ef] hover:text-[#5136db] flex items-center gap-1 uppercase tracking-wider"
              >
                Review Approval Queue
                <ArrowRight className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
