# Apex Bank Account & Transaction System — API Documentation

This document describes the RESTful API for the Bank Account and Transaction Management System built with **FastAPI**, **SQLAlchemy 2.0**, and **Neon PostgreSQL**.

Interactive OpenAPI/Swagger documentation is automatically available at:
`http://localhost:8000/docs` (or `/docs` in AI Studio).

---

## Standard Error Format

All error responses across the API follow a strict, consistent JSON structure:

```json
{
  "error": {
    "code": "INSUFFICIENT_BALANCE",
    "message": "The account does not have sufficient funds.",
    "details": null
  }
}
```

### HTTP Status Code Mappings:
| HTTP Status | Error Code | Description |
|---|---|---|
| `200 OK` | — | Successful read or query |
| `201 Created` | — | Successful resource creation (Account, Transaction, Transfer) |
| `400 Bad Request` | `INSUFFICIENT_BALANCE`, `SAME_ACCOUNT_TRANSFER`, `INVALID_AMOUNT`, `INVALID_PAGINATION` | Business logic validation failure |
| `404 Not Found` | `ACCOUNT_NOT_FOUND` | Account or requested resource does not exist |
| `409 Conflict` | `DUPLICATE_TRANSACTION_REFERENCE`, `DUPLICATE_TRANSFER_REFERENCE` | Unique constraint violation |
| `422 Unprocessable` | `VALIDATION_ERROR` | Schema / input format validation failure |
| `500 Server Error` | `INTERNAL_SERVER_ERROR` | Unexpected server failure (details redacted) |

---

## 1. Account Management Endpoints

### 1.1 Create Bank Account
- **Endpoint**: `POST /api/v1/accounts`
- **Description**: Creates a new bank account with an initial authoritative balance of `0.00`.
- **Request Body**:
```json
{
  "name": "Acme Capital Operating Account"
}
```
- **Validation Rules**:
  - `name`: Required, non-empty, trimmed string (max 255 chars).
  - Balance defaults to `0.00` via database schema.
- **Success Response (`201 Created`)**:
```json
{
  "id": "e4b2d3c1-7f8a-4b9e-9c2d-1a2b3c4d5e6f",
  "name": "Acme Capital Operating Account",
  "balance": "0.00",
  "created_at": "2026-10-27T12:00:00.000000Z"
}
```
- **Example cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/accounts \
  -H "Content-Type: application/json" \
  -d '{"name": "Savings Account"}'
