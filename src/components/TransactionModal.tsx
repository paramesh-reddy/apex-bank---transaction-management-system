import React, { useState, useEffect } from 'react';
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
