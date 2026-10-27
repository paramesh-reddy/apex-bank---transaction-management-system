import os
import shutil

os.makedirs('src/utils', exist_ok=True)
os.makedirs('src/components', exist_ok=True)
os.makedirs('src/pages', exist_ok=True)
os.makedirs('src/services', exist_ok=True)

# 1. formatters.ts
with open('src/utils/formatters.ts', 'w') as f:
    f.write('''export function formatCurrency(amount: string | number): string {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  if (isNaN(num)) return '$0.00';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num);
}

export function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  } catch {
    return dateString;
  }
}

export function formatRelativeTime(dateString: string): string {
  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffSec = Math.floor((now.getTime() - date.getTime()) / 1000);
    if (diffSec < 60) return 'Just now';
    if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
    if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
    return `${Math.floor(diffSec / 86400)}d ago`;
  } catch {
    return dateString;
  }
}

export function generateReference(prefix = 'REF'): string {
  const timestamp = Date.now().toString(36).toUpperCase();
  const random = Math.random().toString(36).substring(2, 6).toUpperCase();
  return `${prefix}-${timestamp}-${random}`;
}
''')

# 2. Sidebar.tsx
with open('src/components/Sidebar.tsx', 'w') as f:
    f.write('''import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Wallet, ArrowLeftRight, FileText, Database, ShieldCheck, Building2 } from 'lucide-react';

interface SidebarProps {
  mobileOpen?: boolean;
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ mobileOpen, onCloseMobile }) => {
  const items = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/accounts', label: 'Accounts', icon: Wallet },
    { to: '/transfers', label: 'Transfers', icon: ArrowLeftRight },
    { to: '/docs-info', label: 'API Specs', icon: FileText },
  ];

  const content = (
    <div className="flex flex-col h-full bg-slate-900 text-slate-200 border-r border-slate-800">
      <div className="p-6 border-b border-slate-800 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center text-white shadow-lg">
          <Building2 className="w-6 h-6" />
        </div>
        <div>
          <h1 className="font-bold text-lg text-white tracking-tight">Apex Bank</h1>
          <p className="text-xs text-slate-400 font-medium">Core Banking System</p>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1.5">
        <div className="px-3 pb-2 text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
          Menu
        </div>
        {items.map((it) => (
          <NavLink
            key={it.to}
            to={it.to}
            onClick={onCloseMobile}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 shadow-xs'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
              }`
            }
          >
            <it.icon className="w-4 h-4 shrink-0" />
            <span>{it.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-slate-800 bg-slate-950/60">
        <div className="p-3 rounded-lg bg-slate-800/60 border border-slate-700/50 text-xs">
          <div className="flex items-center justify-between text-slate-200 mb-1.5">
            <span className="flex items-center gap-1.5 font-medium">
              <Database className="w-3.5 h-3.5 text-emerald-400" /> Neon PG
            </span>
            <span className="text-[10px] text-emerald-400 bg-emerald-950 px-1.5 py-0.5 rounded border border-emerald-800">
              Connected
            </span>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Atomic locking with <code className="text-emerald-300">FOR UPDATE</code>.
          </p>
        </div>
        <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400">
          <span className="flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Append-only
          </span>
          <a
            href="/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="text-emerald-400 hover:underline font-medium"
          >
            Swagger UI &rarr;
          </a>
        </div>
      </div>
    </div>
  );

  return (
    <>
      <aside className="hidden md:block w-64 h-screen sticky top-0 shrink-0">
        {content}
      </aside>
      {mobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex">
          <div className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm" onClick={onCloseMobile} />
          <div className="relative w-72 max-w-[80vw] h-full shadow-2xl z-10">
            {content}
          </div>
        </div>
      )}
    </>
  );
};
''')

# 3. Navbar.tsx
with open('src/components/Navbar.tsx', 'w') as f:
    f.write('''import React from 'react';
import { Menu, Plus, ArrowUpRight, ArrowDownLeft, ArrowLeftRight } from 'lucide-react';

interface NavbarProps {
  onOpenMobileSidebar: () => void;
  onOpenCreateAccount: () => void;
  onOpenTransaction: (type?: 'credit' | 'debit') => void;
  onOpenTransfer: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenMobileSidebar,
  onOpenCreateAccount,
  onOpenTransaction,
  onOpenTransfer,
}) => {
  return (
    <header className="sticky top-0 z-30 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-4 sm:px-8 py-3.5 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMobileSidebar}
          className="md:hidden p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
          aria-label="Toggle menu"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div>
          <h2 className="text-sm font-semibold text-slate-900 dark:text-white hidden sm:block">
            Apex Financial Dashboard
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 hidden sm:block">
            Full-Stack Assessment &bull; Neon PostgreSQL &bull; FastAPI
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={() => onOpenTransaction('credit')}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100 transition-colors shadow-xs"
        >
          <ArrowDownLeft className="w-3.5 h-3.5 text-emerald-600" />
          <span>Deposit</span>
        </button>

        <button
          onClick={() => onOpenTransaction('debit')}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200 hover:bg-amber-100 transition-colors shadow-xs"
        >
          <ArrowUpRight className="w-3.5 h-3.5 text-amber-600" />
          <span>Withdraw</span>
        </button>

        <button
          onClick={onOpenTransfer}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 transition-colors shadow-xs"
        >
          <ArrowLeftRight className="w-3.5 h-3.5 text-blue-600" />
          <span>Transfer</span>
        </button>

        <button
          onClick={onOpenCreateAccount}
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 text-white hover:bg-slate-800 transition-colors shadow-sm"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Account</span>
        </button>
      </div>
    </header>
  );
};
''')

