import React, { useState } from 'react';
import { Database, Search, ArrowUpDown } from 'lucide-react';

export default function TransactionsTable({ transactions = [] }) {
  const [searchTerm, setSearchTerm] = useState('');

  const filtered = transactions.filter(t => 
    t.merchant.toLowerCase().includes(searchTerm.toLowerCase()) ||
    t.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
    t.transaction_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="my-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-1.5 h-1.5 rounded-full bg-[#6f55ef]"></div>
            <span className="text-[10px] font-[800] uppercase tracking-[2px] text-[#6f55ef]">
              Financial Ingestion Telemetry
            </span>
          </div>
          <h2 className="text-xl font-[900] text-[#17132d] flex items-center gap-2 tracking-tight">
            <Database className="w-5 h-5 text-[#6f55ef]" />
            Transaction Audit Feed
          </h2>
          <p className="text-xs text-[#17132d]/60 font-medium">
            Raw statement data ingested for automated cadence interval detection and clustering
          </p>
        </div>

        {/* VeriVision Search Box */}
        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 text-[#6f55ef] absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search merchant, category, or Tx..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-white/90 border border-purple-200/80 rounded-xl text-xs text-[#17132d] placeholder-slate-400 focus:outline-none focus:border-[#6f55ef] focus:ring-2 focus:ring-[#6f55ef]/20 shadow-[0_4px_16px_rgba(111,85,239,0.06)] transition-all font-medium"
          />
        </div>
      </div>

      <div className="veri-card overflow-hidden !p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#f8f6ff]/90 text-[#17132d] border-b border-purple-100 uppercase font-[800] text-[10px] tracking-[1.5px]">
              <tr>
                <th className="px-5 py-3.5">Tx ID</th>
                <th className="px-5 py-3.5">Date</th>
                <th className="px-5 py-3.5">Merchant</th>
                <th className="px-5 py-3.5">Category</th>
                <th className="px-5 py-3.5 text-right">Amount</th>
                <th className="px-5 py-3.5">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-purple-100/40 text-[#17132d]/80">
              {filtered.map((tx) => (
                <tr key={tx.transaction_id || tx.id} className="hover:bg-purple-50/50 transition-colors">
                  <td className="px-5 py-3 font-mono text-purple-700/80 font-bold text-[11px]">{tx.transaction_id}</td>
                  <td className="px-5 py-3 font-mono text-slate-500 font-medium">{tx.date}</td>
                  <td className="px-5 py-3 font-[800] text-[#17132d]">{tx.merchant}</td>
                  <td className="px-5 py-3">
                    <span className="px-2.5 py-0.5 rounded-lg bg-[#ede8ff] text-[#6f55ef] border border-purple-200/60 text-[10px] font-[800] uppercase tracking-wider">
                      {tx.category.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-right font-[900] text-[#17132d]">
                    {tx.currency}{tx.amount.toLocaleString()}
                  </td>
                  <td className="px-5 py-3 text-[#17132d]/60 max-w-xs truncate font-medium">{tx.description}</td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan="6" className="px-5 py-8 text-center text-xs text-[#17132d]/50 font-medium">
                    No transactions matching your query
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
