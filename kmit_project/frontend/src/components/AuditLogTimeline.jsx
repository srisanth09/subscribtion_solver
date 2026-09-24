import React from 'react';
import { 
  History, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  ShieldAlert, 
  TrendingDown, 
  Clock, 
  ArrowRight 
} from 'lucide-react';

export default function AuditLogTimeline({ logs = [] }) {
  if (logs.length === 0) {
    return (
      <div className="bg-white border border-purple-100 rounded-2xl p-8 text-center my-6 shadow-xs">
        <Clock className="w-10 h-10 text-purple-400 mx-auto mb-3" />
        <h3 className="text-base font-bold text-slate-900">No Audit Records Yet</h3>
        <p className="text-xs text-slate-500 mt-1">
          Run a Guardian Audit to generate an immutable audit trail of decisions and savings.
        </p>
      </div>
    );
  }

  const getActionBadge = (type) => {
    switch (type) {
      case 'AUTO_CANCEL':
        return { label: 'Auto-Cancelled', bg: 'bg-rose-50 text-rose-700 border-rose-200', icon: <XCircle className="w-3.5 h-3.5" /> };
      case 'BLOCKED_GUARDRAIL':
        return { label: 'Guardrail Blocked', bg: 'bg-purple-50 text-purple-700 border-purple-200', icon: <ShieldAlert className="w-3.5 h-3.5" /> };
      case 'ESCALATE_APPROVAL':
        return { label: 'Escalated to Human', bg: 'bg-amber-50 text-amber-800 border-amber-300', icon: <AlertTriangle className="w-3.5 h-3.5 text-amber-600" /> };
      case 'USER_APPROVED_CANCEL':
        return { label: 'User Cancelled', bg: 'bg-emerald-50 text-emerald-700 border-emerald-200', icon: <CheckCircle className="w-3.5 h-3.5" /> };
      case 'NEGOTIATION_ACCEPTED':
        return { label: 'Discount Negotiated', bg: 'bg-indigo-50 text-indigo-700 border-indigo-200', icon: <TrendingDown className="w-3.5 h-3.5" /> };
      default:
        return { label: type, bg: 'bg-slate-100 text-slate-700 border-slate-200', icon: <History className="w-3.5 h-3.5 text-purple-600" /> };
    }
  };

  return (
    <div className="my-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <History className="w-5 h-5 text-purple-600" />
          <h2 className="text-lg font-extrabold text-slate-900">Autonomous Action & Audit Log</h2>
        </div>
        <span className="text-xs text-slate-500">
          Showing {logs.length} chronological audit events
        </span>
      </div>

      <div className="space-y-3">
        {logs.map((log) => {
          const badge = getActionBadge(log.action_type);
          const formattedDate = new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

          return (
            <div 
              key={log.id}
              className="p-4 rounded-xl bg-white border border-slate-200 hover:border-purple-300 shadow-xs hover:shadow-sm transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs text-slate-400 font-mono">{formattedDate}</span>
                  <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold border flex items-center gap-1 ${badge.bg}`}>
                    {badge.icon}
                    {badge.label}
                  </span>
                  <span className="text-sm font-extrabold text-slate-900">{log.merchant}</span>
                  {log.amount > 0 && (
                    <span className="text-xs text-slate-500 font-medium">
                      (₹{log.amount.toLocaleString()}/mo)
                    </span>
                  )}
                </div>

                <p className="text-xs text-slate-600 max-w-2xl leading-relaxed">
                  {log.reason}
                </p>

                <div className="flex items-center gap-3 text-[11px] text-slate-400">
                  <span>Waste: {log.waste_score}/100</span>
                  <span>•</span>
                  <span>Confidence: {(log.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>

              {log.monthly_saving > 0 && (
                <div className="text-left md:text-right shrink-0 bg-purple-50 border border-purple-100 px-3 py-1.5 rounded-lg shadow-xs">
                  <div className="text-[10px] uppercase font-bold text-purple-700">Monthly Saved</div>
                  <div className="text-base font-extrabold text-purple-900">
                    +₹{log.monthly_saving.toLocaleString()}/mo
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