# 4. CreateAccountModal.tsx
with open('src/components/CreateAccountModal.tsx', 'w') as f:
    f.write('''import React, { useState } from 'react';
import { X, Building2, AlertCircle } from 'lucide-react';
import { accountService } from '../services/accountService';
import { parseApiError } from '../services/api';

interface CreateAccountModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (newAccount: any) => void;
}

export const CreateAccountModal: React.FC<CreateAccountModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Account name is required and cannot be empty.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const created = await accountService.createAccount(name.trim());
      setName('');
      onSuccess(created);
      onClose();
    } catch (err) {
      const parsed = parseApiError(err);
      setError(parsed.message || 'Failed to create account.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs">
      <div className="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between p-5 border-b border-slate-100 bg-slate-50/50">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center">
              <Building2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 text-base">Create New Account</h3>
              <p className="text-xs text-slate-500">Opens with initial balance of $0.00</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          {error && (
            <div className="p-3 rounded-lg bg-red-50 border border-red-200 flex items-start gap-2 text-xs text-red-700">
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Account Holder / Business Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              required
              autoFocus
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Acme Corp Operating Account"
              className="w-full px-3.5 py-2.5 text-sm rounded-lg border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 transition-colors"
            />
            <p className="text-[11px] text-slate-400 mt-1">
              Must be non-empty string. Balances are tracked via arbitrary-precision Decimal.
            </p>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-600 space-y-1">
            <div className="flex justify-between">
              <span className="text-slate-500">Initial Balance:</span>
              <span className="font-semibold text-slate-900">$0.00 (Fixed)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Currency:</span>
              <span className="font-medium text-slate-700">USD ($)</span>
            </div>
          </div>

          <div className="flex items-center justify-end gap-2.5 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !name.trim()}
              className="px-4 py-2 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 rounded-lg shadow-xs transition-colors"
            >
              {loading ? 'Creating...' : 'Open Account'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
''')

