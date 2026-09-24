import React from 'react';
import { 
  AlertTriangle, 
  Check, 
  X, 
  Sliders, 
  Layers, 
  MessageSquareQuote,
  ShieldAlert,
  ArrowRight
} from 'lucide-react';

export default function ApprovalsSection({ 
  pendingSubscriptions = [], 
  onApproveCancel, 
  onKeepSubscription, 
  onNegotiate 
}) {
  if (pendingSubscriptions.length === 0) {
    return (
      <div className="veri-card p-8 text-center my-8">
        <div className="w-12 h-12 bg-[#6f55ef]/10 text-[#6f55ef] rounded-2xl flex items-center justify-center mx-auto mb-3 border border-[#6f55ef]/25 shadow-xs">
          <Check className="w-6 h-6" />
        </div>
        <h3 className="text-base font-[900] tracking-[1px] uppercase text-[#17132d]">No Pending Approvals</h3>
        <p className="text-xs text-[#17132d]/60 max-w-md mx-auto mt-1 font-medium">
          The agent has either kept active services or safely auto-cancelled low-risk waste under your guardrail policy.
        </p>
      </div>
    );
  }

  return (
    <div className="my-8 space-y-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-2.5 h-2.5 rounded-full bg-amber-500 animate-ping" />
          <h2 className="text-base font-[900] tracking-[1.5px] uppercase text-[#17132d]">
            Human-In-The-Loop: Actions Needing Your Judgment
          </h2>
        </div>
        <span className="text-xs font-semibold text-[#17132d]/50 uppercase tracking-wider">
          Personal preference escalation
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {pendingSubscriptions.map((sub) => {
          const isDuplicate = sub.is_duplicate_detected;
          const counterpart = sub.duplicate_counterpart;

          return (
            <div 
              key={sub.id} 
              className="veri-card p-6 border-2 border-amber-400/70 shadow-[0_10px_30px_rgba(245,158,11,0.08)] relative overflow-hidden flex flex-col justify-between"
            >
              <div>
                {/* Header badge */}
                <div className="flex items-center justify-between mb-3.5">
                  <span className="text-[9px] font-[800] tracking-[2px] uppercase px-3 py-1 rounded-md bg-amber-100 text-amber-800 border border-amber-300 flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                    Approval Required
                  </span>
                  <span className="text-xl font-[900] text-[#17132d]">
                    {sub.currency}{sub.amount.toLocaleString()}
                    <span className="text-xs font-[700] text-[#17132d]/50"> / {sub.cadence}</span>
                  </span>
                </div>

                {/* Merchant Name & Inactivity */}
                <h3 className="text-xl font-[900] text-[#17132d] tracking-tight">{sub.merchant}</h3>
                <p className="text-xs text-[#17132d]/60 mt-1 font-medium">
                  Category: <span className="text-[#17132d] font-[700] capitalize">{sub.category.replace('_', ' ')}</span> • 
                  Last used: <span className="text-amber-700 font-[800]">{sub.last_used_days_ago} days ago</span>
                </p>

                {/* Overlap Details */}
                {isDuplicate && counterpart && (
                  <div className="mt-3.5 p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/25">
                    <div className="text-[10px] font-[800] tracking-[1.5px] uppercase text-amber-900 flex items-center gap-1.5 mb-1">
                      <Layers className="w-3.5 h-3.5 text-amber-700" />
                      Competing Service Detected
                    </div>
                    <p className="text-xs text-amber-950 font-medium leading-relaxed">
                      You also pay for <strong className="font-[800] text-[#17132d]">{counterpart}</strong>. 
                      Since you may intentionally keep both, the agent will not cancel without your choice.
                    </p>
                  </div>
                )}

                {/* Agent Reasoning Box */}
                <div className="mt-3.5 p-3.5 rounded-xl bg-white/70 border border-[#6f55ef]/20">
                  <div className="text-[9px] font-[800] tracking-[1.5px] uppercase text-[#6f55ef] mb-1 flex items-center gap-1">
                    <MessageSquareQuote className="w-3.5 h-3.5 text-[#6f55ef]" />
                    Guardian Reasoning
                  </div>
                  <p className="text-xs text-[#17132d]/80 leading-relaxed font-medium">
                    {sub.decision_reason}
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-5 pt-4 border-t border-[#17132d]/10 flex flex-wrap items-center gap-2.5">
                <button
                  onClick={() => onApproveCancel(sub.id)}
                  className="flex-1 min-w-[120px] px-3.5 py-2.5 rounded-xl bg-[#ff3c6e]/10 hover:bg-[#ff3c6e] text-[#ff3c6e] hover:text-white border border-[#ff3c6e]/30 text-[11px] font-[800] tracking-[1px] uppercase transition-all flex items-center justify-center gap-1.5 active:scale-95 shadow-xs"
                >
                  <X className="w-3.5 h-3.5" />
                  Cancel & Save {sub.currency}{sub.amount}
                </button>

                <button
                  onClick={() => onKeepSubscription(sub.id)}
                  className="flex-1 min-w-[100px] px-3.5 py-2.5 rounded-xl bg-[#17132d]/8 hover:bg-[#17132d]/15 text-[#17132d] border border-[#17132d]/15 text-[11px] font-[800] tracking-[1px] uppercase transition-all flex items-center justify-center gap-1.5 active:scale-95 shadow-xs"
                >
                  <Check className="w-3.5 h-3.5 text-emerald-600" />
                  Keep Service
                </button>

                <button
                  onClick={() => onNegotiate(sub)}
                  className="px-3.5 py-2.5 rounded-xl bg-[#6f55ef]/10 hover:bg-[#6f55ef] text-[#6f55ef] hover:text-white border border-[#6f55ef]/30 text-[11px] font-[800] tracking-[1px] uppercase transition-all flex items-center justify-center gap-1.5 active:scale-95 shadow-xs"
                >
                  Negotiate
                </button>
              </div>

            </div>
          );
        })}
      </div>
    </div>
  );
}
