import React, { useState, useEffect } from 'react';
import { 
  HandCoins, 
  Send, 
  CheckCircle2, 
  XCircle, 
  Sparkles, 
  Zap, 
  RefreshCw, 
  MessageSquare, 
  ArrowRight, 
  ShieldCheck, 
  Sliders, 
  Bot, 
  Building2, 
  TrendingDown, 
  Check, 
  AlertTriangle 
} from 'lucide-react';
import { api } from '../services/api';

export default function NegotiationModeHub({
  subscriptions = [],
  guardrails,
  onUpdateGuardrails,
  onRefreshAllData
}) {
  const [communications, setCommunications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedSubId, setSelectedSubId] = useState('');
  const [requestType, setRequestType] = useState('DISCOUNT_REQUEST');
  const [isSimulating, setIsSimulating] = useState(false);
  const [latestEvaluation, setLatestEvaluation] = useState(null);
  const [selectedComm, setSelectedComm] = useState(null);

  // Eligible candidate subscriptions (active or pending)
  const candidateSubs = subscriptions.filter(
    s => s.status !== 'cancelled' && s.category !== 'loan_payment' && s.category !== 'insurance'
  );

  const fetchCommunications = async () => {
    setLoading(true);
    try {
      const res = await api.getMerchantCommunications();
      setCommunications(res.data);
    } catch (err) {
      console.error("Failed to load merchant communications:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCommunications();
    if (candidateSubs.length > 0 && !selectedSubId) {
      setSelectedSubId(candidateSubs[0].id.toString());
    }
  }, [subscriptions]);

  const handleToggleMode = async () => {
    const newMode = !guardrails?.negotiation_mode;
    try {
      await onUpdateGuardrails({ negotiation_mode: newMode });
    } catch (err) {
      alert("Failed to toggle negotiation mode: " + err.message);
    }
  };

  const handleSimulate = async (outcome) => {
    if (!selectedSubId) {
      alert("Please select a subscription first.");
      return;
    }
    setIsSimulating(true);
    setLatestEvaluation(null);

    try {
      const res = await api.simulateTestMerchant(
        parseInt(selectedSubId),
        outcome,
        requestType
      );
      setLatestEvaluation(res.data);
      await fetchCommunications();
      if (onRefreshAllData) await onRefreshAllData();
    } catch (err) {
      alert("Simulation failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setIsSimulating(false);
    }
  };

  const handleManualDispatch = async () => {
    if (!selectedSubId) {
      alert("Please select a subscription first.");
      return;
    }
    setIsSimulating(true);
    try {
      await api.sendMerchantNegotiation(
        parseInt(selectedSubId),
        requestType,
        requestType === 'TIER_DOWNGRADE' ? 35.0 : 25.0
      );
      await fetchCommunications();
      if (onRefreshAllData) await onRefreshAllData();
      alert("Negotiation request dispatched to merchant!");
    } catch (err) {
      alert("Dispatch failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setIsSimulating(false);
    }
  };

  const handleRespondToComm = async (commId, outcome) => {
    try {
      const res = await api.respondMerchantNegotiation(commId, outcome);
      setLatestEvaluation(res.data);
      await fetchCommunications();
      if (onRefreshAllData) await onRefreshAllData();
    } catch (err) {
      alert("Response error: " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="space-y-6">
      
      {/* 1. Header Banner & Mode Toggle */}
      <div className="p-6 rounded-3xl bg-white/70 backdrop-blur-2xl border border-white/90 shadow-[0_12px_36px_rgba(23,19,45,0.06)] flex flex-col lg:flex-row lg:items-center justify-between gap-5 transition-all">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-[#6f55ef] to-[#5136db] text-white flex items-center justify-center shadow-lg shadow-[#6f55ef]/25 shrink-0 mt-0.5">
            <HandCoins className="w-6 h-6" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2.5">
              <h2 className="text-base font-[900] tracking-[1px] uppercase text-[#17132d]">
                Negotiation Mode Engine
              </h2>
              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-[800] uppercase tracking-[1px] border ${
                guardrails?.negotiation_mode 
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-300' 
                  : 'bg-purple-50 text-purple-700 border-purple-200'
              }`}>
                {guardrails?.negotiation_mode ? '● ACTIVE (DISCOUNT-FIRST)' : '○ STANDARD (CANCEL-FIRST)'}
              </span>
            </div>
            <p className="text-xs text-[#17132d]/70 mt-1 font-medium max-w-2xl leading-relaxed">
              The agent contacts merchants with a generated downgrade or discount request before cancelling an eligible subscription. Users save recurring spend without completely losing service.
            </p>
          </div>
        </div>

        {/* Mode Toggle Switch */}
        <div className="flex items-center gap-3 bg-[#17132d]/5 px-4 py-3 rounded-2xl border border-[#6f55ef]/15 self-start lg:self-center shrink-0">
          <div className="text-right">
            <span className="text-xs font-[800] uppercase tracking-[0.5px] text-[#17132d] block">
              Negotiation Mode
            </span>
            <span className="text-[10px] text-[#17132d]/50 font-medium">
              {guardrails?.negotiation_mode ? 'Contact merchants first' : 'Direct auto-cancel'}
            </span>
          </div>
          <button
            type="button"
            onClick={handleToggleMode}
            className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
              guardrails?.negotiation_mode ? 'bg-[#6f55ef]' : 'bg-[#17132d]/20'
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                guardrails?.negotiation_mode ? 'translate-x-5' : 'translate-x-0'
              }`}
            />
          </button>
        </div>
      </div>

      {/* 2. Interactive Test Merchant Sandbox */}
      <div className="p-6 rounded-3xl bg-gradient-to-br from-white/90 via-[#f9f8ff]/80 to-white/90 backdrop-blur-2xl border border-[#6f55ef]/20 shadow-[0_12px_36px_rgba(111,85,239,0.06)]">
        <div className="flex items-center justify-between mb-4 border-b border-[#6f55ef]/15 pb-3">
          <div className="flex items-center gap-2">
            <Building2 className="w-5 h-5 text-[#6f55ef]" />
            <h3 className="text-sm font-[900] tracking-[1px] uppercase text-[#17132d]">
              Test Merchant Simulation Sandbox
            </h3>
          </div>
          <span className="text-[10px] font-mono font-[800] text-[#6f55ef] bg-[#6f55ef]/10 px-2.5 py-0.5 rounded-full border border-[#6f55ef]/20">
            TEST SPEC: IDEA 2
          </span>
        </div>

        <p className="text-xs text-[#17132d]/70 mb-5 font-medium">
          Test how the agent drafts, dispatches, and evaluates responses from a merchant API. Click below to simulate the merchant accepting or rejecting the proposal:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-5">
          {/* Pick Subscription */}
          <div>
            <label className="block text-[10px] font-[800] uppercase tracking-[1px] text-[#17132d]/60 mb-1.5">
              Select Subscription
            </label>
            <select
              value={selectedSubId}
              onChange={(e) => setSelectedSubId(e.target.value)}
              className="w-full bg-white/90 border border-[#6f55ef]/25 rounded-xl px-3 py-2 text-xs font-[700] text-[#17132d] focus:outline-none focus:border-[#6f55ef]"
            >
              {candidateSubs.map(s => (
                <option key={s.id} value={s.id}>
                  {s.merchant} — {s.currency}{s.amount}/mo ({s.category})
                </option>
              ))}
            </select>
          </div>

          {/* Request Type */}
          <div>
            <label className="block text-[10px] font-[800] uppercase tracking-[1px] text-[#17132d]/60 mb-1.5">
              Request Type
            </label>
            <select
              value={requestType}
              onChange={(e) => setRequestType(e.target.value)}
              className="w-full bg-white/90 border border-[#6f55ef]/25 rounded-xl px-3 py-2 text-xs font-[700] text-[#17132d] focus:outline-none focus:border-[#6f55ef]"
            >
              <option value="DISCOUNT_REQUEST">25% Retention Discount</option>
              <option value="TIER_DOWNGRADE">Lighter Essential Tier Downgrade (35% off)</option>
            </select>
          </div>

          {/* Action CTAs */}
          <div className="flex flex-col justify-end gap-2">
            <button
              onClick={handleManualDispatch}
              disabled={isSimulating}
              className="w-full px-4 py-2 rounded-xl bg-white/80 hover:bg-[#6f55ef]/10 text-[#6f55ef] text-xs font-[800] uppercase tracking-[1px] border border-[#6f55ef]/30 flex items-center justify-center gap-1.5 transition-all active:scale-95 disabled:opacity-50"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Dispatch Request Only</span>
            </button>
          </div>
        </div>

        {/* Simulation Triggers (Accept / Reject) */}
        <div className="p-4 rounded-2xl bg-white/70 border border-[#6f55ef]/20 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-xs font-[800] uppercase tracking-[0.5px] text-[#17132d]">
            <Sparkles className="w-4 h-4 text-[#6f55ef]" />
            <span>Simulate Incoming Merchant Decision:</span>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <button
              onClick={() => handleSimulate('ACCEPTED')}
              disabled={isSimulating}
              className="flex-1 sm:flex-none px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-[800] uppercase tracking-[1px] flex items-center justify-center gap-2 shadow-md shadow-emerald-600/20 active:scale-95 transition-all disabled:opacity-50"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Test Merchant: Accept Offer</span>
            </button>

            <button
              onClick={() => handleSimulate('REJECTED')}
              disabled={isSimulating}
              className="flex-1 sm:flex-none px-4 py-2.5 rounded-xl bg-gradient-to-r from-[#ff3c6e] to-[#e62e5c] hover:from-[#ff527f] hover:to-[#ff3c6e] text-white text-xs font-[800] uppercase tracking-[1px] flex items-center justify-center gap-2 shadow-md shadow-[#ff3c6e]/20 active:scale-95 transition-all disabled:opacity-50"
            >
              <XCircle className="w-4 h-4" />
              <span>Test Merchant: Reject Offer</span>
            </button>
          </div>
        </div>

        {/* Live Evaluation Box */}
        {latestEvaluation && (
          <div className={`mt-5 p-4 rounded-2xl border ${
            latestEvaluation.status === 'ACCEPTED'
              ? 'bg-emerald-50/80 border-emerald-300 text-emerald-950'
              : 'bg-rose-50/80 border-rose-300 text-rose-950'
          } animate-in fade-in slide-in-from-top-2 duration-300`}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2 font-[800] text-xs uppercase tracking-[1px]">
                <Bot className="w-4 h-4 text-[#6f55ef]" />
                <span>Agent Evaluation Outcome: {latestEvaluation.status}</span>
              </div>
              <span className="text-[10px] font-mono font-[800] uppercase px-2 py-0.5 rounded-md bg-white/60 border border-current">
                Action: {latestEvaluation.resulting_action}
              </span>
            </div>
            <p className="text-xs font-mono whitespace-pre-wrap leading-relaxed">
              {latestEvaluation.agent_evaluation}
            </p>
            <div className="mt-2.5 pt-2 border-t border-current/15 flex flex-wrap items-center gap-4 text-xs font-[800]">
              <span>Merchant: {latestEvaluation.merchant}</span>
              <span>Updated Status: {latestEvaluation.subscription_status}</span>
              <span>New Monthly Price: ₹{latestEvaluation.new_price}</span>
              <span>Monthly Savings: +₹{latestEvaluation.monthly_savings}</span>
            </div>
          </div>
        )}

      </div>

      {/* 3. Dispatched Merchant Communications Log Table */}
      <div className="p-6 rounded-3xl bg-white/70 backdrop-blur-2xl border border-white/90 shadow-[0_12px_36px_rgba(23,19,45,0.06)]">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-[#6f55ef]" />
            <h3 className="text-sm font-[900] tracking-[1px] uppercase text-[#17132d]">
              Tracked Merchant Communication Threads ({communications.length})
            </h3>
          </div>
          <button
            onClick={fetchCommunications}
            disabled={loading}
            className="p-2 rounded-xl text-[#17132d]/60 hover:text-[#6f55ef] hover:bg-[#6f55ef]/10 transition-colors"
            title="Refresh communications"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {communications.length === 0 ? (
          <div className="text-center py-10 rounded-2xl bg-white/50 border border-dashed border-purple-200">
            <HandCoins className="w-8 h-8 text-[#6f55ef]/40 mx-auto mb-2" />
            <p className="text-xs font-[800] uppercase tracking-[1px] text-[#17132d]">
              No Merchant Negotiation Threads Yet
            </p>
            <p className="text-[11px] text-[#17132d]/60 mt-0.5">
              Enable Negotiation Mode or dispatch a request above to see merchant communications in action.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#6f55ef]/15 text-[10px] font-[800] uppercase tracking-[1.5px] text-[#17132d]/50">
                  <th className="py-3 px-3">Merchant</th>
                  <th className="py-3 px-3">Request Type</th>
                  <th className="py-3 px-3">Status</th>
                  <th className="py-3 px-3">Pricing Shift</th>
                  <th className="py-3 px-3">Resulting Action</th>
                  <th className="py-3 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-purple-50 font-medium text-[#17132d]">
                {communications.map(comm => (
                  <tr key={comm.id} className="hover:bg-[#6f55ef]/5 transition-colors">
                    <td className="py-3 px-3 font-[800] text-sm">
                      {comm.merchant}
                    </td>
                    <td className="py-3 px-3">
                      <span className="text-[10px] font-mono bg-purple-100 text-purple-800 px-2 py-0.5 rounded-full font-[700]">
                        {comm.request_type === 'TIER_DOWNGRADE' ? 'DOWNGRADE' : 'DISCOUNT'}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span className={`text-[10px] font-[800] px-2.5 py-0.5 rounded-full border ${
                        comm.status === 'MERCHANT_ACCEPTED'
                          ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                          : comm.status === 'MERCHANT_REJECTED'
                          ? 'bg-rose-50 text-rose-700 border-rose-300'
                          : 'bg-amber-50 text-amber-700 border-amber-300'
                      }`}>
                        {comm.status}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-mono">
                      <span className="line-through text-[#17132d]/40">₹{comm.original_price}</span>
                      <ArrowRight className="inline w-3 h-3 mx-1 text-[#6f55ef]" />
                      <span className="font-[800] text-[#17132d]">
                        ₹{comm.merchant_counter_price || comm.target_price}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-mono text-[11px]">
                      {comm.resulting_action || 'AWAITING_REPLY'}
                    </td>
                    <td className="py-3 px-3 text-right space-x-1.5">
                      {comm.status === 'SENT' && (
                        <>
                          <button
                            onClick={() => handleRespondToComm(comm.id, 'ACCEPTED')}
                            className="px-2.5 py-1 rounded-lg bg-emerald-100 hover:bg-emerald-200 text-emerald-800 text-[10px] font-[800] uppercase"
                            title="Simulate merchant acceptance"
                          >
                            Accept
                          </button>
                          <button
                            onClick={() => handleRespondToComm(comm.id, 'REJECTED')}
                            className="px-2.5 py-1 rounded-lg bg-rose-100 hover:bg-rose-200 text-rose-800 text-[10px] font-[800] uppercase"
                            title="Simulate merchant rejection"
                          >
                            Reject
                          </button>
                        </>
                      )}
                      <button
                        onClick={() => setSelectedComm(comm)}
                        className="px-2.5 py-1 rounded-lg bg-purple-50 hover:bg-purple-100 text-[#6f55ef] text-[10px] font-[800] uppercase border border-[#6f55ef]/20"
                      >
                        View Letter
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selectedComm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#17132d]/40 backdrop-blur-md p-4 overflow-y-auto">
          <div className="w-full max-w-xl bg-white rounded-3xl p-6 shadow-2xl border border-purple-100 space-y-4 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b border-purple-100 pb-3">
              <h4 className="font-[900] text-sm uppercase text-[#17132d]">
                Communication Details: {selectedComm.merchant}
              </h4>
              <button
                onClick={() => setSelectedComm(null)}
                className="text-xs font-[800] text-[#17132d]/50 hover:text-[#17132d]"
              >
                ✕ Close
              </button>
            </div>

            <div>
              <span className="text-[10px] font-[800] uppercase text-[#6f55ef] block mb-1">
                Outgoing Pitch Letter:
              </span>
              <pre className="p-3 bg-[#17132d] text-[#ede8ff] rounded-xl text-[11px] font-mono whitespace-pre-wrap">
                {selectedComm.pitch_message}
              </pre>
            </div>

            {selectedComm.merchant_reply_text && (
              <div>
                <span className="text-[10px] font-[800] uppercase text-emerald-700 block mb-1">
                  Merchant Reply:
                </span>
                <pre className="p-3 bg-purple-50 text-[#17132d] border border-purple-200 rounded-xl text-[11px] font-mono whitespace-pre-wrap">
                  {selectedComm.merchant_reply_text}
                </pre>
              </div>
            )}

            {selectedComm.agent_evaluation && (
              <div>
                <span className="text-[10px] font-[800] uppercase text-indigo-700 block mb-1">
                  Agent Evaluation & Action:
                </span>
                <p className="p-3 bg-indigo-50 text-indigo-950 border border-indigo-200 rounded-xl text-xs font-medium">
                  {selectedComm.agent_evaluation}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  );
}
