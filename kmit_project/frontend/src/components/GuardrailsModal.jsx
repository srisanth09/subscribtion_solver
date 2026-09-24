import React, { useState, useEffect } from 'react';
import { X, ShieldCheck, Sliders, AlertCircle, Save, Check, HandCoins } from 'lucide-react';

const AVAILABLE_CATEGORIES = [
  { id: 'insurance', label: 'Insurance Policies (Life, Health, Auto)' },
  { id: 'loan_payment', label: 'Loan EMIs & Debt Repayments' },
  { id: 'healthcare', label: 'Medical & Healthcare Services' },
  { id: 'utility', label: 'Utilities (Electricity, Water, Internet)' },
  { id: 'education', label: 'Tuition & Education Programs' },
  { id: 'tax', label: 'Tax & Compliance Filing Fees' }
];

export default function GuardrailsModal({ isOpen, onClose, guardrails, onSave }) {
  if (!isOpen) return null;

  const [limit, setLimit] = useState(guardrails?.auto_action_limit || 2000);
  const [protectedCats, setProtectedCats] = useState(guardrails?.protected_categories || []);
  const [confidence, setConfidence] = useState(guardrails?.min_confidence_threshold || 0.85);
  const [requireDuplicateApproval, setRequireDuplicateApproval] = useState(
    guardrails?.require_approval_for_duplicates ?? true
  );
  const [negotiationMode, setNegotiationMode] = useState(
    guardrails?.negotiation_mode ?? false
  );
  const [isSaved, setIsSaved] = useState(false);

  useEffect(() => {
    if (guardrails) {
      setLimit(guardrails.auto_action_limit);
      setProtectedCats(guardrails.protected_categories || []);
      setConfidence(guardrails.min_confidence_threshold || 0.85);
      setRequireDuplicateApproval(guardrails.require_approval_for_duplicates ?? true);
      setNegotiationMode(guardrails.negotiation_mode ?? false);
    }
  }, [guardrails]);

  const toggleCategory = (catId) => {
    if (protectedCats.includes(catId)) {
      setProtectedCats(protectedCats.filter(c => c !== catId));
    } else {
      setProtectedCats([...protectedCats, catId]);
    }
  };

  const handleSave = () => {
    onSave({
      auto_action_limit: parseFloat(limit),
      protected_categories: protectedCats,
      min_confidence_threshold: parseFloat(confidence),
      require_approval_for_duplicates: requireDuplicateApproval,
      negotiation_mode: negotiationMode
    });
    setIsSaved(true);
    setTimeout(() => {
      setIsSaved(false);
      onClose();
    }, 800);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#17132d]/40 backdrop-blur-xl p-4">
      <div className="w-full max-w-xl bg-white/95 backdrop-blur-2xl border border-white/95 rounded-[24px] shadow-[0_20px_60px_rgba(23,19,45,0.15)] overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-[#6f55ef]/15 bg-white/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#6f55ef]/12 text-[#6f55ef] flex items-center justify-center border border-[#6f55ef]/25 shadow-xs">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-[900] tracking-[1px] uppercase text-[#17132d]">Agent Safety Guardrails</h3>
              <p className="text-xs text-[#17132d]/60 font-medium">Hard boundaries governing autonomous decision execution</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 rounded-xl text-[#17132d]/50 hover:text-[#17132d] hover:bg-[#6f55ef]/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5 max-h-[75vh] overflow-y-auto">
          
          {/* Setting 1: Autonomous Spending Ceiling */}
          <div className="p-4 rounded-2xl bg-[#6f55ef]/5 border border-[#6f55ef]/15">
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-[800] tracking-[1px] uppercase text-[#17132d] flex items-center gap-1.5">
                <Sliders className="w-4 h-4 text-[#6f55ef]" />
                Autonomous Action Ceiling
              </label>
              <span className="text-base font-[900] text-[#6f55ef]">
                ₹{Number(limit).toLocaleString()}
              </span>
            </div>
            <p className="text-xs text-[#17132d]/65 mb-3 leading-relaxed font-medium">
              The agent will <strong>never</strong> auto-cancel any subscription above this amount without prior human authorization.
            </p>
            <input 
              type="range"
              min="200"
              max="10000"
              step="100"
              value={limit}
              onChange={(e) => setLimit(e.target.value)}
              className="w-full accent-[#6f55ef] bg-slate-200 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-[#17132d]/50 mt-1 font-[700] uppercase tracking-wider">
              <span>₹200 (Conservative)</span>
              <span>₹5,000</span>
              <span>₹10,000 (Aggressive)</span>
            </div>
          </div>

          {/* Setting 2: Protected Categories */}
          <div>
            <label className="text-xs font-[800] tracking-[1px] uppercase text-[#17132d] block mb-1">
              Strictly Protected Categories (Zero Autonomy)
            </label>
            <p className="text-xs text-[#17132d]/65 mb-3 leading-relaxed font-medium">
              Even if a service shows 300+ days of inactivity, the agent is <strong>strictly blocked</strong> from touching it.
            </p>

            <div className="grid grid-cols-1 gap-2">
              {AVAILABLE_CATEGORIES.map((cat) => {
                const isChecked = protectedCats.includes(cat.id);
                return (
                  <div
                    key={cat.id}
                    onClick={() => toggleCategory(cat.id)}
                    className={`flex items-center justify-between p-3 rounded-xl border cursor-pointer transition-all ${
                      isChecked
                        ? 'bg-[#6f55ef]/10 border-[#6f55ef]/30 text-[#17132d] font-[700] shadow-xs'
                        : 'bg-white/70 border-[#17132d]/15 text-[#17132d]/70 hover:border-[#6f55ef]/30 hover:bg-[#6f55ef]/5'
                    }`}
                  >
                    <span className="text-xs">{cat.label}</span>
                    <div className={`w-4 h-4 rounded flex items-center justify-center border transition-colors ${
                      isChecked ? 'bg-[#6f55ef] border-[#6f55ef] text-white' : 'border-slate-300'
                    }`}>
                      {isChecked && <Check className="w-3 h-3 stroke-[3]" />}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Setting 3: Decision Confidence Threshold */}
          <div className="p-4 rounded-2xl bg-[#6f55ef]/5 border border-[#6f55ef]/15">
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-[800] tracking-[1px] uppercase text-[#17132d]">
                Decision Certainty Threshold
              </label>
              <span className="text-sm font-[900] text-[#6f55ef]">
                {(confidence * 100).toFixed(0)}%
              </span>
            </div>
            <p className="text-xs text-[#17132d]/65 mb-3 leading-relaxed font-medium">
              Recommendations below this certainty score are escalated to human judgment.
            </p>
            <input 
              type="range"
              min="0.60"
              max="0.95"
              step="0.05"
              value={confidence}
              onChange={(e) => setConfidence(e.target.value)}
              className="w-full accent-[#6f55ef] bg-slate-200 rounded-lg cursor-pointer"
            />
          </div>

          {/* Setting 4: Negotiation Mode (Idea 2) */}
          <div className="p-4 rounded-2xl bg-[#6f55ef]/5 border border-[#6f55ef]/15">
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-[800] tracking-[1px] uppercase text-[#17132d] flex items-center gap-1.5">
                <HandCoins className="w-4 h-4 text-[#6f55ef]" />
                Negotiation Mode (Contact Merchants First)
              </label>
              <input
                type="checkbox"
                checked={negotiationMode}
                onChange={(e) => setNegotiationMode(e.target.checked)}
                className="w-4 h-4 accent-[#6f55ef] cursor-pointer"
              />
            </div>
            <p className="text-xs text-[#17132d]/65 leading-relaxed font-medium">
              When active, the agent contacts merchants with a generated downgrade or discount request before cancelling an eligible subscription, saving money without losing service.
            </p>
          </div>

        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 bg-white/70 border-t border-[#6f55ef]/15 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-[11px] font-[800] tracking-[1px] uppercase text-[#17132d]/60 hover:text-[#17132d] hover:bg-[#6f55ef]/10 transition-colors"
          >
            Cancel
          </button>

          <button
            onClick={handleSave}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#6f55ef] to-[#5136db] hover:from-[#5c3ee6] hover:to-[#4329cb] text-white text-[11px] font-[800] tracking-[1px] uppercase transition-all flex items-center gap-2 shadow-md shadow-[#6f55ef]/25 hover:shadow-[#6f55ef]/40 active:scale-95"
          >
            {isSaved ? (
              <>
                <Check className="w-4 h-4" />
                <span>Saved!</span>
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                <span>Save Guardrails Policy</span>
              </>
            )}
          </button>
        </div>

      </div>
    </div>
  );
}