# 5. TransactionModal.tsx
with open('src/components/TransactionModal.tsx', 'w') as f:
    f.write('''import React, { useState, useEffect } from 'react';
import { X, ArrowDownLeft, ArrowUpRight, AlertCircle, RefreshCw } from 'lucide-react';
import { Account } from '../services/accountService';
import { transactionService } from '../services/transactionService';
import { generateReference, formatCurrency } from '../utils/formatters';
import { parseApiError } from '../services/api';

interface TransactionModalProps {
  isOpen: boolean;
  initialType?: 'credit' | 'debit';
  initialAccountId?: string;
  accounts: Account[];
  onClose: () => void;
  onSuccess: (data: any) => void;
}

export const TransactionModal: React.FC<TransactionModalProps> = ({
  isOpen,
  initialType = 'credit',
  initialAccountId,
  accounts,
  onClose,
  onSuccess,
}) => {
  const [type, setType] = useState<'credit' | 'debit'>(initialType);
  const [accountId, setAccountId] = useState(initialAccountId || '');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [referenceId, setReferenceId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      setType(initialType);
      if (initialAccountId) {
        setAccountId(initialAccountId);
      } else if (accounts.length > 0 && !accountId) {
        setAccountId(accounts[0].id);
      }
      setReferenceId(generateReference(initialType === 'credit' ? 'DEP' : 'WTH'));
      setAmount('');
      setDescription('');
      setError(null);
    }
  }, [isOpen, initialType, initialAccountId, accounts]);

  if (!isOpen) return null;

  const selectedAccount = accounts.find((a) => a.id === accountId);
  const currentBalance = selectedAccount ? parseFloat(selectedAccount.balance) : 0;

  const handleRegenerateReference = () => {
    setReferenceId(generateReference(type === 'credit' ? 'DEP' : 'WTH'));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accountId) {
      setError('Please select an account.');
      return;
    }
    const numAmount = parseFloat(amount);
    if (isNaN(numAmount) || numAmount <= 0) {
      setError('Amount must be a positive number greater than 0.');
      return;
    }
    if (type === 'debit' && numAmount > currentBalance) {
      setError(`Insufficient balance. Current balance is ${formatCurrency(currentBalance)}, cannot withdraw ${formatCurrency(numAmount)}.`);
      return;
    }
    if (!referenceId.trim()) {
      setError('Reference ID is required.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const res = await transactionService.createTransaction(accountId, {
        type,
        amount: numAmount.toFixed(2),
        description: description.trim() || undefined,
        reference_id: referenceId.trim(),
      });
      onSuccess(res);
      onClose();
    } catch (err) {
      const parsed = parseApiError(err);
      setError(parsed.message || 'Transaction failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs">
      <div className="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-lg overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between p-5 border-b border-slate-100 bg-slate-50/50">
          <div className="flex items-center gap-2.5">
            <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${
              type === 'credit' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
            }`}>
              {type === 'credit' ? <ArrowDownLeft className="w-5 h-5" /> : <ArrowUpRight className="w-5 h-5" />}
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 text-base">
                {type === 'credit' ? 'Deposit Funds (Credit)' : 'Withdraw Funds (Debit)'}
              </h3>
              <p className="text-xs text-slate-500">Atomic balance update with row locking</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          {error && (
            <div className="p-3 rounded-lg bg-red-50 border border-red-200 flex items-start gap-2 text-xs text-red-700">
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Type Switcher */}
          <div className="grid grid-cols-2 gap-2 p-1 bg-slate-100 rounded-lg text-xs font-semibold">
            <button
              type="button"
              onClick={() => {
                setType('credit');
                setReferenceId(generateReference('DEP'));
              }}
              className={`py-2 rounded-md transition-all ${
                type === 'credit' ? 'bg-white text-emerald-700 shadow-xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Deposit (Credit)
            </button>
            <button
              type="button"
              onClick={() => {
                setType('debit');
                setReferenceId(generateReference('WTH'));
              }}
              className={`py-2 rounded-md transition-all ${
                type === 'debit' ? 'bg-white text-amber-700 shadow-xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Withdraw (Debit)
            </button>
          </div>

          {/* Account Selection */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Target Account <span className="text-red-500">*</span>
            </label>
            <select
              required
              value={accountId}
              onChange={(e) => setAccountId(e.target.value)}
              className="w-full px-3.5 py-2 text-sm rounded-lg border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600"
            >
              <option value="" disabled>Select an account</option>
              {accounts.map((acc) => (
                <option key={acc.id} value={acc.id}>
                  {acc.name} — Balance: {formatCurrency(acc.balance)}
                </option>
              ))}
            </select>
            {selectedAccount && (
              <p className="text-[11px] text-slate-500 mt-1">
                Available balance: <strong className="text-slate-800">{formatCurrency(selectedAccount.balance)}</strong>
              </p>
            )}
          </div>

          {/* Amount Input */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Amount ($) <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 font-semibold">$</span>
              <input
                type="number"
                step="0.01"
                min="0.01"
                required
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="0.00"
                className="w-full pl-8 pr-3.5 py-2 text-sm rounded-lg border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 font-mono"
              />
            </div>
            {/* Quick Amount Buttons */}
            <div className="flex gap-1.5 mt-2">
              {[25, 50, 100, 250, 500].map((val) => (
                <button
                  key={val}
                  type="button"
                  onClick={() => setAmount(val.toFixed(2))}
                  className="px-2.5 py-1 text-[11px] font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 rounded transition-colors"
                >
                  +${val}
                </button>
              ))}
              {type === 'debit' && selectedAccount && currentBalance > 0 && (
                <button
                  type="button"
                  onClick={() => setAmount(currentBalance.toFixed(2))}
                  className="px-2.5 py-1 text-[11px] font-semibold bg-amber-100 hover:bg-amber-200 text-amber-800 rounded transition-colors ml-auto"
                >
                  All (${currentBalance.toFixed(2)})
                </button>
              )}
            </div>
          </div>

          {/* Reference ID */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-semibold text-slate-700">
                Reference ID <span className="text-red-500">*</span>
              </label>
              <button
                type="button"
                onClick={handleRegenerateReference}
                className="text-[11px] text-emerald-600 hover:text-emerald-700 flex items-center gap-1"
              >
                <RefreshCw className="w-3 h-3" /> Auto-generate
              </button>
            </div>
            <input
              type="text"
              required
              value={referenceId}
              onChange={(e) => setReferenceId(e.target.value)}
              placeholder="e.g. REF-2026-X19"
              className="w-full px-3.5 py-2 text-sm font-mono rounded-lg border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600"
            />
            <p className="text-[11px] text-slate-400 mt-1">
              Enforced unique per account via database constraint.
            </p>
          </div>

          {/* Optional Description */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Description (Optional)
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g. Monthly payroll, invoice payment"
              className="w-full px-3.5 py-2 text-sm rounded-lg border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600"
            />
          </div>

          <div className="flex items-center justify-end gap-2.5 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !amount || !referenceId}
              className={`px-5 py-2 text-xs font-semibold text-white rounded-lg shadow-xs transition-colors disabled:opacity-50 ${
                type === 'credit' ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-amber-600 hover:bg-amber-700'
              }`}
            >
              {loading ? 'Processing...' : type === 'credit' ? 'Execute Deposit' : 'Execute Withdrawal'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
''')

