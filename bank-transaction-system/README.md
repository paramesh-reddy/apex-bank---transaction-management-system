# Apex Bank Account and Transaction Management System

A production-minded, full-stack Core Banking and Transaction Management System built with **React**, **FastAPI**, **SQLAlchemy 2.0**, **Alembic**, and **Neon PostgreSQL**.

---

## Key Features

1. **ACID Transaction Atomicity & Consistency**:
   - Single database transaction for balance verification, transaction row insertion, and balance updates.
   - Guaranteed rollback on any error with no orphaned or partial records.
2. **Pessimistic Concurrency Control**:
   - Uses `SELECT ... FOR UPDATE` row locks to serialize concurrent debits and protect against overdrafts.
3. **Deadlock-Free Inter-Account Transfers**:
   - Deterministic row-locking in ascending UUID order eliminates deadlock conditions during concurrent cross-transfers.
   - Creates linked debit and credit transaction records traceable from both accounts' histories.
4. **Append-Only Transaction Immutability**:
   - Zero update or delete API endpoints.
   - Enforced at the database layer with a PostgreSQL `BEFORE UPDATE OR DELETE` trigger.
5. **Arbitrary-Precision Financial Math**:
   - All calculations use Python `Decimal` and PostgreSQL `NUMERIC(18,2)`. Floats are strictly prohibited.
6. **Responsive Financial UI**:
   - Built with React, Tailwind CSS, Lucide icons, and React Router.
   - Real-time balance calculations, server-side pagination, quick-deposit pills, and transfer confirmation dialogs.

---

## Technology Stack

- **Frontend**: React 19, Vite, React Router, Tailwind CSS, Axios, Lucide React
- **Backend**: Python 3.10+, FastAPI, Pydantic v2, Pydantic-Settings, SQLAlchemy 2.0, Alembic, Psycopg 3
- **Database**: Neon Cloud PostgreSQL (Serverless connection pooler with SSL)
- **Testing**: Pytest, HTTPX, Starlette TestClient (23 passing automated tests)

---

## Project Structure

```
bank-transaction-system/
├── backend/
│   ├── alembic/
│   │   ├── versions/
│   │   │   └── 001_initial_schema.py
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── alembic.ini
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── accounts.py
│   │       │   └── transfers.py
│   │       └── router.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── exceptions.py
│   ├── models/
│   │   ├── account.py
│   │   ├── transaction.py
│   │   └── transfer.py
│   ├── repositories/
│   │   ├── account_repo.py
│   │   ├── transaction_repo.py
│   │   └── transfer_repo.py
│   ├── schemas/
│   │   ├── account.py
│   │   ├── transaction.py
│   │   ├── transfer.py
│   │   └── error.py
│   ├── services/
│   │   ├── account_service.py
│   │   ├── transaction_service.py
│   │   └── transfer_service.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_accounts.py
│   │   ├── test_transactions.py
│   │   ├── test_transfers.py
│   │   └── test_atomicity_concurrency.py
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CreateAccountModal.tsx
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── TransactionModal.tsx
│   │   │   ├── TransactionTable.tsx
│   │   │   └── TransferModal.tsx
│   │   ├── pages/
│   │   │   ├── AccountDetailsPage.tsx
│   │   │   ├── AccountsPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── DocsPage.tsx
│   │   │   └── TransfersPage.tsx
│   │   ├── services/
│   │   │   ├── accountService.ts
│   │   │   ├── api.ts
│   │   │   ├── transactionService.ts
│   │   │   └── transferService.ts
│   │   ├── utils/
│   │   │   └── formatters.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   └── .env.example
├── docs/
│   ├── API_DOCUMENTATION.md
│   └── ASSUMPTIONS.md
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## Getting Started & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Neon PostgreSQL connection string (configured in `.env`)

---

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Configure `DATABASE_URL`:
   ```env
   DATABASE_URL=postgresql+psycopg://neondb_owner:npg_cB1oTNHC6Fga@ep-sweet-wildflower-b5tiqheb-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   APP_ENV=development
   ```

5. Run Alembic Database Migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the FastAPI backend server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   - API: `http://localhost:8000/api/v1`
   - Interactive Swagger Documentation: `http://localhost:8000/docs`

---

### Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

4. Start Vite dev server:
   ```bash
   npm run dev
   ```
   The application will be live at `http://localhost:5173`.

---

## Automated Testing

Run the comprehensive Pytest suite against Neon PostgreSQL:
```bash
cd backend
PYTHONPATH=. pytest -v
```

### Test Coverage Highlights:
- **Accounts**: Creation, non-empty validation, 404 handling, listing.
- **Transactions**: Credit balance increase, debit decrease, multi-transaction decimal precision, rejection of zero/negative amounts, rejection of invalid types, per-account unique reference validation, insufficient balance protection.
- **Transfers**: Inter-account balance transfers, same-account transfer rejection, insufficient funds rejection, duplicate reference rejection, dual-account ledger traceability.
- **Atomicity & Concurrency**: Multi-threaded concurrent debits test ensuring balance never goes negative, PostgreSQL trigger blocking direct SQL updates and deletions on transaction rows.

---

## Docker Compose (Optional Local Development)

Run both frontend and backend services:
```bash
docker-compose up --build
```
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
