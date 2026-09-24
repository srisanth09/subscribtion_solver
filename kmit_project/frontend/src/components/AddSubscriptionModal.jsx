import React, { useState } from 'react';
import { 
  PlusCircle, 
  X, 
  Layers, 
  CheckCircle2, 
  AlertCircle, 
  Calendar, 
  CreditCard, 
  TrendingUp, 
  Sparkles,
  ShieldCheck,
  Copy
} from 'lucide-react';

const CATEGORY_OPTIONS = [
  { value: 'video_streaming', label: 'Video Streaming' },
  { value: 'music_streaming', label: 'Music Streaming' },
  { value: 'fitness', label: 'Fitness & Gym' },
  { value: 'productivity', label: 'Productivity & Cloud' },
  { value: 'developer_tools', label: 'Developer Tools' },
  { value: 'mental_health', label: 'Mental Health & Wellness' },
  { value: 'insurance', label: 'Insurance Policy (Protected)' },
  { value: 'loan_payment', label: 'Loan Payment / EMI (Protected)' },
  { value: 'utility', label: 'Utility / Bills (Protected)' },
  { value: 'education', label: 'Education / Learning (Protected)' },
  { value: 'gaming', label: 'Gaming & Entertainment' },
  { value: 'general', label: 'General Recurring Charge' }
];

const CADENCE_OPTIONS = [
  { value: 'monthly', label: 'Monthly' },
  { value: 'yearly', label: 'Yearly' },
  { value: 'quarterly', label: 'Quarterly' },
  { value: 'weekly', label: 'Weekly' }
];

