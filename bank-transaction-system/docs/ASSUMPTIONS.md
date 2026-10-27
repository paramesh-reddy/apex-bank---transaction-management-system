# Apex Bank Account & Transaction System — Assumptions & Architectural Decisions

This document outlines key engineering assumptions, constraints, and design decisions made for the Full-Stack Developer Assessment.

---

## 1. Initial Account Balance
- Every new bank account begins with an authoritative balance of strictly `0.00`.
- Initial deposits must be made via an explicit `credit` transaction, providing a complete audit trail from account opening.

## 2. Currency & Numeric Representation
- The system operates under a single currency (USD, `$`).
- Floating-point arithmetic (`float`) is strictly prohibited in the backend codebase for all monetary values.
- Arbitrary-precision math is enforced using Python's `decimal.Decimal` and PostgreSQL's `NUMERIC(18, 2)` datatype.
- All monetary inputs are validated to have at most 2 decimal places and must be strictly positive (`amount > 0.00`). NaN and Infinity values are rejected with `422 Unprocessable Entity`.

## 3. Reference ID Uniqueness Policy
- **Transactions Table**: A composite unique constraint `UNIQUE (account_id, reference_id)` is enforced.
  - The same reference ID *may* be reused across different accounts (e.g., external vendor transaction IDs or check numbers).
  - Attempting to submit a duplicate reference ID for the same account raises `409 Conflict` (`DUPLICATE_TRANSACTION_REFERENCE`).
- **Transfers Table**: A global unique constraint `UNIQUE (reference_id)` is enforced on the `transfers` table.
- **Traceability Policy**:
  - The resulting debit transaction on the source account receives reference `TR-DEBIT-{transfer_reference_id}`.
  - The resulting credit transaction on the destination account receives reference `TR-CREDIT-{transfer_reference_id}`.
  - Both transaction records reference `transfer_id = transfer.id`, making transfers traceable from both accounts' transaction histories.

## 4. Atomicity & Concurrency (Pessimistic Locking)
- For every credit or debit:
  1. Open a single database transaction.
  2. Issue `SELECT ... FOR UPDATE` on the account row.
  3. Validate balance availability for debits.
  4. Insert immutable transaction row.
  5. Update the account balance.
  6. Commit both changes simultaneously.
- If any validation or database constraint fails, the entire transaction is rolled back immediately.
- Concurrent debit requests are serialized by the row lock; simultaneous requests cannot overspend the available balance.

## 5. Deadlock Prevention in Transfers
- When executing a transfer between Account A and Account B, row locks are acquired deterministically in ascending UUID string order (`min(A, B)` locked first, followed by `max(A, B)`).
- This eliminates cyclic lock dependencies between simultaneous cross-transfers (e.g., A &rarr; B and B &rarr; A occurring at the same instant).

## 6. Transaction Immutability
- Transactions are append-only.
- No `PUT`, `PATCH`, or `DELETE` endpoints are exposed in the REST API.
- A PostgreSQL `BEFORE UPDATE OR DELETE` trigger protects the `transactions` table from modifications even if attempted via direct SQL queries.

## 7. Authentication Scope
- Authentication and authorization (JWT/OAuth) are outside the scope of this assessment as specified in the guidelines. The system demonstrates core banking domain integrity, transaction atomicity, and ledger correctness.
