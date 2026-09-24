import React from 'react';
import { 
  TrendingDown, 
  Sparkles, 
  AlertOctagon, 
  CheckCircle, 
  ShieldAlert,
  ArrowUpRight
} from 'lucide-react';

export default function SavingsSummaryCards({ metrics, onOpenApprovals }) {
  const currency = metrics?.currency || '₹';
  const monthlySavings = metrics?.potential_monthly_savings || 0;
  const annualSavings = metrics?.potential_annual_savings || 0;
  const autoCancelled = metrics?.auto_cancelled_count || 0;
  const pendingApproval = metrics?.pending_approval_count || 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
      
      {/* Card 1: Monthly Waste Stopped */}
      <div className="veri-card p-6 relative overflow-hidden group">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-[800] tracking-[2px] uppercase text-[#6f55ef]">
            Monthly Waste Stopped
          </span>
          <div className="w-10 h-10 rounded-xl bg-[#6f55ef]/10 flex items-center justify-center text-[#6f55ef] border border-[#6f55ef]/25 shadow-xs group-hover:scale-105 transition-transform">
            <TrendingDown className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-4">
          <div className="text-3xl font-[900] text-[#17132d] tracking-tight">
            {currency}{monthlySavings.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
            <span className="text-xs font-[700] text-[#17132d]/50"> /mo</span>
          </div>
          <p className="text-xs text-[#17132d]/60 mt-1.5 flex items-center gap-1.5 font-medium">
            <span className="text-[#6f55ef] font-[800] bg-[#6f55ef]/10 px-2 py-0.5 rounded-full border border-[#6f55ef]/20 text-[10px] tracking-[0.5px]">
              Active Forensics
            </span>
            <span>realized savings</span>
          </p>
        </div>
        <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-[#6f55ef]/10 rounded-full blur-2xl pointer-events-none" />
      </div>

      {/* Card 2: Annual Run-Rate */}
      <div className="veri-card p-6 relative overflow-hidden group">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-[800] tracking-[2px] uppercase text-[#5136db]">
            Projected Run-Rate
          </span>
          <div className="w-10 h-10 rounded-xl bg-[#5136db]/10 flex items-center justify-center text-[#5136db] border border-[#5136db]/25 shadow-xs group-hover:scale-105 transition-transform">
            <Sparkles className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-4">
          <div className="text-3xl font-[900] text-[#17132d] tracking-tight">
            {currency}{annualSavings.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
            <span className="text-xs font-[700] text-[#17132d]/50"> /yr</span>
          </div>
          <p className="text-xs text-[#17132d]/60 mt-1.5 font-medium">
            Annualized capital leak prevented
          </p>
        </div>
        <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-[#5136db]/10 rounded-full blur-2xl pointer-events-none" />
      </div>

      {/* Card 3: Autonomous Actions */}
      <div className="veri-card p-6 relative overflow-hidden group">
        <div className="flex items-center justify-between">
          <span className="text-[10px] font-[800] tracking-[2px] uppercase text-[#17132d]/70">
            Autonomous Actions
          </span>
          <div className="w-10 h-10 rounded-xl bg-[#6f55ef]/10 flex items-center justify-center text-[#6f55ef] border border-[#6f55ef]/20 shadow-xs group-hover:scale-105 transition-transform">
            <CheckCircle className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-4">
          <div className="text-3xl font-[900] text-[#17132d] tracking-tight">
            {autoCancelled}
            <span className="text-xs font-[700] text-[#17132d]/50"> auto-cancelled</span>
          </div>
          <p className="text-xs text-[#17132d]/60 mt-1.5 font-medium">
            High-waste recurring mandates revoked
          </p>
        </div>
        <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-[#6f55ef]/10 rounded-full blur-2xl pointer-events-none" />
      </div>

      {/* Card 4: Human Approvals Pending */}
      <div 
        onClick={onOpenApprovals}
        className={`veri-card p-6 relative overflow-hidden cursor-pointer group ${
          pendingApproval > 0 
            ? 'border-amber-400/60 bg-gradient-to-br from-white/90 via-amber-50/30 to-white/90 shadow-[0_10px_30px_rgba(245,158,11,0.08)]' 
            : ''
        }`}
      >
        <div className="flex items-center justify-between">
          <span className={`text-[10px] font-[800] tracking-[2px] uppercase ${
            pendingApproval > 0 ? 'text-amber-700' : 'text-[#17132d]/70'
          }`}>
            Pending Approvals
          </span>
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center border shadow-xs group-hover:scale-105 transition-transform ${
            pendingApproval > 0 
              ? 'bg-amber-100 text-amber-700 border-amber-300' 
              : 'bg-white text-[#17132d]/60 border-[#17132d]/15'
          }`}>
            <AlertOctagon className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-4 flex items-baseline justify-between">
          <div>
            <div className="text-3xl font-[900] text-[#17132d] tracking-tight">
              {pendingApproval}
              <span className="text-xs font-[700] text-[#17132d]/50"> decisions</span>
            </div>
            <p className="text-xs text-[#17132d]/60 mt-1.5 font-medium">
              Ambiguity or guardrail threshold gates
            </p>
          </div>
          {pendingApproval > 0 && (
            <span className="text-xs text-amber-700 flex items-center gap-0.5 hover:underline font-[800]">
              Review <ArrowUpRight className="w-3.5 h-3.5" />
            </span>
          )}
        </div>
        <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-amber-500/10 rounded-full blur-2xl pointer-events-none" />
      </div>

    </div>
  );
}
