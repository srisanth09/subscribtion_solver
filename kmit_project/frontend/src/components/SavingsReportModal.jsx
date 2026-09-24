import React from 'react';
import { X, FileText, Download, Printer, CheckCircle, ArrowRight } from 'lucide-react';

export default function SavingsReportModal({ isOpen, onClose, reportData }) {
  if (!isOpen || !reportData) return null;

  const { metrics, report_markdown, recent_actions } = reportData;

  const handleDownloadMarkdown = () => {
    const blob = new Blob([report_markdown], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `spend_guardian_report_${new Date().toISOString().slice(0, 10)}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#17132d]/40 backdrop-blur-xl p-4">
      <div className="w-full max-w-3xl bg-white/95 backdrop-blur-2xl border border-white/95 rounded-[24px] shadow-[0_20px_60px_rgba(23,19,45,0.15)] overflow-hidden animate-in fade-in zoom-in-95 duration-200 flex flex-col max-h-[90vh]">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-[#6f55ef]/15 bg-white/60 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#6f55ef]/12 text-[#6f55ef] flex items-center justify-center border border-[#6f55ef]/25 shadow-xs">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-[900] tracking-[1px] uppercase text-[#17132d]">Audit & Savings Forensics Report</h3>
              <p className="text-xs text-[#17132d]/60 font-medium">Executive financial briefing on autonomous waste elimination</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 rounded-xl text-[#17132d]/50 hover:text-[#17132d] hover:bg-[#6f55ef]/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Scrollable Body */}
        <div className="p-6 space-y-6 overflow-y-auto print:p-0">
          
          {/* Top Metric Strip */}
          <div className="grid grid-cols-3 gap-4 p-5 rounded-2xl bg-[#6f55ef]/5 border border-[#6f55ef]/15 text-center">
            <div>
              <div className="text-[10px] text-[#17132d]/50 uppercase font-[800] tracking-[1.5px]">Realized Monthly</div>
              <div className="text-2xl font-[900] text-[#6f55ef] mt-1">
                {metrics?.currency}{metrics?.realized_monthly_savings?.toLocaleString()}
              </div>
            </div>
            <div>
              <div className="text-[10px] text-[#17132d]/50 uppercase font-[800] tracking-[1.5px]">Annual Run-Rate</div>
              <div className="text-2xl font-[900] text-[#5136db] mt-1">
                {metrics?.currency}{metrics?.realized_annual_savings?.toLocaleString()}
              </div>
            </div>
            <div>
              <div className="text-[10px] text-[#17132d]/50 uppercase font-[800] tracking-[1.5px]">Auto-Cancelled</div>
              <div className="text-2xl font-[900] text-[#17132d] mt-1">
                {metrics?.auto_cancelled_count}
              </div>
            </div>
          </div>

          {/* Formatted Report Content */}
          <div className="p-6 rounded-2xl bg-white/70 border border-[#6f55ef]/15 space-y-4 text-xs text-[#17132d]/80 leading-relaxed font-sans font-medium">
            <div>
              <h4 className="text-sm font-[900] tracking-[0.5px] uppercase text-[#17132d] mb-2">Executive Summary</h4>
              <p>
                During the current billing cycle, the <strong>Subscription & Recurring-Spend Guardian Agent</strong> audited a total of <strong>{metrics?.total_subscriptions}</strong> recurring charges. Within user-defined safety boundaries, the agent executed <strong>{metrics?.auto_cancelled_count}</strong> autonomous cancellations on zero-risk abandoned services, eliminating <strong>{metrics?.currency}{metrics?.realized_monthly_savings?.toLocaleString()}</strong> in recurring monthly waste.
              </p>
            </div>

            <div>
              <h4 className="text-sm font-[900] tracking-[0.5px] uppercase text-[#17132d] mb-2">Recent Autonomous & Approved Interventions</h4>
              <div className="space-y-2.5">
                {recent_actions?.map((action, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-white border border-[#6f55ef]/15 flex items-center justify-between shadow-xs">
                    <div>
                      <span className="font-[800] text-[#17132d]">{action.merchant}</span>
                      <span className="text-[#6f55ef] ml-2 font-mono font-[800] text-[11px]">[{action.action}]</span>
                      <p className="text-[11px] text-[#17132d]/60 mt-0.5 font-medium">{action.reason}</p>
                    </div>
                    {action.monthly_saving > 0 && (
                      <span className="text-[#6f55ef] bg-[#6f55ef]/10 border border-[#6f55ef]/20 px-2.5 py-1 rounded-full font-[900] text-[11px] shrink-0 ml-4">
                        +{metrics?.currency}{action.monthly_saving}/mo
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-sm font-[900] tracking-[0.5px] uppercase text-[#17132d] mb-1">Human-In-The-Loop Pending Items</h4>
              <p className="text-[#17132d]/60">
                {metrics?.pending_approval_count > 0 
                  ? `${metrics?.pending_approval_count} items currently require human authorization due to overlapping functionality or spending policy thresholds.`
                  : "All actionable items have been verified. Zero pending review items."}
              </p>
            </div>
          </div>

        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 bg-white/70 border-t border-[#6f55ef]/15 flex items-center justify-between gap-3 shrink-0">
          <button
            onClick={handleDownloadMarkdown}
            className="px-4 py-2.5 rounded-xl bg-white hover:bg-[#6f55ef]/10 text-[#6f55ef] border border-[#6f55ef]/25 text-[11px] font-[800] tracking-[1px] uppercase transition-all flex items-center gap-2 shadow-xs"
          >
            <Download className="w-4 h-4 text-[#6f55ef]" />
            Download Markdown
          </button>

          <div className="flex items-center gap-2.5">
            <button
              onClick={handlePrint}
              className="px-4 py-2.5 rounded-xl bg-white hover:bg-[#17132d]/5 text-[#17132d] border border-[#17132d]/15 text-[11px] font-[800] tracking-[1px] uppercase transition-all flex items-center gap-2 shadow-xs"
            >
              <Printer className="w-4 h-4" />
              Print
            </button>

            <button
              onClick={onClose}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#6f55ef] to-[#5136db] hover:from-[#5c3ee6] hover:to-[#4329cb] text-white text-[11px] font-[800] tracking-[1px] uppercase transition-all shadow-md shadow-[#6f55ef]/30"
            >
              Close
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
