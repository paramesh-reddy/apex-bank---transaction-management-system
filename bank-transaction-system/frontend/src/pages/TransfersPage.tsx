import React, { useEffect, useState } from 'react';
import { ArrowLeftRight, CheckCircle2 } from 'lucide-react';
import { transferService, Transfer } from '../services/transferService';
import { formatCurrency, formatDate } from '../utils/formatters';

interface TransfersPageProps {
  revision: number;
  onOpenTransfer: () => void;
}

export const TransfersPage: React.FC<TransfersPageProps> = ({ revision, onOpenTransfer }) => {
  const [transfers, setTransfers] = useState<Transfer[]>([]);
  const [loading, setLoading] = useState(true);

  const loadTransfers = async () => {
    try {
      setLoading(true);
      const items = await transferService.getTransfers(1, 50);
      setTransfers(items);
    } catch (err) {
      console.error('Error fetching transfers:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTransfers();
  }, [revision]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Money Transfers</h1>
          <p className="text-xs text-slate-500 mt-1">
            Atomic transfers executed with consistent row-locking order to prevent database deadlocks.
          </p>
        </div>
        <button
          onClick={onOpenTransfer}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white shadow-xs transition-colors self-start sm:self-auto"
        >
          <ArrowLeftRight className="w-4 h-4" /> Transfer Money
        </button>
      </div>

      {/* Transfer Ledger Explanation Box */}
      <div className="bg-blue-50/70 border border-blue-200 rounded-xl p-4 text-xs text-blue-900 space-y-1">
        <div className="font-semibold flex items-center gap-1.5">
          <CheckCircle2 className="w-4 h-4 text-blue-600" /> Two-Phase Row-Locking &amp; Atomicity Guarantee
        </div>
        <p className="text-blue-800 text-[11px] leading-relaxed">
          Transfers acquire PostgreSQL row locks in ascending UUID sequence, completely eliminating deadlock scenarios between concurrent opposing transfers. Each transfer generates both a debit transaction for the sender and a credit transaction for the recipient, committed atomically with the updated balances.
        </p>
      </div>

      {/* Transfers List */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        {loading ? (
          <div className="p-12 text-center text-slate-400 text-xs">Loading transfer history...</div>
        ) : transfers.length === 0 ? (
          <div className="p-12 text-center text-slate-400 text-xs">
            No transfers recorded yet. Click &ldquo;Transfer Money&rdquo; to execute an atomic inter-account transfer.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider">
                  <th className="py-3 px-4">Transfer Reference</th>
                  <th className="py-3 px-4">Amount</th>
                  <th className="py-3 px-4">Source Account ID</th>
                  <th className="py-3 px-4">Destination Account ID</th>
                  <th className="py-3 px-4">Note / Description</th>
                  <th className="py-3 px-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {transfers.map((trf) => (
                  <tr key={trf.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-semibold text-blue-700 whitespace-nowrap">
                      {trf.reference_id}
                    </td>
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-900 text-sm whitespace-nowrap">
                      {formatCurrency(trf.amount)}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-[11px] text-slate-500 whitespace-nowrap">
                      {trf.source_account_id.slice(0, 8)}...
                    </td>
                    <td className="py-3.5 px-4 font-mono text-[11px] text-slate-500 whitespace-nowrap">
                      {trf.destination_account_id.slice(0, 8)}...
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 max-w-xs truncate">
                      {trf.description || '—'}
                    </td>
                    <td className="py-3.5 px-4 text-slate-500 whitespace-nowrap">
                      {formatDate(trf.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