# 6. TransferModal.tsx
with open('src/components/TransferModal.tsx', 'w') as f:
    f.write('''import React, { useState, useEffect } from 'react';
import { X, ArrowLeftRight, AlertCircle, RefreshCw, CheckCircle2 } from 'lucide-react';
import { Account } from '../services/accountService';
import { transferService } from '../services/transferService';
import { generateReference, formatCurrency } from '../utils/formatters';
import { parseApiError } from '../services/api';

interface TransferModalProps {
  isOpen: boolean;
  initialSourceAccountId?: string;
  accounts: Account[];
  onClose: () => void;
  onSuccess: (data: any) => void;
}

export const TransferModal: React.FC<TransferModalProps> = ({
  isOpen,
  initialSourceAccountId,
  accounts,
  onClose,
  onSuccess,
}) => {
  const [sourceId, setSourceId] = useState(initialSourceAccountId || '');
  const [destId, setDestId] = useState('');
  const [amount, setAmount] = useState('');
  const [referenceId, setReferenceId] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      if (initialSourceAccountId) {
        setSourceId(initialSourceAccountId);
        const other = accounts.find((a) => a.id !== initialSourceAccountId);
        setDestId(other ? other.id : '');
      } else if (accounts.length >= 2) {
        setSourceId(accounts[0].id);
        setDestId(accounts[1].id);
      }
      setReferenceId(generateReference('TRF'));
      setAmount('');
      setDescription('');
      setConfirming(false);
      setError(null);
    }
  }, [isOpen, initialSourceAccountId, accounts]);

  if (!isOpen) return null;

  const sourceAccount = accounts.find((a) => a.id === sourceId);
  const destAccount = accounts.find((a) => a.id === destId);
  const sourceBalance = sourceAccount ? parseFloat(sourceAccount.balance) : 0;
  const numAmount = parseFloat(amount) || 0;

  const handleProceedToConfirm = (e: React.FormEvent) => {
    e.preventDefault();
    if (!sourceId || !destId) {
      setError('Please select both source and destination accounts.');
      return;
    }
    if (sourceId === destId) {
      setError('Source and destination accounts must be different.');
      return;
    }
    if (isNaN(numAmount) || numAmount <= 0) {
      setError('Amount must be greater than zero.');
      return;
    }
    if (numAmount > sourceBalance) {
      setError(`Insufficient funds in ${sourceAccount?.name}. Available: ${formatCurrency(sourceBalance)}, Transfer requested: ${formatCurrency(numAmount)}.`);
      return;
    }
    if (!referenceId.trim()) {
      setError('Transfer reference ID is required.');
      return;
    }
    setError(null);
    setConfirming(true);
  };

  const handleExecuteTransfer = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await transferService.createTransfer({
        source_account_id: sourceId,
        destination_account_id: destId,
        amount: numAmount.toFixed(2),
        reference_id: referenceId.trim(),
        description: description.trim() || undefined,
      });
      onSuccess(res);
      onClose();
    } catch (err) {
      const parsed = parseApiError(err);
      setError(parsed.message || 'Transfer failed.');
      setConfirming(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs">
      <div className="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-lg overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between p-5 border-b border-slate-100 bg-slate-50/50">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center">
              <ArrowLeftRight className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 text-base">Transfer Money Between Accounts</h3>
              <p className="text-xs text-slate-500">Atomic ledger settlement with deadlock prevention</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100">
            <X className="w-5 h-5" />
          </button>
        </div>

        {confirming ? (
          <div className="p-5 space-y-4">
            <div className="p-4 rounded-xl bg-blue-50/70 border border-blue-200 text-xs space-y-3">
              <div className="font-semibold text-blue-900 text-sm flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-blue-600" /> Confirm Money Transfer
              </div>

              <div className="grid grid-cols-2 gap-3 pt-1 text-slate-700">
                <div className="p-2.5 bg-white rounded-lg border border-blue-100">
                  <span className="text-[11px] text-slate-400 block font-medium">From (Source)</span>
                  <span className="font-semibold text-slate-900 block truncate">{sourceAccount?.name}</span>
                  <span className="text-[11px] text-slate-500">New balance: {formatCurrency(sourceBalance - numAmount)}</span>
                </div>
                <div className="p-2.5 bg-white rounded-lg border border-blue-100">
                  <span className="text-[11px] text-slate-400 block font-medium">To (Destination)</span>
                  <span className="font-semibold text-slate-900 block truncate">{destAccount?.name}</span>
                  <span className="text-[11px] text-slate-500">
                    New balance: {formatCurrency((parseFloat(destAccount?.balance || '0')) + numAmount)}
                  </span>
                </div>
              </div>

              <div className="border-t border-blue-200/60 pt-2 flex justify-between items-center text-xs">
                <span className="text-slate-500">Amount to Transfer:</span>
                <span className="text-base font-bold text-blue-900 font-mono">{formatCurrency(numAmount)}</span>
              </div>
              <div className="flex justify-between items-center text-[11px] text-slate-500">
                <span>Reference:</span>
                <span className="font-mono text-slate-800">{referenceId}</span>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-2">
              <button
                type="button"
                onClick={() => setConfirming(false)}
                disabled={loading}
                className="px-4 py-2 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
              >
                Back to Edit
              </button>
              <button
                type="button"
                onClick={handleExecuteTransfer}
                disabled={loading}
                className="px-5 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-xs disabled:opacity-50"
              >
                {loading ? 'Executing Transfer...' : 'Confirm & Commit Transfer'}
              </button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleProceedToConfirm} className="p-5 space-y-4">
            {error && (
              <div className="p-3 rounded-lg bg-red-50 border border-red-200 flex items-start gap-2 text-xs text-red-700">
                <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            {/* Source Account */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Source Account (From) <span className="text-red-500">*</span>
              </label>
              <select
                required
                value={sourceId}
                onChange={(e) => setSourceId(e.target.value)}
                className="w-full px-3.5 py-2 text-sm rounded-lg border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600"
              >
                <option value="" disabled>Select sender account</option>
                {accounts.map((acc) => (
                  <option key={acc.id} value={acc.id}>
                    {acc.name} — Balance: {formatCurrency(acc.balance)}
                  </option>
                ))}
              </select>
              {sourceAccount && (
                <p className="text-[11px] text-slate-500 mt-1">
                  Available funds: <strong className="text-slate-800">{formatCurrency(sourceAccount.balance)}</strong>
                </p>
              )}
            </div>

            {/* Destination Account */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Destination Account (To) <span className="text-red-500">*</span>
              </label>
              <select
                required
                value={destId}
                onChange={(e) => setDestId(e.target.value)}
                className="w-full px-3.5 py-2 text-sm rounded-lg border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600"
              >
                <option value="" disabled>Select recipient account</option>
                {accounts
                  .filter((acc) => acc.id !== sourceId)
                  .map((acc) => (
                    <option key={acc.id} value={acc.id}>
                      {acc.name} — Balance: {formatCurrency(acc.balance)}
                    </option>
                  ))}
              </select>
            </div>

            {/* Amount */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Transfer Amount ($) <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 font-semibold">$</span>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  required
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="0.00"
                  className="w-full pl-8 pr-3.5 py-2 text-sm rounded-lg border border-slate-300 font-mono focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600"
                />
              </div>
            </div>

            {/* Reference */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-semibold text-slate-700">
                  Transfer Reference <span className="text-red-500">*</span>
                </label>
                <button
                  type="button"
                  onClick={() => setReferenceId(generateReference('TRF'))}
                  className="text-[11px] text-blue-600 hover:text-blue-700 flex items-center gap-1"
                >
                  <RefreshCw className="w-3 h-3" /> Auto-generate
                </button>
              </div>
              <input
                type="text"
                required
                value={referenceId}
                onChange={(e) => setReferenceId(e.target.value)}
                placeholder="e.g. TRF-2026-X81"
                className="w-full px-3.5 py-2 text-sm font-mono rounded-lg border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600"
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Note / Description (Optional)
              </label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="e.g. Supplier payment or inter-account transfer"
                className="w-full px-3.5 py-2 text-sm rounded-lg border border-slate-300 focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600"
              />
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={!amount || !sourceId || !destId || !referenceId}
                className="px-5 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-xs disabled:opacity-50"
              >
                Review Transfer
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
''')

