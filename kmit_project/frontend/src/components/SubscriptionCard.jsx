import React from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  TrendingUp, 
  Package, 
  Clock, 
  CheckCircle2, 
  AlertCircle, 
  XCircle,
  SlidersHorizontal,
  ChevronRight,
  HandCoins
} from 'lucide-react';

export default function SubscriptionCard({ 
  subscription, 
  onPerformAction, 
  onNegotiate 
}) {
  const {
    id,
    merchant,
    amount,
    currency,
    cadence,
    category,
    last_used_days_ago,
    waste_score,
    confidence_score,
    status,
    guardrail_status,
    decision,
    decision_reason,
    price_hike_detected,
    hike_percentage,
    old_price,
    is_duplicate_detected,
    is_bundled,
    bundle_provider,
    bundle_description,
    trial_converted
  } = subscription;

  // Waste Score Color
  const getWasteBadge = (score) => {
    if (score >= 70) return { bg: 'bg-[#ff3c6e]/12 text-[#ff3c6e] border-[#ff3c6e]/30', label: 'High Waste' };
    if (score >= 40) return { bg: 'bg-amber-100 text-amber-800 border-amber-300', label: 'Moderate' };
    return { bg: 'bg-[#6f55ef]/10 text-[#6f55ef] border-[#6f55ef]/25', label: 'Low Waste' };
  };

  const wasteInfo = getWasteBadge(waste_score);

  // Status Badge
  const renderStatusBadge = () => {
    if (status === 'cancelled') {
      return (
        <span className="px-2.5 py-1 rounded-md text-[9px] font-[800] tracking-[1.5px] uppercase bg-[#ff3c6e]/12 text-[#ff3c6e] border border-[#ff3c6e]/30 flex items-center gap-1">
          <XCircle className="w-3.5 h-3.5" />
          Auto-Cancelled
        </span>
      );
    }
    if (status === 'protected' || guardrail_status === 'BLOCKED_PROTECTED') {
      return (
        <span className="px-2.5 py-1 rounded-md text-[9px] font-[800] tracking-[1.5px] uppercase bg-[#6f55ef]/15 text-[#6f55ef] border border-[#6f55ef]/30 flex items-center gap-1">
          <ShieldAlert className="w-3.5 h-3.5 text-[#6f55ef]" />
          Protected Category
        </span>
      );
    }
    if (status === 'pending_approval') {
      return (
        <span className="px-2.5 py-1 rounded-md text-[9px] font-[800] tracking-[1.5px] uppercase bg-amber-100 text-amber-800 border border-amber-300 flex items-center gap-1">
          <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
          Needs Approval
        </span>
      );
    }
    if (status === 'negotiating') {
      return (
        <span className="px-2.5 py-1 rounded-md text-[9px] font-[800] tracking-[1.5px] uppercase bg-[#5136db]/10 text-[#5136db] border border-[#5136db]/25 flex items-center gap-1">
          <HandCoins className="w-3.5 h-3.5 text-[#5136db]" />
          Negotiation Active
        </span>
      );
    }
    if (status === 'negotiated') {
      return (
        <span className="px-2.5 py-1 rounded-md text-[9px] font-[800] tracking-[1.5px] uppercase bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center gap-1">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
          Negotiated Discount
        </span>
      );
    }
    return (
      <span className="px-2.5 py-1 rounded-md text-[9px] font-[800] tracking-[1.5px] uppercase bg-[#6f55ef]/10 text-[#6f55ef] border border-[#6f55ef]/20 flex items-center gap-1">
        <CheckCircle2 className="w-3.5 h-3.5 text-[#6f55ef]" />
        Active & Verified
      </span>
    );
  };

  return (
    <div className={`veri-card p-6 flex flex-col justify-between group ${
      status === 'cancelled' ? 'opacity-80 bg-white/50' :
      status === 'pending_approval' ? 'border-amber-400/50 bg-amber-50/20 shadow-[0_10px_30px_rgba(245,158,11,0.06)]' :
      status === 'protected' ? 'border-[#6f55ef]/25' : ''
    }`}>
      <div>
        {/* Header: Badges & Price */}
        <div className="flex items-start justify-between gap-2 mb-3.5">
          <div className="flex flex-wrap gap-1.5">
            {renderStatusBadge()}
            <span className={`px-2.5 py-1 rounded-md text-[9px] font-[800] tracking-[1.5px] uppercase border ${wasteInfo.bg}`}>
              Waste: {waste_score}/100
            </span>
          </div>

          <div className="text-right">
            <div className="text-xl font-[900] text-[#17132d]">
              {currency}{amount.toLocaleString()}
            </div>
            <div className="text-[10px] font-[800] tracking-[1px] uppercase text-[#17132d]/40">/{cadence}</div>
          </div>
        </div>

        {/* Merchant Title & Category */}
        <div className="mb-2">
          <h4 className="text-lg font-[900] text-[#17132d] tracking-tight">{merchant}</h4>
          <p className="text-xs text-[#17132d]/60 flex items-center gap-1.5 mt-0.5 font-medium">
            <span className="capitalize text-[#17132d] font-[700]">{category.replace('_', ' ')}</span>
            <span>•</span>
            <span className={last_used_days_ago <= 7 ? 'text-[#6f55ef] font-[800]' : 'text-[#17132d]/60'}>
              Used {last_used_days_ago} days ago
            </span>
          </p>
        </div>

        {/* Feature Badges: Price Hike, Free Trial, Bundle */}
        <div className="space-y-2 my-3.5">
          {price_hike_detected && (
            <div className="px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-950 text-xs flex items-center gap-2 font-[600]">
              <TrendingUp className="w-3.5 h-3.5 text-amber-600 shrink-0" />
              <span>
                <strong className="font-[800]">+{hike_percentage}% Price Hike</strong> ({currency}{old_price} → {currency}{amount})
              </span>
            </div>
          )}

          {trial_converted && (
            <div className="px-3 py-1.5 rounded-xl bg-[#6f55ef]/10 border border-[#6f55ef]/25 text-[#17132d] text-xs flex items-center gap-2 font-[600]">
              <Clock className="w-3.5 h-3.5 text-[#6f55ef] shrink-0" />
              <span>Converted from Free Trial to Paid</span>
            </div>
          )}

          {is_bundled && (
            <div className="px-3 py-1.5 rounded-xl bg-[#68c7ff]/15 border border-[#68c7ff]/30 text-[#17132d] text-xs flex items-center gap-2 font-[600]">
              <Package className="w-3.5 h-3.5 text-[#5136db] shrink-0" />
              <span>Covered by bundle: <strong className="font-[800]">{bundle_provider}</strong></span>
            </div>
          )}
        </div>

        {/* AI Agent Reasoning */}
        <div className="p-3.5 rounded-xl bg-white/70 border border-[#6f55ef]/15 my-2.5">
          <div className="text-[9px] uppercase font-[800] text-[#6f55ef] tracking-[1.5px] mb-1 flex items-center justify-between">
            <span>Agent Rationale</span>
            <span className="font-[800] text-[#17132d]/60">Conf: {(confidence_score * 100).toFixed(0)}%</span>
          </div>
          <p className="text-xs text-[#17132d]/80 leading-relaxed font-medium">
            {decision_reason}
          </p>
        </div>
      </div>

      {/* Action Footer */}
      <div className="mt-4 pt-3.5 border-t border-[#17132d]/10 flex items-center justify-between gap-2">
        {status === 'cancelled' ? (
          <div className="text-xs text-[#6f55ef] font-[800] tracking-[0.5px] uppercase flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-[#6f55ef]" />
            Recurring fee eliminated
          </div>
        ) : status === 'protected' ? (
          <div className="text-xs text-[#5136db] font-[800] tracking-[0.5px] uppercase flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-[#5136db]" />
            Safety Policy Locked
          </div>
        ) : status === 'negotiated' ? (
          <div className="flex items-center justify-between gap-2 w-full">
            <span className="text-xs text-emerald-700 font-[800] tracking-[0.5px] uppercase flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              Retained with Discount
            </span>
            <button
              onClick={() => onNegotiate(subscription)}
              className="px-3 py-1.5 rounded-xl bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 text-[10px] font-[800] uppercase tracking-[1px] transition-all"
            >
              View Offer
            </button>
          </div>
        ) : status === 'negotiating' ? (
          <div className="flex items-center gap-2 w-full">
            <button
              onClick={() => onNegotiate(subscription)}
              className="flex-1 px-3 py-2 rounded-xl bg-gradient-to-r from-[#6f55ef] to-[#5136db] text-white text-[11px] font-[800] tracking-[1px] uppercase transition-all shadow-sm shadow-[#6f55ef]/25 hover:shadow-[#6f55ef]/40 active:scale-95 animate-pulse flex items-center justify-center gap-1.5"
            >
              <HandCoins className="w-3.5 h-3.5" />
              Review Pending Offer
            </button>
            <button
              onClick={() => onPerformAction(id, 'approve_cancel')}
              className="px-3 py-2 rounded-xl bg-[#ff3c6e]/10 hover:bg-[#ff3c6e] text-[#ff3c6e] hover:text-white border border-[#ff3c6e]/30 text-[11px] font-[800] tracking-[1px] uppercase transition-all"
            >
              Cancel
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2 w-full">
            {status !== 'kept' && (
              <button
                onClick={() => onPerformAction(id, 'approve_cancel')}
                className="flex-1 px-3 py-2 rounded-xl bg-[#ff3c6e]/10 hover:bg-[#ff3c6e] text-[#ff3c6e] hover:text-white border border-[#ff3c6e]/30 text-[11px] font-[800] tracking-[1px] uppercase transition-all shadow-xs active:scale-95"
              >
                Cancel
              </button>
            )}

            <button
              onClick={() => onNegotiate(subscription)}
              className="flex-1 px-3 py-2 rounded-xl bg-gradient-to-r from-[#6f55ef] to-[#5136db] hover:from-[#5c3ee6] hover:to-[#4329cb] text-white text-[11px] font-[800] tracking-[1px] uppercase transition-all shadow-sm shadow-[#6f55ef]/25 hover:shadow-[#6f55ef]/40 active:scale-95"
            >
              Negotiate
            </button>

            {status !== 'kept' && (
              <button
                onClick={() => onPerformAction(id, 'keep')}
                className="px-3 py-2 rounded-xl bg-[#17132d]/8 hover:bg-[#17132d]/15 text-[#17132d] border border-[#17132d]/15 text-[11px] font-[800] tracking-[1px] uppercase transition-all shadow-xs active:scale-95"
              >
                Keep
              </button>
            )}
          </div>
        )}
      </div>

    </div>
  );
}
