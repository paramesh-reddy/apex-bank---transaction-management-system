import React, { useEffect, useState } from 'react';
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
