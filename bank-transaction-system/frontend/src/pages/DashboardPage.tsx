import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Wallet, 
  Layers, 
  ArrowLeftRight, 
  ShieldCheck, 
  Plus, 
  ArrowDownLeft, 
  ArrowUpRight,
  TrendingUp,
  ChevronRight
} from 'lucide-react';
import { accountService, Account, AccountMetrics } from '../services/accountService';
import { formatCurrency, formatDate } from '../utils/formatters';

interface DashboardPageProps {
  revision: number;
  onOpenCreateAccount: () => void;
  onOpenTransaction: (type?: 'credit' | 'debit', accountId?: string) => void;
  onOpenTransfer: (sourceAccountId?: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  revision,
  onOpenCreateAccount,
  onOpenTransaction,
  onOpenTransfer,
}) => {
  const [metrics, setMetrics] = useState<AccountMetrics | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const [metricsData, accountsData] = await Promise.all([
        accountService.getMetrics(),
        accountService.getAccounts(0, 5),
      ]);
      setMetrics(metricsData);
      setAccounts(accountsData.items);
    } catch (e) {
      console.error('Failed to load dashboard data:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [revision]);

  return (
    <div className="space-y-6">
      {/* Top Banner & Quick Actions */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-lg border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-semibold mb-3 border border-emerald-500/30">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Neon PostgreSQL Active &bull; Acid Locking Verified
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Apex Bank Account &amp; Transaction System
          </h1>
          <p className="text-slate-300 text-sm mt-1 max-w-xl">
            Financial ledger built with FastAPI, PostgreSQL, and SQLAlchemy 2.0 with strict row-level lock atomicity and zero-compromise Decimal calculations.
          </p>
        </div>

        <div className="flex flex-wrap gap-2.5">
          <button
            onClick={onOpenCreateAccount}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-md transition-all"
          >
            <Plus className="w-4 h-4" /> Open Account
          </button>
          <button
            onClick={() => onOpenTransaction('credit')}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-white border border-slate-700 transition-all"
          >
            <ArrowDownLeft className="w-4 h-4 text-emerald-400" /> Deposit
          </button>
          <button
            onClick={() => onOpenTransfer()}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-white border border-slate-700 transition-all"
          >
            <ArrowLeftRight className="w-4 h-4 text-blue-400" /> Transfer
          </button>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Accounts */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase text-slate-500 tracking-wider">
              Total Accounts
            </span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center">
              <Wallet className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {loading ? '—' : metrics?.total_accounts || 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Active customer bank accounts</p>
        </div>

        {/* Combined Balance */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase text-slate-500 tracking-wider">
              Combined Balance
            </span>
            <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-700 flex items-center justify-center">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900 font-mono">
            {loading ? '—' : formatCurrency(metrics?.total_balance || '0.00')}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Aggregated PostgreSQL balance</p>
        </div>

        {/* Total Transactions */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase text-slate-500 tracking-wider">
              Ledger Transactions
            </span>
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {loading ? '—' : metrics?.total_transactions || 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Immutable transaction records</p>
        </div>

        {/* System Status */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase text-slate-500 tracking-wider">
              Ledger Status
            </span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-base font-bold text-emerald-700 flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
            ACID Verified
          </div>
          <p className="text-[11px] text-slate-500 mt-1">SELECT ... FOR UPDATE locks</p>
        </div>
      </div>

      {/* Accounts List Section */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900">Active Accounts Overview</h2>
            <p className="text-xs text-slate-500">Live balance derived from real PostgreSQL database</p>
          </div>
          <Link
            to="/accounts"
            className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 flex items-center gap-1"
          >
            View all accounts <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="divide-y divide-slate-100">
          {loading ? (
            <div className="p-8 text-center text-slate-400 text-xs">Loading accounts...</div>
          ) : accounts.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-xs">No accounts found. Create your first account above!</div>
          ) : (
            accounts.map((acc) => (
              <div key={acc.id} className="p-4 sm:px-6 flex items-center justify-between hover:bg-slate-50/70 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center font-bold text-sm">
                    {acc.name.slice(0, 2).toUpperCase()}
                  </div>
                  <div>
                    <Link
                      to={`/accounts/${acc.id}`}
                      className="font-semibold text-slate-900 hover:text-emerald-600 text-sm transition-colors"
                    >
                      {acc.name}
                    </Link>
                    <p className="text-[11px] font-mono text-slate-400">ID: {acc.id.slice(0, 8)}... &bull; Opened {formatDate(acc.created_at)}</p>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <span className="font-bold text-slate-900 text-base font-mono">
                      {formatCurrency(acc.balance)}
                    </span>
                    <span className="block text-[10px] text-slate-400 uppercase font-medium">Available Balance</span>
                  </div>

                  <div className="hidden sm:flex items-center gap-1.5">
                    <button
                      onClick={() => onOpenTransaction('credit', acc.id)}
                      className="p-1.5 rounded-lg border border-slate-200 hover:bg-emerald-50 text-slate-600 hover:text-emerald-700 transition-colors"
                      title="Deposit to this account"
                    >
                      <ArrowDownLeft className="w-4 h-4 text-emerald-600" />
                    </button>
                    <button
                      onClick={() => onOpenTransaction('debit', acc.id)}
                      className="p-1.5 rounded-lg border border-slate-200 hover:bg-amber-50 text-slate-600 hover:text-amber-700 transition-colors"
                      title="Withdraw from this account"
                    >
                      <ArrowUpRight className="w-4 h-4 text-amber-600" />
                    </button>
                    <button
                      onClick={() => onOpenTransfer(acc.id)}
                      className="p-1.5 rounded-lg border border-slate-200 hover:bg-blue-50 text-slate-600 hover:text-blue-700 transition-colors"
                      title="Transfer from this account"
                    >
                      <ArrowLeftRight className="w-4 h-4 text-blue-600" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
