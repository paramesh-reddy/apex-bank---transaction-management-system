import React from 'react';
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
