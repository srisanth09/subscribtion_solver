import React from 'react';
import { Mail, Calendar, Sparkles, TrendingUp, AlertTriangle } from 'lucide-react';

export default function EmailExplorer({ emails = [] }) {
  return (
    <div className="my-8">
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-1.5 h-1.5 rounded-full bg-[#6f55ef]"></div>
          <span className="text-[10px] font-[800] uppercase tracking-[2px] text-[#6f55ef]">
            NLP Email Signal Ingestion
          </span>
        </div>
        <h2 className="text-xl font-[900] text-[#17132d] flex items-center gap-2 tracking-tight">
          <Mail className="w-5 h-5 text-[#6f55ef]" />
          Scanned Billing & Subscription Signals
        </h2>
        <p className="text-xs text-[#17132d]/60 font-medium">
          Autonomous inbox telemetry for price-hike alerts, trial-to-paid conversions, and scheduled renewals
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {emails.map((email) => {
          const isPriceHike = email.event_type === 'price_hike';
          const isTrial = email.event_type?.includes('trial');

          return (
            <div 
              key={email.id}
              className={`veri-card flex flex-col justify-between transition-all duration-300 ${
                isPriceHike ? 'border-[#ff3c6e]/30 hover:border-[#ff3c6e]/60 hover:shadow-[0_16px_36px_rgba(255,60,110,0.12)]' : 
                isTrial ? 'border-[#6f55ef]/35' : ''
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className={`px-2.5 py-1 rounded-full text-[10px] font-[800] uppercase tracking-[1.2px] border ${
                    isPriceHike ? 'bg-[#ff3c6e]/10 text-[#ff3c6e] border-[#ff3c6e]/30' :
                    isTrial ? 'bg-[#6f55ef]/10 text-[#6f55ef] border-[#6f55ef]/30' :
                    'bg-[#17132d]/5 text-[#17132d]/70 border-purple-100'
                  }`}>
                    {email.event_type?.replace(/_/g, ' ')}
                  </span>
                  <span className="text-[11px] text-[#17132d]/50 font-mono font-medium">
                    {new Date(email.date).toLocaleDateString()}
                  </span>
                </div>

                <h4 className="text-sm font-[800] text-[#17132d] mb-1 leading-snug">{email.subject}</h4>
                <div className="text-xs text-[#17132d]/60 mb-3 font-medium">
                  Sender: <span className="font-mono text-[#6f55ef] font-bold">{email.sender}</span>
                </div>

                <div className="p-3.5 rounded-xl bg-[#f8f6ff]/80 border border-purple-100/70 text-xs text-[#17132d]/80 whitespace-pre-wrap leading-relaxed font-sans font-normal">
                  {email.body}
                </div>
              </div>

              {email.extracted_data && (
                <div className="mt-4 pt-3.5 border-t border-purple-100/60 flex items-center justify-between text-[11px] text-[#17132d]/60 font-medium">
                  <span>Merchant: <strong className="text-[#17132d] font-[800]">{email.extracted_data.merchant}</strong></span>
                  {email.extracted_data.percentage_increase && (
                    <span className="text-[#ff3c6e] font-[800] bg-[#ff3c6e]/10 px-2.5 py-0.5 rounded-full border border-[#ff3c6e]/30 text-[10px] uppercase tracking-wider">
                      +{email.extracted_data.percentage_increase}% Hike
                    </span>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
