import { apiClient } from './api';

export interface Account {
  id: string;
  name: string;
  balance: string;
  created_at: string;
}

export interface AccountListResponse {
  items: Account[];
  total: number;
}

export interface AccountMetrics {
  total_accounts: number;
  total_balance: string;
  total_transactions: number;
}

export const accountService = {
  async getAccounts(skip = 0, limit = 100): Promise<AccountListResponse> {
    const res = await apiClient.get<AccountListResponse>('/accounts', {
      params: { skip, limit },
    });
    return res.data;
  },

  async getAccount(accountId: string): Promise<Account> {
    const res = await apiClient.get<Account>(`/accounts/${accountId}`);
    return res.data;
  },

  async getMetrics(): Promise<AccountMetrics> {
    const res = await apiClient.get<AccountMetrics>('/accounts/summary/metrics');
    return res.data;
  },

  async createAccount(name: string): Promise<Account> {
    const res = await apiClient.post<Account>('/accounts', { name });
    return res.data;
  },
};