export default function AddSubscriptionModal({ isOpen, onClose, onAddSuccess }) {
  const [formData, setFormData] = useState({
    merchant: '',
    amount: '',
    currency: '₹',
    category: 'video_streaming',
    cadence: 'monthly',
    last_used_days_ago: 0,
    previous_price: '',
    transaction_date: new Date().toISOString().slice(0, 10),
    is_duplicate: false,
    duplicate_counterpart: '',
    is_bundled: false,
    bundle_provider: '',
    trial_converted: false
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  if (!isOpen) return null;

  const validate = () => {
    const errs = {};
    if (!formData.merchant.trim()) {
      errs.merchant = "Merchant / Service name cannot be empty";
    }

    const numAmount = parseFloat(formData.amount);
    if (isNaN(numAmount) || numAmount <= 0) {
      errs.amount = "Amount must be greater than 0";
    }

    if (!formData.category) {
      errs.category = "Category is required";
    }

    if (!formData.cadence) {
      errs.cadence = "Billing frequency is required";
    }

    const days = parseInt(formData.last_used_days_ago, 10);
    if (isNaN(days) || days < 0) {
      errs.last_used_days_ago = "Days inactive must be >= 0";
    }

    if (formData.previous_price) {
      const prev = parseFloat(formData.previous_price);
      if (isNaN(prev) || prev < 0) {
        errs.previous_price = "Previous price must be a valid positive number if entered";
      }
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSuccessMessage('');

    if (!validate()) return;

    setIsSubmitting(true);
    try {
      const payload = {
        merchant: formData.merchant.trim(),
        amount: parseFloat(formData.amount),
        currency: formData.currency,
        category: formData.category,
        cadence: formData.cadence,
        last_used_days_ago: parseInt(formData.last_used_days_ago, 10) || 0,
        is_duplicate: formData.is_duplicate,
        duplicate_counterpart: formData.is_duplicate ? formData.duplicate_counterpart.trim() : null,
        is_bundled: formData.is_bundled,
        bundle_provider: formData.is_bundled ? formData.bundle_provider.trim() : null,
        trial_converted: formData.trial_converted,
        previous_price: formData.previous_price ? parseFloat(formData.previous_price) : null,
        transaction_date: formData.transaction_date || new Date().toISOString().slice(0, 10)
      };

      await onAddSuccess(payload);
      setSuccessMessage("Subscription added successfully! Analyzing through Guardian AI...");

      setTimeout(() => {
        setIsSubmitting(false);
        setSuccessMessage('');
        onClose();
      }, 1200);
    } catch (err) {
      console.error("Add subscription failed:", err);
      setErrors({ server: err.response?.data?.detail || err.message || "Failed to add subscription" });
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#17132d]/40 backdrop-blur-xl p-4 overflow-y-auto">
      <div className="w-full max-w-2xl bg-white/95 backdrop-blur-2xl border border-white/95 rounded-[24px] shadow-[0_20px_60px_rgba(23,19,45,0.15)] overflow-hidden animate-in fade-in zoom-in-95 duration-200 my-8">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-[#6f55ef]/15 bg-white/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#6f55ef] to-[#5136db] flex items-center justify-center text-white shadow-md shadow-[#6f55ef]/25">
              <PlusCircle className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[9px] font-[800] uppercase tracking-[2px] text-[#6f55ef] block">
                Manual Telemetry Ingestion
              </span>
              <h3 className="text-base font-[900] tracking-[0.5px] uppercase text-[#17132d]">
                Add New Subscription
              </h3>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-[#17132d]/40 hover:text-[#17132d] hover:bg-purple-100/50 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {successMessage && (
            <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>{successMessage}</span>
            </div>
          )}

          {errors.server && (
            <div className="p-3.5 rounded-xl bg-[#ff3c6e]/10 border border-[#ff3c6e]/30 text-[#ff3c6e] text-xs font-semibold flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-[#ff3c6e] shrink-0" />
              <span>{errors.server}</span>
            </div>
          )}

          {/* Row 1: Merchant Name & Amount */}
          <div className="grid grid-cols-1 sm:grid-cols-12 gap-4">
            <div className="sm:col-span-7">
              <label className="block text-[11px] font-[800] uppercase tracking-[1px] text-[#17132d] mb-1.5">
                Merchant / Service Name <span className="text-[#ff3c6e]">*</span>
              </label>
              <input
                type="text"
                placeholder="e.g. Netflix, StreamFlix, IronFit Gym"
                value={formData.merchant}
                onChange={(e) => {
                  setFormData({ ...formData, merchant: e.target.value });
                  if (errors.merchant) setErrors({ ...errors, merchant: null });
                }}
                className={`w-full px-3.5 py-2.5 bg-white/90 border rounded-xl text-xs text-[#17132d] placeholder-slate-400 font-medium focus:outline-none focus:ring-2 transition-all ${
                  errors.merchant ? 'border-[#ff3c6e] focus:ring-[#ff3c6e]/20' : 'border-purple-200/80 focus:border-[#6f55ef] focus:ring-[#6f55ef]/20'
                }`}
              />
              {errors.merchant && (
                <p className="text-[10px] text-[#ff3c6e] mt-1 font-semibold">{errors.merchant}</p>
              )}
            </div>

            <div className="sm:col-span-5">
              <label className="block text-[11px] font-[800] uppercase tracking-[1px] text-[#17132d] mb-1.5">
                Amount & Currency <span className="text-[#ff3c6e]">*</span>
              </label>
              <div className="flex items-center gap-2">
                <select
                  value={formData.currency}
                  onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                  className="w-16 px-2.5 py-2.5 bg-white/90 border border-purple-200/80 rounded-xl text-xs font-bold text-[#17132d] focus:outline-none focus:border-[#6f55ef]"
                >
                  <option value="₹">₹</option>
                  <option value="$">$</option>
                  <option value="€">€</option>
                  <option value="£">£</option>
                </select>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="e.g. 649"
                  value={formData.amount}
                  onChange={(e) => {
                    setFormData({ ...formData, amount: e.target.value });
                    if (errors.amount) setErrors({ ...errors, amount: null });
                  }}
                  className={`flex-1 px-3.5 py-2.5 bg-white/90 border rounded-xl text-xs text-[#17132d] font-bold focus:outline-none focus:ring-2 transition-all ${
                    errors.amount ? 'border-[#ff3c6e] focus:ring-[#ff3c6e]/20' : 'border-purple-200/80 focus:border-[#6f55ef] focus:ring-[#6f55ef]/20'
                  }`}
                />
              </div>
              {errors.amount && (
                <p className="text-[10px] text-[#ff3c6e] mt-1 font-semibold">{errors.amount}</p>
              )}
            </div>
          </div>

          {/* Row 2: Category & Cadence */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-[11px] font-[800] uppercase tracking-[1px] text-[#17132d] mb-1.5">
                Category <span className="text-[#ff3c6e]">*</span>
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-3.5 py-2.5 bg-white/90 border border-purple-200/80 rounded-xl text-xs text-[#17132d] font-medium focus:outline-none focus:border-[#6f55ef]"
              >
                {CATEGORY_OPTIONS.map((c) => (
                  <option key={c.value} value={c.value}>{c.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-[800] uppercase tracking-[1px] text-[#17132d] mb-1.5">
                Billing Cadence / Frequency <span className="text-[#ff3c6e]">*</span>
              </label>
              <select
                value={formData.cadence}
                onChange={(e) => setFormData({ ...formData, cadence: e.target.value })}
                className="w-full px-3.5 py-2.5 bg-white/90 border border-purple-200/80 rounded-xl text-xs text-[#17132d] font-medium focus:outline-none focus:border-[#6f55ef]"
              >
                {CADENCE_OPTIONS.map((c) => (
                  <option key={c.value} value={c.value}>{c.label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Row 3: Days Inactive & Previous Price (Optional) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-[11px] font-[800] uppercase tracking-[1px] text-[#17132d] mb-1.5">
                Days Since Last Use (Inactivity) <span className="text-[#ff3c6e]">*</span>
              </label>
              <input
                type="number"
                min="0"
                placeholder="0 if active, 187 if unused"
                value={formData.last_used_days_ago}
                onChange={(e) => {
                  setFormData({ ...formData, last_used_days_ago: e.target.value });
                  if (errors.last_used_days_ago) setErrors({ ...errors, last_used_days_ago: null });
                }}
                className={`w-full px-3.5 py-2.5 bg-white/90 border rounded-xl text-xs text-[#17132d] font-medium focus:outline-none focus:ring-2 transition-all ${
                  errors.last_used_days_ago ? 'border-[#ff3c6e] focus:ring-[#ff3c6e]/20' : 'border-purple-200/80 focus:border-[#6f55ef] focus:ring-[#6f55ef]/20'
                }`}
              />
              <span className="text-[10px] text-[#17132d]/50 mt-1 block">
                Values &gt; 90 days trigger high waste scores for autonomous remediation.
              </span>
              {errors.last_used_days_ago && (
                <p className="text-[10px] text-[#ff3c6e] mt-1 font-semibold">{errors.last_used_days_ago}</p>
              )}
            </div>

            <div>
              <label className="block text-[11px] font-[800] uppercase tracking-[1px] text-[#17132d] mb-1.5">
                Previous Price (Optional Price-Hike Detection)
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                placeholder="e.g. 499 (if recent price hike)"
                value={formData.previous_price}
                onChange={(e) => {
                  setFormData({ ...formData, previous_price: e.target.value });
                  if (errors.previous_price) setErrors({ ...errors, previous_price: null });
                }}
                className="w-full px-3.5 py-2.5 bg-white/90 border border-purple-200/80 rounded-xl text-xs text-[#17132d] font-medium focus:outline-none focus:border-[#6f55ef]"
              />
              <span className="text-[10px] text-[#17132d]/50 mt-1 block">
                Triggers unscheduled rate-hike flag and loyalty negotiation offer.
              </span>
              {errors.previous_price && (
                <p className="text-[10px] text-[#ff3c6e] mt-1 font-semibold">{errors.previous_price}</p>
              )}
            </div>
          </div>

          {/* Row 4: Transaction Date */}
          <div>
            <label className="block text-[11px] font-[800] uppercase tracking-[1px] text-[#17132d] mb-1.5">
              Billing Date / Transaction Date (Optional)
            </label>
            <input
              type="date"
              value={formData.transaction_date}
              onChange={(e) => setFormData({ ...formData, transaction_date: e.target.value })}
              className="w-full sm:w-1/2 px-3.5 py-2.5 bg-white/90 border border-purple-200/80 rounded-xl text-xs text-[#17132d] font-medium focus:outline-none focus:border-[#6f55ef]"
            />
          </div>

          {/* Advanced Switches: Duplicates, Bundles, Free Trial */}
          <div className="p-4 rounded-xl bg-purple-50/50 border border-purple-100 space-y-3">
            <span className="text-[10px] font-[800] uppercase tracking-[1.5px] text-[#6f55ef] block">
              Advanced Forensics Flags
            </span>

            {/* Duplicate Flag */}
            <div className="flex items-center justify-between gap-3">
              <label className="text-xs text-[#17132d] font-semibold flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.is_duplicate}
                  onChange={(e) => setFormData({ ...formData, is_duplicate: e.target.checked })}
                  className="rounded text-[#6f55ef] focus:ring-[#6f55ef] w-4 h-4"
                />
                <span>Overlapping / Duplicate service in same category</span>
              </label>
            </div>

            {formData.is_duplicate && (
              <div className="pl-6 pt-1">
                <input
                  type="text"
                  placeholder="Competing service name (e.g. YouTube Premium or Spotify)"
                  value={formData.duplicate_counterpart}
                  onChange={(e) => setFormData({ ...formData, duplicate_counterpart: e.target.value })}
                  className="w-full px-3 py-2 bg-white border border-purple-200 rounded-lg text-xs text-[#17132d]"
                />
              </div>
            )}

            {/* Bundle Flag */}
            <div className="flex items-center justify-between gap-3">
              <label className="text-xs text-[#17132d] font-semibold flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.is_bundled}
                  onChange={(e) => setFormData({ ...formData, is_bundled: e.target.checked })}
                  className="rounded text-[#6f55ef] focus:ring-[#6f55ef] w-4 h-4"
                />
                <span>Part of a bundled package or carrier plan</span>
              </label>
            </div>

            {formData.is_bundled && (
              <div className="pl-6 pt-1">
                <input
                  type="text"
                  placeholder="Bundle provider (e.g. Apple One, Telco Plan)"
                  value={formData.bundle_provider}
                  onChange={(e) => setFormData({ ...formData, bundle_provider: e.target.value })}
                  className="w-full px-3 py-2 bg-white border border-purple-200 rounded-lg text-xs text-[#17132d]"
                />
              </div>
            )}

            {/* Free Trial Conversion */}
            <div className="flex items-center justify-between gap-3">
              <label className="text-xs text-[#17132d] font-semibold flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.trial_converted}
                  onChange={(e) => setFormData({ ...formData, trial_converted: e.target.checked })}
                  className="rounded text-[#6f55ef] focus:ring-[#6f55ef] w-4 h-4"
                />
                <span>Recently converted from free trial to paid recurring billing</span>
              </label>
            </div>
          </div>

          {/* Footer Actions */}
          <div className="pt-3 border-t border-purple-100 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl border border-[#17132d]/15 hover:bg-[#17132d]/5 text-[#17132d] text-xs font-[800] uppercase tracking-[1px] transition-all"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#6f55ef] to-[#5136db] hover:from-[#5c3ee6] hover:to-[#4329cb] text-white text-xs font-[800] uppercase tracking-[1px] shadow-md shadow-[#6f55ef]/25 transition-all active:scale-95 flex items-center gap-2 disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Ingesting Data...</span>
                </>
              ) : (
                <>
                  <PlusCircle className="w-4 h-4" />
                  <span>Add Subscription</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