# 7. TransactionTable.tsx
with open('src/components/TransactionTable.tsx', 'w') as f:
    f.write('''import React from 'react';
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
''')

# 8. DashboardPage.tsx
with open('src/pages/DashboardPage.tsx', 'w') as f:
    f.write('''import React, { useEffect, useState } from 'react';
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
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import { accountService, Account, AccountMetrics } from '../services/accountService';
import { formatCurrency, formatDate } from '../utils/formatters';

interface DashboardPageProps {
  onOpenCreateAccount: () => void;
  onOpenTransaction: (type?: 'credit' | 'debit', accountId?: string) => void;
  onOpenTransfer: (sourceAccountId?: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
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
  }, []);

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
''')

# 9. AccountsPage.tsx
with open('src/pages/AccountsPage.tsx', 'w') as f:
    f.write('''import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, Wallet, ArrowDownLeft, ArrowUpRight, ArrowLeftRight, ChevronRight, Copy, Check } from 'lucide-react';
import { accountService, Account } from '../services/accountService';
import { formatCurrency, formatDate } from '../utils/formatters';

interface AccountsPageProps {
  onOpenCreateAccount: () => void;
  onOpenTransaction: (type?: 'credit' | 'debit', accountId?: string) => void;
  onOpenTransfer: (sourceAccountId?: string) => void;
}

export const AccountsPage: React.FC<AccountsPageProps> = ({
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
  }, []);

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
''')

