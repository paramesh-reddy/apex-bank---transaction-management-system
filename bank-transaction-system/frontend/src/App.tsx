import { useState, useEffect } from 'react';
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
  const [revision, setRevision] = useState(0);

  const loadAccounts = async () => {
    try {
      const data = await accountService.getAccounts(0, 100);
      setAccounts(data.items);
    } catch (err) {
      console.error('Failed to load accounts', err);
    }
  };

  useEffect(() => {
    loadAccounts();
  }, []);

  const refreshData = () => {
    loadAccounts();
    setRevision((n) => n + 1);
  };

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
                    revision={revision}
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
                    revision={revision}
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
                    revision={revision}
                    onOpenTransaction={handleOpenTransaction}
                    onOpenTransfer={handleOpenTransfer}
                  />
                }
              />
              <Route
                path="/transfers"
                element={<TransfersPage revision={revision} onOpenTransfer={() => handleOpenTransfer()} />}
              />
              <Route path="/docs-info" element={<DocsPage />} />
            </Routes>
          </main>
        </div>

        {/* Global Modals */}
        <CreateAccountModal
          isOpen={createAccountOpen}
          onClose={() => setCreateAccountOpen(false)}
          onSuccess={refreshData}
        />

        <TransactionModal
          isOpen={transactionModalOpen}
          initialType={transactionType}
          initialAccountId={selectedAccountId}
          accounts={accounts}
          onClose={() => setTransactionModalOpen(false)}
          onSuccess={refreshData}
        />

        <TransferModal
          isOpen={transferModalOpen}
          initialSourceAccountId={selectedAccountId}
          accounts={accounts}
          onClose={() => setTransferModalOpen(false)}
          onSuccess={refreshData}
        />
      </div>
    </BrowserRouter>
  );
}
