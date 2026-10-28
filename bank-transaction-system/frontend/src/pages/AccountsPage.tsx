import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, Wallet, ChevronRight, Copy, Check } from 'lucide-react';
import { accountService, Account } from '../services/accountService';
import { formatCurrency, formatDate } from '../utils/formatters';

interface AccountsPageProps {
  revision: number;
  onOpenCreateAccount: () => void;
  onOpenTransaction: (type?: 'credit' | 'debit', accountId?: string) => void;
  onOpenTransfer: (sourceAccountId?: string) => void;
}

export const AccountsPage: React.FC<AccountsPageProps> = ({
  revision,
  onOpenCreateAccount,
  onOpenTransaction,
  onOpenTransfer,
}) => {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      const data = await accountService.getAccounts(0, 100);
      setAccounts(data.items);
    } catch (err) {
      console.error('Error fetching accounts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, [revision]);

  const handleCopy = (id: string) => {
    navigator.clipboard.writeText(id);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const filtered = accounts.filter(
    (acc) =>
      acc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      acc.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Bank Accounts</h1>
          <p className="text-xs text-slate-500 mt-1">
            Manage customer accounts, balances, and inspect immutable transaction records.
          </p>
        </div>
        <button
          onClick={onOpenCreateAccount}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white shadow-xs transition-colors self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" /> Create Account
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search accounts by name or UUID..."
            className="w-full pl-9 pr-4 py-2 text-xs rounded-xl border border-slate-300 bg-white focus:outline-hidden focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600"
          />
        </div>
      </div>

      {/* Accounts Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        {loading ? (
          <div className="p-12 text-center text-slate-400 text-xs">Loading accounts...</div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center text-slate-400 text-xs">
            {searchTerm ? 'No accounts matched your search criteria.' : 'No accounts available.'}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider">
                  <th className="py-3.5 px-4">Account Holder / Name</th>
                  <th className="py-3.5 px-4">Account UUID</th>
                  <th className="py-3.5 px-4">Current Balance</th>
                  <th className="py-3.5 px-4">Created Date</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.map((acc) => (
                  <tr key={acc.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <Link
                        to={`/accounts/${acc.id}`}
                        className="font-bold text-slate-900 hover:text-emerald-600 text-sm flex items-center gap-2"
                      >
                        <Wallet className="w-4 h-4 text-slate-400" />
                        {acc.name}
                      </Link>
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <div className="flex items-center gap-1.5 font-mono text-[11px] text-slate-500">
                        <span>{acc.id}</span>
                        <button
                          onClick={() => handleCopy(acc.id)}
                          className="text-slate-400 hover:text-slate-700"
                          title="Copy UUID"
                        >
                          {copiedId === acc.id ? (
                            <Check className="w-3.5 h-3.5 text-emerald-600" />
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                        </button>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span className="font-bold font-mono text-sm text-slate-900">
                        {formatCurrency(acc.balance)}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap text-slate-500">
                      {formatDate(acc.created_at)}
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap text-right">
                      <div className="inline-flex items-center gap-1.5">
                        <button
                          onClick={() => onOpenTransaction('credit', acc.id)}
                          className="px-2.5 py-1 rounded bg-emerald-50 text-emerald-700 hover:bg-emerald-100 font-semibold text-[11px] border border-emerald-200"
                        >
                          Deposit
                        </button>
                        <button
                          onClick={() => onOpenTransaction('debit', acc.id)}
                          className="px-2.5 py-1 rounded bg-amber-50 text-amber-700 hover:bg-amber-100 font-semibold text-[11px] border border-amber-200"
                        >
                          Withdraw
                        </button>
                        <button
                          onClick={() => onOpenTransfer(acc.id)}
                          className="px-2.5 py-1 rounded bg-blue-50 text-blue-700 hover:bg-blue-100 font-semibold text-[11px] border border-blue-200"
                        >
                          Transfer
                        </button>
                        <Link
                          to={`/accounts/${acc.id}`}
                          className="p-1 rounded text-slate-400 hover:text-slate-700"
                          title="View Account Details"
                        >
                          <ChevronRight className="w-4 h-4" />
                        </Link>
                      </div>
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