# 10. AccountDetailsPage.tsx
with open('src/pages/AccountDetailsPage.tsx', 'w') as f:
    f.write('''import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Wallet, 
  ArrowDownLeft, 
  ArrowUpRight, 
  ArrowLeftRight, 
  Copy, 
  Check, 
  AlertCircle,
  Calendar,
  ShieldCheck
} from 'lucide-react';
import { accountService, Account } from '../services/accountService';
import { transactionService, Transaction } from '../services/transactionService';
import { TransactionTable } from '../components/TransactionTable';
import { formatCurrency, formatDate } from '../utils/formatters';

interface AccountDetailsPageProps {
  onOpenTransaction: (type?: 'credit' | 'debit', accountId?: string) => void;
  onOpenTransfer: (sourceAccountId?: string) => void;
}

export const AccountDetailsPage: React.FC<AccountDetailsPageProps> = ({
  onOpenTransaction,
  onOpenTransfer,
}) => {
  const { accountId } = useParams<{ accountId: string }>();
  const [account, setAccount] = useState<Account | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [txLoading, setTxLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  // Pagination state
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalRecords, setTotalRecords] = useState(0);
  const [totalPages, setTotalPages] = useState(1);

  const fetchAccount = async () => {
    if (!accountId) return;
    try {
      setLoading(true);
      setError(null);
      const acc = await accountService.getAccount(accountId);
      setAccount(acc);
    } catch (err: any) {
      setError('Account not found or invalid UUID.');
    } finally {
      setLoading(false);
    }
  };

  const fetchTransactions = async () => {
    if (!accountId) return;
    try {
      setTxLoading(true);
      const res = await transactionService.getAccountTransactions(accountId, page, pageSize);
      setTransactions(res.items);
      setTotalRecords(res.total_records);
      setTotalPages(res.total_pages);
    } catch (err) {
      console.error('Error fetching transactions:', err);
    } finally {
      setTxLoading(false);
    }
  };

  useEffect(() => {
    fetchAccount();
  }, [accountId]);

  useEffect(() => {
    fetchTransactions();
  }, [accountId, page, pageSize]);

  const handleCopy = () => {
    if (accountId) {
      navigator.clipboard.writeText(accountId);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return <div className="p-12 text-center text-slate-400 text-sm">Loading account details...</div>;
  }

  if (error || !account) {
    return (
      <div className="p-8 bg-red-50 rounded-2xl border border-red-200 text-red-700 text-center space-y-3">
        <AlertCircle className="w-8 h-8 mx-auto text-red-600" />
        <h2 className="text-base font-bold">Account Not Found</h2>
        <p className="text-xs text-red-600 max-w-md mx-auto">{error || 'No account matching this identifier exists.'}</p>
        <Link to="/accounts" className="inline-flex items-center gap-1.5 text-xs font-semibold text-red-700 hover:underline">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Accounts list
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back button */}
      <Link
        to="/accounts"
        className="inline-flex items-center gap-1 text-xs font-semibold text-slate-500 hover:text-slate-800 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Accounts
      </Link>

      {/* Account Hero Card */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center">
              <Wallet className="w-4 h-4" />
            </span>
            <h1 className="text-2xl font-bold text-slate-900">{account.name}</h1>
          </div>
          <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
            <div className="flex items-center gap-1 font-mono bg-slate-100 px-2 py-0.5 rounded">
              <span>{account.id}</span>
              <button onClick={handleCopy} className="text-slate-400 hover:text-slate-700" title="Copy UUID">
                {copied ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
              </button>
            </div>
            <span className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5 text-slate-400" /> Opened {formatDate(account.created_at)}
            </span>
            <span className="flex items-center gap-1 text-emerald-700 font-medium">
              <ShieldCheck className="w-3.5 h-3.5" /> Append-only Ledger
            </span>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 w-full md:w-auto">
          <div className="bg-slate-50 border border-slate-200 rounded-xl px-5 py-3 w-full sm:w-auto">
            <span className="text-[11px] font-semibold uppercase text-slate-500 tracking-wider block">
              Current Authoritative Balance
            </span>
            <span className="text-3xl font-extrabold text-slate-900 font-mono">
              {formatCurrency(account.balance)}
            </span>
          </div>

          <div className="flex sm:flex-col gap-2 w-full sm:w-auto">
            <button
              onClick={() => onOpenTransaction('credit', account.id)}
              className="flex-1 sm:flex-none inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold bg-emerald-600 text-white hover:bg-emerald-700 transition-colors shadow-xs"
            >
              <ArrowDownLeft className="w-3.5 h-3.5" /> Deposit
            </button>
            <button
              onClick={() => onOpenTransaction('debit', account.id)}
              className="flex-1 sm:flex-none inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold bg-amber-600 text-white hover:bg-amber-700 transition-colors shadow-xs"
            >
              <ArrowUpRight className="w-3.5 h-3.5" /> Withdraw
            </button>
            <button
              onClick={() => onOpenTransfer(account.id)}
              className="flex-1 sm:flex-none inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold bg-blue-600 text-white hover:bg-blue-700 transition-colors shadow-xs"
            >
              <ArrowLeftRight className="w-3.5 h-3.5" /> Transfer
            </button>
          </div>
        </div>
      </div>

      {/* Transaction History Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900">Transaction History</h2>
            <p className="text-xs text-slate-500">
              Paginated transactions ordered by <code className="text-slate-800 font-mono">created_at DESC, id DESC</code>.
            </p>
          </div>
        </div>

        <TransactionTable
          transactions={transactions}
          loading={txLoading}
          currentPage={page}
          pageSize={pageSize}
          totalRecords={totalRecords}
          totalPages={totalPages}
          onPageChange={(p) => setPage(p)}
          onPageSizeChange={(s) => {
            setPageSize(s);
            setPage(1);
          }}
        />
      </div>
    </div>
  );
};
''')

