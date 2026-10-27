import React from 'react';
import { ArrowDownLeft, ArrowUpRight, Copy, Check, ArrowLeftRight } from 'lucide-react';
import { Transaction } from '../services/transactionService';
import { formatCurrency, formatDate } from '../utils/formatters';

interface TransactionTableProps {
  transactions: Transaction[];
  loading?: boolean;
  currentPage: number;
  pageSize: number;
  totalRecords: number;
  totalPages: number;
  onPageChange: (newPage: number) => void;
  onPageSizeChange?: (newSize: number) => void;
}

export const TransactionTable: React.FC<TransactionTableProps> = ({
  transactions,
  loading = false,
  currentPage,
  pageSize,
  totalRecords,
  totalPages,
  onPageChange,
  onPageSizeChange,
}) => {
  const [copiedId, setCopiedId] = React.useState<string | null>(null);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(text);
    setTimeout(() => setCopiedId(null), 2000);
  };

  if (loading) {
    return (
      <div className="p-8 text-center text-slate-500 text-sm">
        <div className="inline-block w-6 h-6 border-2 border-slate-300 border-t-emerald-600 rounded-full animate-spin mb-2" />
        <p>Loading transactions...</p>
      </div>
    );
  }

  if (transactions.length === 0) {
    return (
      <div className="p-12 text-center text-slate-400 text-sm bg-white rounded-xl border border-slate-200">
        <p className="font-medium text-slate-600 mb-1">No transactions recorded</p>
        <p className="text-xs text-slate-400">Transactions created will appear here in chronological latest-first order.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider">
              <th className="py-3 px-4">Type</th>
              <th className="py-3 px-4">Amount</th>
              <th className="py-3 px-4">Reference ID</th>
              <th className="py-3 px-4">Description</th>
              <th className="py-3 px-4">Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {transactions.map((tx) => {
              const isCredit = tx.type === 'credit';
              return (
                <tr key={tx.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span
                      className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold ${
                        isCredit
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : 'bg-amber-50 text-amber-700 border border-amber-200'
                      }`}
                    >
                      {isCredit ? (
                        <ArrowDownLeft className="w-3 h-3 text-emerald-600" />
                      ) : (
                        <ArrowUpRight className="w-3 h-3 text-amber-600" />
                      )}
                      {isCredit ? 'Credit (Deposit)' : 'Debit (Withdraw)'}
                    </span>
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span
                      className={`font-semibold font-mono text-sm ${
                        isCredit ? 'text-emerald-600' : 'text-slate-900'
                      }`}
                    >
                      {isCredit ? '+' : '-'}{formatCurrency(tx.amount)}
                    </span>
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    <div className="flex items-center gap-1.5 font-mono text-[11px] text-slate-700">
                      <span>{tx.reference_id}</span>
                      <button
                        onClick={() => handleCopy(tx.reference_id)}
                        className="text-slate-400 hover:text-slate-600"
                        title="Copy reference"
                      >
                        {copiedId === tx.reference_id ? (
                          <Check className="w-3 h-3 text-emerald-600" />
                        ) : (
                          <Copy className="w-3 h-3" />
                        )}
                      </button>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-slate-600 max-w-xs truncate">
                    <div className="flex items-center gap-1.5">
                      {tx.transfer_id && (
                        <span className="inline-flex items-center gap-0.5 text-[10px] text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded border border-blue-200 shrink-0">
                          <ArrowLeftRight className="w-2.5 h-2.5" /> Transfer
                        </span>
                      )}
                      <span>{tx.description || '—'}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap text-slate-500">
                    {formatDate(tx.created_at)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="p-4 bg-slate-50/70 border-t border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-600">
        <div className="flex items-center gap-3">
          <span>
            Showing <strong className="text-slate-900">{transactions.length}</strong> of{' '}
            <strong className="text-slate-900">{totalRecords}</strong> transactions
          </span>
          {onPageSizeChange && (
            <div className="flex items-center gap-1.5">
              <span>Per page:</span>
              <select
                value={pageSize}
                onChange={(e) => onPageSizeChange(Number(e.target.value))}
                className="px-2 py-1 rounded border border-slate-300 text-xs bg-white"
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </div>
          )}
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage <= 1}
            className="px-3 py-1.5 rounded border border-slate-300 bg-white hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed font-medium"
          >
            Previous
          </button>
          <span className="px-2">
            Page {currentPage} of {totalPages || 1}
          </span>
          <button
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage >= totalPages}
            className="px-3 py-1.5 rounded border border-slate-300 bg-white hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed font-medium"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
};
