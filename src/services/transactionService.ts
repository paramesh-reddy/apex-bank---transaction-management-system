import { apiClient } from './api';

export interface Transaction {
  id: string;
  account_id: string;
  type: 'credit' | 'debit';
  amount: string;
  description: string | null;
  reference_id: string;
  transfer_id: string | null;
  created_at: string;
}

export interface TransactionWithBalanceResponse {
  transaction: Transaction;
  account_balance: string;
}

export interface PaginatedTransactionsResponse {
  items: Transaction[];
  current_page: number;
  page_size: number;
  total_records: number;
  total_pages: number;
}

export interface CreateTransactionPayload {
  type: 'credit' | 'debit';
  amount: string;
  description?: string;
  reference_id: string;
}

export const transactionService = {
  async getAccountTransactions(
    accountId: string,
    page = 1,
    limit = 10
  ): Promise<PaginatedTransactionsResponse> {
    const res = await apiClient.get<PaginatedTransactionsResponse>(
      `/accounts/${accountId}/transactions`,
      { params: { page, limit } }
    );
    return res.data;
  },

  async createTransaction(
    accountId: string,
    payload: CreateTransactionPayload
  ): Promise<TransactionWithBalanceResponse> {
    const res = await apiClient.post<TransactionWithBalanceResponse>(
      `/accounts/${accountId}/transactions`,
      payload
    );
    return res.data;
  },
};
