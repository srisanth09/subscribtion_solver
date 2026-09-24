import React, { useState, useEffect } from 'react';
import { api } from './services/api';
import Navbar from './components/Navbar';
import SavingsSummaryCards from './components/SavingsSummaryCards';
import AgentTerminal from './components/AgentTerminal';
import ApprovalsSection from './components/ApprovalsSection';
import SubscriptionCard from './components/SubscriptionCard';
import GuardrailsModal from './components/GuardrailsModal';
import NegotiationModal from './components/NegotiationModal';
import AuditLogTimeline from './components/AuditLogTimeline';
import TransactionsTable from './components/TransactionsTable';
import EmailExplorer from './components/EmailExplorer';
import SavingsReportModal from './components/SavingsReportModal';
import AddSubscriptionModal from './components/AddSubscriptionModal';
import PromptConsole from './components/PromptConsole';
import NegotiationModeHub from './components/NegotiationModeHub';

import { 
  ShieldCheck, 
  Sparkles, 
  Filter, 
  Search, 
  Layers, 
  Bot, 
  CheckCircle,
  HelpCircle,
  Zap,
  Plus,
  HandCoins
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [subscriptions, setSubscriptions] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [logs, setLogs] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [emails, setEmails] = useState([]);
  const [guardrails, setGuardrails] = useState(null);

  const [isRunningAudit, setIsRunningAudit] = useState(false);
  const [auditTraces, setAuditTraces] = useState([]);

  // Prompt Console State
  const [promptResponse, setPromptResponse] = useState(null);
  const [isProcessingPrompt, setIsProcessingPrompt] = useState(false);

  // Modals
  const [isAddSubOpen, setIsAddSubOpen] = useState(false);
  const [isGuardrailsOpen, setIsGuardrailsOpen] = useState(false);
  const [isReportOpen, setIsReportOpen] = useState(false);
  const [reportData, setReportData] = useState(null);
  const [isNegotiationOpen, setIsNegotiationOpen] = useState(false);
  const [activeNegotiation, setActiveNegotiation] = useState(null);

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');

  // Load initial data
  const refreshAllData = async () => {
    try {
      const [subsRes, metricsRes, logsRes, txRes, emailsRes, guardrailsRes] = await Promise.all([
        api.getSubscriptions(),
        api.getSavings(),
        api.getAuditLogs(),
        api.getTransactions(),
        api.getEmails(),
        api.getGuardrails()
      ]);

      setSubscriptions(subsRes.data);
      setMetrics(metricsRes.data);
      setLogs(logsRes.data);
      setTransactions(txRes.data);
      setEmails(emailsRes.data);
      setGuardrails(guardrailsRes.data);
    } catch (err) {
      console.error("Error refreshing data:", err);
    }
  };

  useEffect(() => {
    refreshAllData();
  }, []);

  // Run Master Agent Audit
  const handleRunAudit = async (customPrompt = "Audit my subscriptions and cancel inactive ones under guardrail limits") => {
    setIsRunningAudit(true);
    setAuditTraces([
      { step: "INIT", message: "Starting Agent Orchestrator pipeline...", status: "INFO", timestamp: new Date().toLocaleTimeString() }
    ]);

    try {
      const res = await api.runAudit(customPrompt);
      if (res.data?.audit_trace) {
        setAuditTraces(res.data.audit_trace);
      }
      await refreshAllData();
    } catch (err) {
      console.error("Audit error:", err);
      setAuditTraces(prev => [
        ...prev,
        { step: "ERROR", message: "Audit failed: " + (err.response?.data?.detail || err.message), status: "WARNING", timestamp: new Date().toLocaleTimeString() }
      ]);
    } finally {
      setIsRunningAudit(false);
    }
  };

  // Add Manual Subscription
  const handleAddSubscription = async (formData) => {
    const res = await api.addSubscription(formData);
    await refreshAllData();
    return res;
  };

  // Execute Natural Language Prompt
  const handleExecutePrompt = async (promptText) => {
    setIsProcessingPrompt(true);
    try {
      const res = await api.sendPrompt(promptText);
      setPromptResponse(res.data);
      if (res.data?.intent === 'AUDIT_EXECUTION') {
        setAuditTraces(prev => [
          ...prev,
          { step: "PROMPT_AUDIT", message: `Agent executed audit prompt: "${promptText}"`, status: "SUCCESS", timestamp: new Date().toLocaleTimeString() }
        ]);
      }
      await refreshAllData();
    } catch (err) {
      console.error("Prompt processing error:", err);
      setPromptResponse({
        intent: "ERROR",
        prompt: promptText,
        reply: "Prompt execution error: " + (err.response?.data?.detail || err.message),
        monthly_savings: 0
      });
    } finally {
      setIsProcessingPrompt(false);
    }
  };

  // Reset Demo
  const handleResetDemo = async () => {
    if (window.confirm("Reset all subscriptions and re-seed clean hackathon demo data?")) {
      await api.resetAndSeed();
      setAuditTraces([]);
      await refreshAllData();
      alert("Database reset and re-seeded with fresh data!");
    }
  };

  // Human in the Loop Actions
  const handlePerformAction = async (subId, action) => {
    try {
      await api.performAction(subId, action);
      await refreshAllData();
    } catch (err) {
      alert("Action failed: " + (err.response?.data?.detail || err.message));
    }
  };

  // Negotiation Mode
  const handleNegotiate = async (sub) => {
    try {
      const res = await api.startNegotiation(sub.id);
      setActiveNegotiation(res.data.offer);
      setIsNegotiationOpen(true);
      await refreshAllData();
    } catch (err) {
      alert("Negotiation start failed: " + (err.response?.data?.detail || err.message));
    }
  };

  const handleAcceptOffer = async (subId, offerId) => {
    try {
      await api.acceptNegotiationOffer(subId, offerId);
      setIsNegotiationOpen(false);
      await refreshAllData();
      alert("Merchant retention discount applied successfully!");
    } catch (err) {
      alert("Offer acceptance failed: " + (err.response?.data?.detail || err.message));
    }
  };

  const handleDeclineOffer = async (subId, offerId) => {
    try {
      await api.declineNegotiationOffer(subId, offerId);
      setIsNegotiationOpen(false);
      await refreshAllData();
      alert("Offer declined. Subscription remains active at standard rate.");
    } catch (err) {
      alert("Offer decline failed: " + (err.response?.data?.detail || err.message));
    }
  };

  const handleFailOffer = async (subId, offerId) => {
    try {
      await api.failNegotiationOffer(subId, offerId, "Merchant declined concession");
      setIsNegotiationOpen(false);
      await refreshAllData();
      alert("Negotiation completed with no concession. Subscription maintained at original price.");
    } catch (err) {
      alert("Fail negotiation action failed: " + (err.response?.data?.detail || err.message));
    }
  };

  const handleDeclineAndCancel = async (subId, offerId) => {
    try {
      if (offerId) {
        try {
          await api.declineNegotiationOffer(subId, offerId);
        } catch (_) {}
      }
      await handlePerformAction(subId, 'approve_cancel');
      setIsNegotiationOpen(false);
    } catch (err) {
      alert("Cancellation failed: " + (err.response?.data?.detail || err.message));
    }
  };

  // Guardrails Save
  const handleSaveGuardrails = async (newConfig) => {
    try {
      const res = await api.updateGuardrails(newConfig);
      setGuardrails(res.data);
      await refreshAllData();
    } catch (err) {
      alert("Guardrail update failed: " + err.message);
    }
  };

  // Open Report Modal
  const handleOpenReport = async () => {
    try {
      const res = await api.getSavingsReport();
      setReportData(res.data);
      setIsReportOpen(true);
    } catch (err) {
      alert("Report generation failed: " + err.message);
    }
  };

  // Filter Subscriptions
  const filteredSubscriptions = subscriptions.filter(sub => {
    const matchesSearch = sub.merchant.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          sub.category.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || sub.status === statusFilter;
    const matchesCategory = categoryFilter === 'all' || sub.category === categoryFilter;
    return matchesSearch && matchesStatus && matchesCategory;
  });

  const pendingApprovals = subscriptions.filter(s => s.status === 'pending_approval');

  return (
    <div className="min-h-screen text-[#17132d] flex flex-col selection:bg-[#6f55ef]/20 selection:text-[#6f55ef]">
      
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onRunAudit={() => handleRunAudit()}
        isRunningAudit={isRunningAudit}
        onOpenGuardrails={() => setIsGuardrailsOpen(true)}
        onOpenReport={handleOpenReport}
        onResetDemo={handleResetDemo}
        onOpenAddSubscription={() => setIsAddSubOpen(true)}
        pendingApprovalsCount={pendingApprovals.length}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Top VeriVision Glass Hero Banner */}
        <div className="mb-8 p-6 rounded-2xl bg-white/70 backdrop-blur-2xl border border-white/90 shadow-[0_10px_30px_rgba(23,19,45,0.05)] flex flex-col md:flex-row md:items-center justify-between gap-5 transition-all">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-[#6f55ef]/12 text-[#6f55ef] flex items-center justify-center border border-[#6f55ef]/25 shadow-xs shrink-0">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <div className="text-[14px] font-[900] tracking-[1.5px] uppercase text-[#17132d] flex items-center gap-2.5">
                <span>Autonomous Spend Guardian Active</span>
                <span className="text-[9px] bg-[#6f55ef]/15 text-[#6f55ef] px-2.5 py-0.5 rounded-full font-mono font-[800] tracking-[1.5px] uppercase border border-[#6f55ef]/30">
                  AUTO-LIMIT: ₹{guardrails?.auto_action_limit?.toLocaleString() || '2,000'}
                </span>
              </div>
              <p className="text-xs text-[#17132d]/70 mt-1 font-medium max-w-2xl leading-relaxed">
                Continuous financial forensics engine: scanning recurring cadences, tracking price hikes, and enforcing policy guardrails.
              </p>
            </div>
          </div>

          {/* Quick Problem Statement Scenario Triggers */}
          <div className="flex flex-wrap items-center gap-2 shrink-0">
            <button
              onClick={() => handleRunAudit("INPUT 1: StreamFlix unused 187 days, under limit, auto-cancel")}
              className="px-3.5 py-2 rounded-xl bg-white/80 hover:bg-[#6f55ef]/10 text-[#17132d] text-[11px] font-[800] tracking-[0.5px] border border-[#17132d]/15 hover:border-[#6f55ef]/40 flex items-center gap-1.5 transition-all active:scale-95 shadow-xs"
            >
              <Zap className="w-3.5 h-3.5 text-[#6f55ef]" />
              Input 1 (Auto-Cancel)
            </button>

            <button
              onClick={() => handleRunAudit("INPUT 2: TuneWave vs MusicBox duplicate category, escalate to human")}
              className="px-3.5 py-2 rounded-xl bg-white/80 hover:bg-amber-500/10 text-[#17132d] text-[11px] font-[800] tracking-[0.5px] border border-[#17132d]/15 hover:border-amber-500/40 flex items-center gap-1.5 transition-all active:scale-95 shadow-xs"
            >
              <Zap className="w-3.5 h-3.5 text-amber-500" />
              Input 2 (Ambiguity)
            </button>

            <button
              onClick={() => handleRunAudit("INPUT 3: HealthGuard Insurance in protected category, block autonomy")}
              className="px-3.5 py-2 rounded-xl bg-white/80 hover:bg-[#68c7ff]/15 text-[#17132d] text-[11px] font-[800] tracking-[0.5px] border border-[#17132d]/15 hover:border-[#68c7ff]/40 flex items-center gap-1.5 transition-all active:scale-95 shadow-xs"
            >
              <Zap className="w-3.5 h-3.5 text-[#5136db]" />
              Input 3 (Guardrail Block)
            </button>

            <button
              onClick={() => {
                setActiveTab('negotiation_hub');
              }}
              className="px-3.5 py-2 rounded-xl bg-white/90 hover:bg-emerald-50 text-emerald-800 text-[11px] font-[800] tracking-[0.5px] border border-emerald-300 hover:border-emerald-500 flex items-center gap-1.5 transition-all active:scale-95 shadow-xs"
            >
              <HandCoins className="w-3.5 h-3.5 text-emerald-600" />
              Idea 2 (Negotiation Mode)
            </button>
          </div>
        </div>

        {/* Live Savings Metrics Cards */}
        <SavingsSummaryCards 
          metrics={metrics} 
          onOpenApprovals={() => setActiveTab('approvals')} 
        />

        {/* Natural Language Prompt Console */}
        <PromptConsole
          onExecutePrompt={handleExecutePrompt}
          isProcessing={isProcessingPrompt}
          promptResponse={promptResponse}
          onClearResponse={() => setPromptResponse(null)}
          onOpenApprovals={() => setActiveTab('approvals')}
        />

        {/* Real-time Agent Reasoning Terminal (VeriVision scan line & console) */}
        <AgentTerminal 
          traces={auditTraces} 
          isRunning={isRunningAudit} 
        />

        {/* ========================================================================= */}
        {/* TAB 1: DASHBOARD / CONTROL CENTER                                         */}
        {/* ========================================================================= */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            
            {/* Pending Approvals Callout (if any) */}
            {pendingApprovals.length > 0 && (
              <ApprovalsSection
                pendingSubscriptions={pendingApprovals}
                onApproveCancel={(id) => handlePerformAction(id, 'approve_cancel')}
                onKeepSubscription={(id) => handlePerformAction(id, 'keep')}
                onNegotiate={handleNegotiate}
              />
            )}

            {/* Subscriptions Grid Header & Filters */}
            <div>
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-5">
                <div>
                  <h3 className="text-base font-[900] tracking-[1px] uppercase text-[#17132d] flex items-center gap-2.5">
                    <Layers className="w-5 h-5 text-[#6f55ef]" />
                    Monitored Recurring Subscriptions ({filteredSubscriptions.length})
                  </h3>
                  <p className="text-xs text-[#17132d]/60 mt-0.5 font-medium">
                    Portfolio of recurring commitments sorted by waste potential
                  </p>
                </div>

                {/* Filter Controls (VeriVision Pill Style) */}
                <div className="flex flex-wrap items-center gap-2.5">
                  {/* Add Subscription Primary Button */}
                  <button
                    onClick={() => setIsAddSubOpen(true)}
                    className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-[800] uppercase tracking-[1px] bg-gradient-to-r from-[#6f55ef] to-[#5136db] hover:from-[#5c3ee6] hover:to-[#4329cb] text-white shadow-md shadow-[#6f55ef]/25 transition-all active:scale-95 shrink-0"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Add Subscription</span>
                  </button>

                  {/* Search */}
                  <div className="relative w-48 sm:w-52">
                    <Search className="w-3.5 h-3.5 text-[#17132d]/40 absolute left-3.5 top-3" />
                    <input
                      type="text"
                      placeholder="Search service..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-9 pr-3 py-2 bg-white/80 backdrop-blur-md border border-[#6f55ef]/20 rounded-xl text-xs text-[#17132d] placeholder-[#17132d]/40 focus:outline-none focus:border-[#6f55ef] focus:ring-2 focus:ring-[#6f55ef]/20 shadow-xs"
                    />
                  </div>

                  {/* Status filter */}
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="bg-white/80 backdrop-blur-md border border-[#6f55ef]/20 rounded-xl px-3.5 py-2 text-xs font-[700] text-[#17132d]/80 focus:outline-none focus:border-[#6f55ef] shadow-xs"
                  >
                    <option value="all">All Statuses</option>
                    <option value="active">Active & Verified</option>
                    <option value="pending_approval">Needs Approval</option>
                    <option value="cancelled">Auto-Cancelled</option>
                    <option value="protected">Protected</option>
                    <option value="negotiating">Negotiating</option>
                    <option value="negotiated">Negotiated Discounts</option>
                  </select>
                </div>
              </div>

              {/* Subscriptions Cards Grid or Empty State */}
              {filteredSubscriptions.length === 0 ? (
                <div className="text-center py-12 px-4 rounded-2xl bg-white/70 backdrop-blur-md border border-dashed border-purple-200 shadow-xs">
                  <Layers className="w-10 h-10 text-[#6f55ef]/40 mx-auto mb-3" />
                  <h4 className="text-sm font-[800] text-[#17132d] uppercase tracking-[1px]">No Subscriptions Found</h4>
                  <p className="text-xs text-[#17132d]/60 max-w-sm mx-auto mt-1 mb-4 font-medium">
                    No subscriptions match your current search filters. Add a new recurring subscription to monitor.
                  </p>
                  <button
                    onClick={() => setIsAddSubOpen(true)}
                    className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-[800] uppercase tracking-[1px] bg-gradient-to-r from-[#6f55ef] to-[#5136db] text-white shadow-md shadow-[#6f55ef]/25 hover:from-[#5c3ee6] hover:to-[#4329cb] active:scale-95 transition-all"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Add New Subscription</span>
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                  {filteredSubscriptions.map((sub) => (
                    <SubscriptionCard
                      key={sub.id}
                      subscription={sub}
                      onPerformAction={handlePerformAction}
                      onNegotiate={handleNegotiate}
                    />
                  ))}
                </div>
              )}
            </div>

          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 2: APPROVALS ONLY                                                     */}
        {/* ========================================================================= */}
        {activeTab === 'approvals' && (
          <ApprovalsSection
            pendingSubscriptions={pendingApprovals}
            onApproveCancel={(id) => handlePerformAction(id, 'approve_cancel')}
            onKeepSubscription={(id) => handlePerformAction(id, 'keep')}
            onNegotiate={handleNegotiate}
          />
        )}

        {/* ========================================================================= */}
        {/* TAB 3: ALL SUBSCRIPTIONS                                                  */}
        {/* ========================================================================= */}
        {activeTab === 'subscriptions' && (
          <div>
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-base font-[900] tracking-[1px] uppercase text-[#17132d]">
                All Subscriptions ({subscriptions.length})
              </h2>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setIsAddSubOpen(true)}
                  className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-[800] uppercase tracking-[1px] bg-gradient-to-r from-[#6f55ef] to-[#5136db] hover:from-[#5c3ee6] hover:to-[#4329cb] text-white shadow-md shadow-[#6f55ef]/25 active:scale-95 transition-all"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add Subscription</span>
                </button>
                <button
                  onClick={() => handleRunAudit()}
                  className="text-xs font-[800] tracking-[1px] uppercase text-[#6f55ef] hover:underline"
                >
                  Re-scan portfolio
                </button>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {filteredSubscriptions.map((sub) => (
                <SubscriptionCard
                  key={sub.id}
                  subscription={sub}
                  onPerformAction={handlePerformAction}
                  onNegotiate={handleNegotiate}
                />
              ))}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 4: NEGOTIATION MODE HUB & TEST MERCHANT SANDBOX                       */}
        {/* ========================================================================= */}
        {activeTab === 'negotiation_hub' && (
          <NegotiationModeHub
            subscriptions={subscriptions}
            guardrails={guardrails}
            onUpdateGuardrails={handleSaveGuardrails}
            onRefreshAllData={refreshAllData}
          />
        )}

        {/* ========================================================================= */}
        {/* TAB 5: AUDIT TRAIL TIMELINE                                               */}
        {/* ========================================================================= */}
        {activeTab === 'audit_trail' && (
          <AuditLogTimeline logs={logs} />
        )}

        {/* ========================================================================= */}
        {/* TAB 5: DATA FEEDS (Transactions & Emails)                                 */}
        {/* ========================================================================= */}
        {activeTab === 'data_feeds' && (
          <div className="space-y-8">
            <TransactionsTable transactions={transactions} />
            <EmailExplorer emails={emails} />
          </div>
        )}

      </main>

      {/* Modals */}
      <GuardrailsModal
        isOpen={isGuardrailsOpen}
        onClose={() => setIsGuardrailsOpen(false)}
        guardrails={guardrails}
        onSave={handleSaveGuardrails}
      />

      <NegotiationModal
        isOpen={isNegotiationOpen}
        onClose={() => setIsNegotiationOpen(false)}
        negotiationData={activeNegotiation}
        onAcceptOffer={handleAcceptOffer}
        onDeclineOffer={handleDeclineOffer}
        onFailOffer={handleFailOffer}
        onDeclineAndCancel={handleDeclineAndCancel}
      />

      <SavingsReportModal
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
        reportData={reportData}
      />

      <AddSubscriptionModal
        isOpen={isAddSubOpen}
        onClose={() => setIsAddSubOpen(false)}
        onAddSuccess={handleAddSubscription}
      />

      {/* VeriVision Glass Footer */}
      <footer className="border-t border-[#6f55ef]/15 bg-white/40 backdrop-blur-xl py-8 text-center text-xs text-[#17132d]/60">
        <p className="font-[800] tracking-[1px] uppercase text-[#17132d]">
          SpendGuardian • Autonomous Subscription & Recurring-Spend Guardian Agent
        </p>
        <p className="mt-1 font-medium text-[#17132d]/50">
          PRAGYAAN 2.0 Hackathon • KMIT CSE(AI&ML) • VeriVision-Inspired Forensic Design
        </p>
      </footer>

    </div>
  );
}
