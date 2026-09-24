import React from 'react';
import { 
  ShieldCheck, 
  Play, 
  Sliders, 
  FileText, 
  RotateCcw, 
  Layers, 
  CheckCircle2, 
  AlertTriangle,
  Database,
  Plus
} from 'lucide-react';

export default function Navbar({ 
  activeTab, 
  setActiveTab, 
  onRunAudit, 
  isRunningAudit, 
  onOpenGuardrails, 
  onOpenReport, 
  onResetDemo,
  onOpenAddSubscription,
  pendingApprovalsCount = 0
}) {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-[#6f55ef]/15 bg-[#f4f1ff]/80 backdrop-blur-2xl transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          
          {/* VeriVision Brand Logo & Tagline */}
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#6f55ef] to-[#5136db] p-0.5 shadow-md shadow-[#6f55ef]/30 flex items-center justify-center">
              <div className="w-full h-full bg-white rounded-[10px] flex items-center justify-center">
                <ShieldCheck className="w-5 h-5 text-[#6f55ef]" />
              </div>
            </div>
            <div>
              <div className="text-[16px] font-[900] tracking-[3px] uppercase text-[#17132d]">
                SpendGuardian
              </div>
              <span className="block text-[8px] font-[800] tracking-[1.5px] uppercase text-[#6f55ef]">
                Autonomous AI Waste Forensics
              </span>
            </div>
          </div>

          {/* Center HUD status pill */}
          <div className="hidden lg:flex items-center gap-2 bg-white/75 backdrop-blur-md border border-[#6f55ef]/20 px-3.5 py-1.5 rounded-full shadow-[0_4px_15px_rgba(111,85,239,0.08)]">
            <span className="hud-dot" />
            <span className="text-[10px] font-[800] tracking-[1px] text-[#17132d] uppercase">
              AI Guardian Engine Active
            </span>
          </div>

          {/* Navigation Tabs (VeriVision Pill Style) */}
          <nav className="hidden md:flex items-center gap-1.5 bg-white/60 backdrop-blur-lg p-1.5 rounded-full border border-[#6f55ef]/15 shadow-xs">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`px-3.5 py-1.5 rounded-full text-[11px] font-[800] tracking-[1.5px] uppercase transition-all ${
                activeTab === 'dashboard'
                  ? 'bg-[#6f55ef] text-white shadow-md shadow-[#6f55ef]/30'
                  : 'text-[#17132d]/70 hover:text-[#6f55ef] hover:bg-[#6f55ef]/10'
              }`}
            >
              Control Center
            </button>

            <button
              onClick={() => setActiveTab('approvals')}
              className={`relative px-3.5 py-1.5 rounded-full text-[11px] font-[800] tracking-[1.5px] uppercase transition-all ${
                activeTab === 'approvals'
                  ? 'bg-[#6f55ef] text-white shadow-md shadow-[#6f55ef]/30'
                  : 'text-[#17132d]/70 hover:text-[#6f55ef] hover:bg-[#6f55ef]/10'
              }`}
            >
              <span className="flex items-center gap-1.5">
                Approvals
                {pendingApprovalsCount > 0 && (
                  <span className={`inline-flex items-center justify-center px-1.5 py-0.5 text-[9px] font-[900] leading-none rounded-full ${
                    activeTab === 'approvals' 
                      ? 'bg-white text-[#6f55ef]' 
                      : 'bg-[#ff3c6e] text-white animate-pulse'
                  }`}>
                    {pendingApprovalsCount}
                  </span>
                )}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('subscriptions')}
              className={`px-3.5 py-1.5 rounded-full text-[11px] font-[800] tracking-[1.5px] uppercase transition-all ${
                activeTab === 'subscriptions'
                  ? 'bg-[#6f55ef] text-white shadow-md shadow-[#6f55ef]/30'
                  : 'text-[#17132d]/70 hover:text-[#6f55ef] hover:bg-[#6f55ef]/10'
              }`}
            >
              Subscriptions
            </button>

            <button
              onClick={() => setActiveTab('negotiation_hub')}
              className={`px-3.5 py-1.5 rounded-full text-[11px] font-[800] tracking-[1.5px] uppercase transition-all ${
                activeTab === 'negotiation_hub'
                  ? 'bg-[#6f55ef] text-white shadow-md shadow-[#6f55ef]/30'
                  : 'text-[#17132d]/70 hover:text-[#6f55ef] hover:bg-[#6f55ef]/10'
              }`}
            >
              Negotiation Mode
            </button>

            <button
              onClick={() => setActiveTab('audit_trail')}
              className={`px-3.5 py-1.5 rounded-full text-[11px] font-[800] tracking-[1.5px] uppercase transition-all ${
                activeTab === 'audit_trail'
                  ? 'bg-[#6f55ef] text-white shadow-md shadow-[#6f55ef]/30'
                  : 'text-[#17132d]/70 hover:text-[#6f55ef] hover:bg-[#6f55ef]/10'
              }`}
            >
              Audit Trail
            </button>

            <button
              onClick={() => setActiveTab('data_feeds')}
              className={`px-3.5 py-1.5 rounded-full text-[11px] font-[800] tracking-[1.5px] uppercase transition-all ${
                activeTab === 'data_feeds'
                  ? 'bg-[#6f55ef] text-white shadow-md shadow-[#6f55ef]/30'
                  : 'text-[#17132d]/70 hover:text-[#6f55ef] hover:bg-[#6f55ef]/10'
              }`}
            >
              Data Feeds
            </button>
          </nav>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            <button
              onClick={onOpenGuardrails}
              title="Configure Guardrails"
              className="p-2 text-[#17132d]/70 hover:text-[#6f55ef] hover:bg-[#6f55ef]/10 rounded-xl transition-all border border-[#6f55ef]/15 bg-white/60"
            >
              <Sliders className="w-4 h-4" />
            </button>

            <button
              onClick={onOpenReport}
              title="View Monthly Savings Report"
              className="p-2 text-[#17132d]/70 hover:text-[#6f55ef] hover:bg-[#6f55ef]/10 rounded-xl transition-all border border-[#6f55ef]/15 bg-white/60"
            >
              <FileText className="w-4 h-4" />
            </button>

            <button
              onClick={onResetDemo}
              title="Reset Demo Data"
              className="p-2 text-[#17132d]/70 hover:text-[#ff3c6e] hover:bg-[#ff3c6e]/10 rounded-xl transition-all border border-[#6f55ef]/15 bg-white/60"
            >
              <RotateCcw className="w-4 h-4" />
            </button>

            {/* Add Subscription Button */}
            <button
              onClick={onOpenAddSubscription}
              className="flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl font-[800] text-[11px] tracking-[1px] uppercase bg-white/90 hover:bg-[#6f55ef]/10 text-[#6f55ef] border border-[#6f55ef]/30 shadow-xs hover:shadow-sm transition-all active:scale-95"
            >
              <Plus className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Add Subscription</span>
            </button>

            {/* Run Guardian Audit Master CTA (VeriVision analyze-button) */}
            <button
              onClick={onRunAudit}
              disabled={isRunningAudit}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-[800] text-[11px] tracking-[1.5px] uppercase transition-all shadow-md active:scale-95 ${
                isRunningAudit
                  ? 'bg-[#6f55ef]/20 text-[#6f55ef] cursor-not-allowed border border-[#6f55ef]/30'
                  : 'bg-gradient-to-r from-[#6f55ef] to-[#5136db] hover:from-[#5c3ee6] hover:to-[#4329cb] text-white shadow-[#6f55ef]/35 hover:shadow-[0_10px_28px_rgba(111,85,239,0.45)] hover:-translate-y-0.5'
              }`}
            >
              {isRunningAudit ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Scanning...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Run Guardian Audit</span>
                </>
              )}
            </button>
          </div>

        </div>
      </div>
    </header>
  );
}
