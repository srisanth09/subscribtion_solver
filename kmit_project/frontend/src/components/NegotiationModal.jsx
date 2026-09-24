import React, { useState } from 'react';
import { X, HandCoins, Check, Mail, Sparkles, ArrowRight, ShieldAlert, ArrowDownRight, Ban } from 'lucide-react';

export default function NegotiationModal({ 
  isOpen, 
  onClose, 
  negotiationData, 
  onAcceptOffer, 
  onDeclineOffer,
  onFailOffer,
  onDeclineAndCancel 
}) {
  if (!isOpen || !negotiationData) return null;

  const {
    merchant,
    original_price,
    offered_price,
    discount_percent,
    pitch_letter,
    merchant_reply,
    subscription_id,
    id: offerId,
    currency = '₹'
  } = negotiationData;

  const [activeTab, setActiveTab] = useState('reply'); // 'reply' or 'pitch'
  const [isSubmitting, setIsSubmitting] = useState(false);

  const monthlySaving = roundToTwo(original_price - offered_price);
  const annualSaving = roundToTwo(monthlySaving * 12);

  function roundToTwo(num) {
    return Math.round((num + Number.EPSILON) * 100) / 100;
  }

  const handleAccept = async () => {
    setIsSubmitting(true);
    try {
      await onAcceptOffer(subscription_id, offerId);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDecline = async () => {
    setIsSubmitting(true);
    try {
      if (onDeclineOffer) {
        await onDeclineOffer(subscription_id, offerId);
      } else {
        onClose();
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFail = async () => {
    setIsSubmitting(true);
    try {
      if (onFailOffer) {
        await onFailOffer(subscription_id, offerId);
      } else {
        onClose();
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = async () => {
    setIsSubmitting(true);
    try {
      await onDeclineAndCancel(subscription_id, offerId);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#17132d]/45 backdrop-blur-xl p-4 overflow-y-auto">
      <div className="w-full max-w-2xl bg-white/95 backdrop-blur-2xl border border-white/95 rounded-[24px] shadow-[0_20px_60px_rgba(23,19,45,0.18)] overflow-hidden animate-in fade-in zoom-in-95 duration-200 my-8">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-[#6f55ef]/15 bg-white/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#6f55ef] to-[#5136db] flex items-center justify-center text-white shadow-md shadow-[#6f55ef]/25">
              <HandCoins className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[9px] font-[800] uppercase tracking-[2px] text-[#6f55ef] block">
                Autonomous Rate Negotiation
              </span>
              <h3 className="text-base font-[900] tracking-[0.5px] uppercase text-[#17132d]">
                Negotiate Subscription: {merchant}
              </h3>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 rounded-xl text-[#17132d]/50 hover:text-[#17132d] hover:bg-[#6f55ef]/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5 max-h-[72vh] overflow-y-auto">
          
          {/* Offer Highlight Banner */}
          <div className="p-5 rounded-2xl bg-gradient-to-br from-[#f5f2ff] via-white to-[#ede8ff] border border-[#6f55ef]/25 shadow-[0_8px_24px_rgba(111,85,239,0.06)]">
            <div className="flex items-center justify-between gap-2 mb-3">
              <div className="flex items-center gap-1.5 text-[10px] font-[800] tracking-[1.5px] uppercase text-[#6f55ef]">
                <Sparkles className="w-3.5 h-3.5 animate-pulse" />
                <span>Retention Concession Secured</span>
              </div>
              <span className="text-[10px] bg-emerald-100 text-emerald-800 border border-emerald-300 font-[800] uppercase px-2.5 py-0.5 rounded-full">
                {discount_percent}% Price Cut
              </span>
            </div>

            {/* Price Comparison Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 py-2 border-y border-purple-100/80 my-2">
              <div>
                <span className="text-[10px] font-[800] uppercase tracking-[1px] text-[#17132d]/50 block">Original Price</span>
                <span className="text-base font-[800] text-[#17132d]/60 line-through">
                  {currency}{original_price.toLocaleString()}<span className="text-[10px] font-normal">/mo</span>
                </span>
              </div>
              <div>
                <span className="text-[10px] font-[800] uppercase tracking-[1px] text-[#6f55ef] block">New Price</span>
                <span className="text-xl font-[900] text-[#17132d]">
                  {currency}{offered_price.toLocaleString()}<span className="text-[10px] font-normal text-[#6f55ef]">/mo</span>
                </span>
              </div>
              <div>
                <span className="text-[10px] font-[800] uppercase tracking-[1px] text-emerald-700 block">Monthly Savings</span>
                <span className="text-base font-[900] text-emerald-600">
                  +{currency}{monthlySaving.toLocaleString()}
                </span>
              </div>
              <div>
                <span className="text-[10px] font-[800] uppercase tracking-[1px] text-[#5136db] block">Annual Savings</span>
                <span className="text-base font-[900] text-[#5136db]">
                  +{currency}{annualSaving.toLocaleString()}
                </span>
              </div>
            </div>

            <p className="text-xs text-[#17132d]/70 mt-2 font-medium">
              Accepting this retention concession keeps your active membership while lowering your recurring spend by {discount_percent}%.
            </p>
          </div>

          {/* Toggle Tabs: Pitch vs Merchant Reply */}
          <div className="flex border-b border-[#6f55ef]/15 gap-4">
            <button
              onClick={() => setActiveTab('reply')}
              className={`pb-2.5 text-[11px] font-[800] tracking-[1.5px] uppercase border-b-2 transition-all flex items-center gap-1.5 ${
                activeTab === 'reply'
                  ? 'border-[#6f55ef] text-[#6f55ef]'
                  : 'border-transparent text-[#17132d]/50 hover:text-[#6f55ef]'
              }`}
            >
              <Mail className="w-3.5 h-3.5" />
              <span>Merchant Counter-Offer Letter</span>
            </button>
            <button
              onClick={() => setActiveTab('pitch')}
              className={`pb-2.5 text-[11px] font-[800] tracking-[1.5px] uppercase border-b-2 transition-all flex items-center gap-1.5 ${
                activeTab === 'pitch'
                  ? 'border-[#6f55ef] text-[#6f55ef]'
                  : 'border-transparent text-[#17132d]/50 hover:text-[#6f55ef]'
              }`}
            >
              <ArrowDownRight className="w-3.5 h-3.5" />
              <span>AI Outgoing Pitch Letter</span>
            </button>
          </div>

          {/* Letter Body Display */}
          <div className="p-5 rounded-2xl bg-[#17132d] border border-[#6f55ef]/20 font-mono text-xs text-[#ede8ff] whitespace-pre-wrap leading-relaxed shadow-xs">
            {activeTab === 'reply' ? merchant_reply : pitch_letter}
          </div>

        </div>

        {/* Footer CTAs */}
        <div className="px-6 py-4 bg-white/80 border-t border-[#6f55ef]/15 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <button
              onClick={handleDecline}
              disabled={isSubmitting}
              className="px-3.5 py-2.5 rounded-xl text-[11px] font-[800] tracking-[1px] uppercase text-[#17132d]/70 hover:text-[#17132d] hover:bg-[#17132d]/5 border border-[#17132d]/15 transition-all active:scale-95 disabled:opacity-50"
              title="Decline the discount offer and keep subscription at original price"
            >
              Decline Offer
            </button>

            <button
              onClick={handleFail}
              disabled={isSubmitting}
              className="px-3.5 py-2.5 rounded-xl text-[11px] font-[800] tracking-[1px] uppercase text-amber-700 hover:text-amber-800 hover:bg-amber-50 border border-amber-300 transition-all active:scale-95 disabled:opacity-50"
              title="Simulate negotiation failure (no discount offered, maintain original price)"
            >
              Simulate Failure
            </button>

            <button
              onClick={handleCancel}
              disabled={isSubmitting}
              className="px-3.5 py-2.5 rounded-xl text-[11px] font-[800] tracking-[1px] uppercase text-[#ff3c6e] hover:text-white hover:bg-[#ff3c6e] border border-[#ff3c6e]/30 transition-all active:scale-95 disabled:opacity-50"
              title="Decline offer and cancel subscription altogether"
            >
              Decline & Cancel
            </button>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2.5 rounded-xl text-[11px] font-[800] tracking-[1px] uppercase text-[#17132d]/60 hover:text-[#17132d] hover:bg-[#6f55ef]/10 transition-colors"
            >
              Close
            </button>

            <button
              onClick={handleAccept}
              disabled={isSubmitting}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#6f55ef] to-[#5136db] hover:from-[#5c3ee6] hover:to-[#4329cb] text-white text-[11px] font-[800] tracking-[1px] uppercase transition-all flex items-center gap-2 shadow-md shadow-[#6f55ef]/30 hover:shadow-[#6f55ef]/45 active:scale-95 disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Applying Discount...</span>
                </>
              ) : (
                <>
                  <Check className="w-4 h-4" />
                  <span>Accept Offer (Save {currency}{monthlySaving}/mo)</span>
                </>
              )}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