```

---

### 1.2 List Bank Accounts
- **Endpoint**: `GET /api/v1/accounts`
- **Query Parameters**:
  - `skip` (optional, default `0`, min `0`): Offset for pagination.
  - `limit` (optional, default `100`, min `1`, max `100`): Maximum records.
- **Success Response (`200 OK`)**:
```json
{
  "items": [
    {
      "id": "e4b2d3c1-7f8a-4b9e-9c2d-1a2b3c4d5e6f",
      "name": "Acme Capital Operating Account",
      "balance": "1500.50",
      "created_at": "2026-10-27T12:00:00.000000Z"
    }
  ],
  "total": 1
}
```

---

### 1.3 Get Account Details & Current Balance
- **Endpoint**: `GET /api/v1/accounts/{account_id}`
- **Path Parameter**: `account_id` (UUID format)
- **Success Response (`200 OK`)**:
```json
{
  "id": "e4b2d3c1-7f8a-4b9e-9c2d-1a2b3c4d5e6f",
  "name": "Acme Capital Operating Account",
  "balance": "1500.50",
  "created_at": "2026-10-27T12:00:00.000000Z"
}
```
- **Error Response (`404 Not Found`)**:
```json
{
  "error": {
    "code": "ACCOUNT_NOT_FOUND",
    "message": "Account with ID 'e4b2d3c1-...' was not found.",
    "details": null
  }
}
```

---

### 1.4 Get Aggregated Financial Metrics
- **Endpoint**: `GET /api/v1/accounts/summary/metrics`
- **Description**: Returns live aggregated bank totals calculated directly in PostgreSQL using `COALESCE(SUM(balance), 0)`.
- **Success Response (`200 OK`)**:
```json
{
  "total_accounts": 15,
  "total_balance": "8450.75",
  "total_transactions": 42
}
```

---

## 2. Transaction Management Endpoints

### 2.1 Post Transaction (Credit or Debit)
- **Endpoint**: `POST /api/v1/accounts/{account_id}/transactions`
- **Description**: Executes an atomic balance update and inserts an immutable transaction record within a single database transaction.
- **Request Body Example**:
```json
{
  "type": "credit",
  "amount": "100.00",
  "description": "Initial customer deposit",
  "reference_id": "REF-1001"
}
```
- **Validation Rules**:
  - `account_id`: Must reference an existing account.
  - `type`: Must be strictly `"credit"` or `"debit"`.
  - `amount`: Must be greater than zero, have at most 2 decimal places, and be a valid positive `Decimal` (NaN and Infinity rejected).
  - `reference_id`: Required, non-empty string. Must be unique per account.
  - For `debit`: Current balance must be greater than or equal to `amount`.
- **Success Response (`201 Created`)**:
```json
{
  "transaction": {
    "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
    "account_id": "e4b2d3c1-7f8a-4b9e-9c2d-1a2b3c4d5e6f",
    "type": "credit",
    "amount": "100.00",
    "description": "Initial customer deposit",
    "reference_id": "REF-1001",
    "transfer_id": null,
    "created_at": "2026-10-27T12:05:00.000000Z"
  },
  "account_balance": "100.00"
}
```
- **Error Response — Insufficient Funds (`400 Bad Request`)**:
```json
{
  "error": {
    "code": "INSUFFICIENT_BALANCE",
    "message": "The account does not have sufficient funds. Available: 50.00, Requested debit: 100.00.",
    "details": null
  }
}
```
- **Error Response — Duplicate Reference (`409 Conflict`)**:
```json
{
  "error": {
    "code": "DUPLICATE_TRANSACTION_REFERENCE",
    "message": "Transaction with reference 'REF-1001' already exists for this account.",
    "details": null
  }
}
```

---

### 2.2 List Transactions (Paginated)
- **Endpoint**: `GET /api/v1/accounts/{account_id}/transactions`
- **Query Parameters**:
  - `page` (optional, default `1`, min `1`): 1-indexed page number.
  - `limit` (optional, default `10`, min `1`, max `100`): Records per page.
- **Sorting Guarantee**: Strictly sorted by `created_at DESC`, with a secondary deterministic sort by `id DESC`.
- **Success Response (`200 OK`)**:
```json
{
  "items": [
    {
      "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
      "account_id": "e4b2d3c1-7f8a-4b9e-9c2d-1a2b3c4d5e6f",
      "type": "credit",
      "amount": "100.00",
      "description": "Initial customer deposit",
      "reference_id": "REF-1001",
      "transfer_id": null,
      "created_at": "2026-10-27T12:05:00.000000Z"
    }
  ],
  "current_page": 1,
  "page_size": 10,
  "total_records": 1,
  "total_pages": 1
}
```

---

## 3. Money Transfer Endpoints

### 3.1 Execute Inter-Account Transfer
- **Endpoint**: `POST /api/v1/transfers`
- **Description**: Atomically transfers funds between two distinct accounts.
- **Request Body Example**:
```json
{
  "source_account_id": "e4b2d3c1-7f8a-4b9e-9c2d-1a2b3c4d5e6f",
  "destination_account_id": "9a8b7c6d-5e4f-3a2b-1c0d-e4f5a6b7c8d9",
  "amount": "30.00",
  "reference_id": "TRANSFER-1001",
  "description": "Supplier payment"
}
```
- **Requirements**:
  1. Source and destination IDs must be different (`400 SAME_ACCOUNT_TRANSFER`).
  2. Both accounts must exist (`404 ACCOUNT_NOT_FOUND`).
  3. Source account balance >= amount (`400 INSUFFICIENT_BALANCE`).
  4. Global unique transfer reference (`409 DUPLICATE_TRANSFER_REFERENCE`).
  5. Deterministic row locking: Locks `min(src_id, dst_id)` then `max(src_id, dst_id)` to eliminate deadlocks.
- **Success Response (`201 Created`)**:
```json
{
  "transfer": {
    "id": "778899aa-bbcc-ddee-ff00-112233445566",
    "reference_id": "TRANSFER-1001",
    "source_account_id": "e4b2d3c1-7f8a-4b9e-9c2d-1a2b3c4d5e6f",
    "destination_account_id": "9a8b7c6d-5e4f-3a2b-1c0d-e4f5a6b7c8d9",
    "amount": "30.00",
    "description": "Supplier payment",
    "created_at": "2026-10-27T12:10:00.000000Z"
  },
  "source_transaction": {
    "id": "...",
    "account_id": "e4b2d3c1-...",
    "type": "debit",
    "amount": "30.00",
    "description": "Transfer to Destination Account: Supplier payment",
    "reference_id": "TR-DEBIT-TRANSFER-1001",
    "transfer_id": "778899aa-...",
    "created_at": "..."
  },
  "destination_transaction": {
    "id": "...",
    "account_id": "9a8b7c6d-...",
    "type": "credit",
    "amount": "30.00",
    "description": "Transfer from Source Account: Supplier payment",
    "reference_id": "TR-CREDIT-TRANSFER-1001",
    "transfer_id": "778899aa-...",
    "created_at": "..."
  },
  "source_balance": "70.00",
  "destination_balance": "80.00"
}
```

---

## 4. Transaction Immutability & Database Trigger

1. **API Layer**: There are no `PUT`, `PATCH`, or `DELETE` endpoints for transactions or transfers.
2. **Database Layer**: A PostgreSQL trigger `trg_prevent_transaction_update_delete` blocks direct SQL updates/deletions on the `transactions` table:
```sql
CREATE OR REPLACE FUNCTION prevent_transaction_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Transactions are strictly immutable and cannot be updated or deleted.';
END;
$$ LANGUAGE plpgsql;
```
