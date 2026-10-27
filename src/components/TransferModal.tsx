import React, { useState, useEffect } from 'react';
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