# 11. TransfersPage.tsx
with open('src/pages/TransfersPage.tsx', 'w') as f:
    f.write('''import React, { useEffect, useState } from 'react';
import { ArrowLeftRight, CheckCircle2, ShieldAlert, Plus, Calendar, FileText } from 'lucide-react';
import { transferService, Transfer } from '../services/transferService';
import { formatCurrency, formatDate } from '../utils/formatters';

interface TransfersPageProps {
  onOpenTransfer: () => void;
}

export const TransfersPage: React.FC<TransfersPageProps> = ({ onOpenTransfer }) => {
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
  }, []);

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
''')

# 12. DocsPage.tsx
with open('src/pages/DocsPage.tsx', 'w') as f:
    f.write('''import React from 'react';
import { ExternalLink, Database, ShieldCheck, CheckCircle2, Code2, Server } from 'lucide-react';

export const DocsPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">API Documentation &amp; Architecture Specs</h1>
        <p className="text-xs text-slate-500 mt-1">
          Full-Stack Developer Assessment specifications, transaction atomicity guarantees, and API endpoints.
        </p>
      </div>

      <div className="p-5 rounded-2xl bg-emerald-950 text-white border border-emerald-800 flex items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold">FastAPI Interactive Swagger Documentation</h2>
          <p className="text-xs text-emerald-200 mt-1">
            Explore and test live REST endpoints directly with interactive OpenAPI schema validation.
          </p>
        </div>
        <a
          href="/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-emerald-400 hover:bg-emerald-300 text-slate-950 transition-colors shadow-sm shrink-0"
        >
          Open Swagger UI <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-5 rounded-xl bg-white border border-slate-200 space-y-3">
          <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
            <ShieldCheck className="w-4 h-4 text-emerald-600" /> Atomicity &amp; Pessimistic Locking
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Every transaction runs inside a dedicated SQLAlchemy session. Balance verification and balance updates are protected with <code className="bg-slate-100 text-slate-800 px-1 py-0.5 rounded font-mono">SELECT ... FOR UPDATE</code>. If any validation or unique constraint check fails, the session is rolled back completely.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-white border border-slate-200 space-y-3">
          <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
            <Code2 className="w-4 h-4 text-blue-600" /> Arbitrary-Precision Financial Math
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Floating-point arithmetic is strictly prohibited in financial backend services. All calculations use Python&apos;s <code className="bg-slate-100 text-slate-800 px-1 py-0.5 rounded font-mono">Decimal</code> and PostgreSQL <code className="bg-slate-100 text-slate-800 px-1 py-0.5 rounded font-mono">NUMERIC(18,2)</code> to eliminate round-off anomalies.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-white border border-slate-200 space-y-3">
          <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
            <Server className="w-4 h-4 text-purple-600" /> Deadlock Prevention in Transfers
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Transfers sort sender and receiver UUIDs deterministically before acquiring row locks. This ensures all concurrent operations lock resources in identical order, completely preventing database deadlocks.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-white border border-slate-200 space-y-3">
          <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
            <Database className="w-4 h-4 text-teal-600" /> Database-Level Immutability
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            In addition to omitting PUT, PATCH, and DELETE endpoints from the REST API, a PostgreSQL <code className="bg-slate-100 text-slate-800 px-1 py-0.5 rounded font-mono">BEFORE UPDATE OR DELETE</code> trigger raises an exception if direct SQL mutation is attempted on the transactions table.
          </p>
        </div>
      </div>
    </div>
  );
};
''')

