import React from 'react';
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