# 13. App.tsx
with open('src/App.tsx', 'w') as f:
    f.write('''import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { CreateAccountModal } from './components/CreateAccountModal';
import { TransactionModal } from './components/TransactionModal';
import { TransferModal } from './components/TransferModal';
import { DashboardPage } from './pages/DashboardPage';
import { AccountsPage } from './pages/AccountsPage';
import { AccountDetailsPage } from './pages/AccountDetailsPage';
import { TransfersPage } from './pages/TransfersPage';
import { DocsPage } from './pages/DocsPage';
import { accountService, Account } from './services/accountService';

export default function App() {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [createAccountOpen, setCreateAccountOpen] = useState(false);
  const [transactionModalOpen, setTransactionModalOpen] = useState(false);
  const [transferModalOpen, setTransferModalOpen] = useState(false);

  const [transactionType, setTransactionType] = useState<'credit' | 'debit'>('credit');
  const [selectedAccountId, setSelectedAccountId] = useState<string | undefined>();
  const [accounts, setAccounts] = useState<Account[]>([]);

  const loadAccounts = async () => {
    try {
      const data = await accountService.getAccounts(0, 100);
      setAccounts(data.items);
    } catch (err) {
      console.error('Failed to load accounts in App:', err);
    }
  };

  useEffect(() => {
    loadAccounts();
  }, []);

  const handleOpenTransaction = (type: 'credit' | 'debit' = 'credit', accountId?: string) => {
    setTransactionType(type);
    setSelectedAccountId(accountId);
    setTransactionModalOpen(true);
  };

  const handleOpenTransfer = (sourceAccountId?: string) => {
    setSelectedAccountId(sourceAccountId);
    setTransferModalOpen(true);
  };

  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-slate-50 text-slate-900 font-sans">
        <Sidebar
          mobileOpen={mobileSidebarOpen}
          onCloseMobile={() => setMobileSidebarOpen(false)}
        />

        <div className="flex-1 flex flex-col min-w-0">
          <Navbar
            onOpenMobileSidebar={() => setMobileSidebarOpen(true)}
            onOpenCreateAccount={() => setCreateAccountOpen(true)}
            onOpenTransaction={(t) => handleOpenTransaction(t)}
            onOpenTransfer={() => handleOpenTransfer()}
          />

          <main className="flex-1 p-4 sm:p-8 max-w-7xl w-full mx-auto">
            <Routes>
              <Route
                path="/"
                element={
                  <DashboardPage
                    onOpenCreateAccount={() => setCreateAccountOpen(true)}
                    onOpenTransaction={handleOpenTransaction}
                    onOpenTransfer={handleOpenTransfer}
                  />
                }
              />
              <Route
                path="/accounts"
                element={
                  <AccountsPage
                    onOpenCreateAccount={() => setCreateAccountOpen(true)}
                    onOpenTransaction={handleOpenTransaction}
                    onOpenTransfer={handleOpenTransfer}
                  />
                }
              />
              <Route
                path="/accounts/:accountId"
                element={
                  <AccountDetailsPage
                    onOpenTransaction={handleOpenTransaction}
                    onOpenTransfer={handleOpenTransfer}
                  />
                }
              />
              <Route
                path="/transfers"
                element={<TransfersPage onOpenTransfer={() => handleOpenTransfer()} />}
              />
              <Route path="/docs-info" element={<DocsPage />} />
            </Routes>
          </main>
        </div>

        {/* Global Modals */}
        <CreateAccountModal
          isOpen={createAccountOpen}
          onClose={() => setCreateAccountOpen(false)}
          onSuccess={() => loadAccounts()}
        />

        <TransactionModal
          isOpen={transactionModalOpen}
          initialType={transactionType}
          initialAccountId={selectedAccountId}
          accounts={accounts}
          onClose={() => setTransactionModalOpen(false)}
          onSuccess={() => loadAccounts()}
        />

        <TransferModal
          isOpen={transferModalOpen}
          initialSourceAccountId={selectedAccountId}
          accounts={accounts}
          onClose={() => setTransferModalOpen(false)}
          onSuccess={() => loadAccounts()}
        />
      </div>
    </BrowserRouter>
  );
}
''')

# Copy all files into bank-transaction-system/frontend/src as well
shutil.copytree('src', 'bank-transaction-system/frontend/src', dirs_exist_ok=True)
print("All frontend files generated successfully in both src and bank-transaction-system/frontend/src!")
