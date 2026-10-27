import { apiClient } from './api';
import { Transaction } from './transactionService';

export interface Transfer {
  id: string;
  reference_id: string;
  source_account_id: string;
  destination_account_id: string;
  amount: string;
  description: string | null;
  created_at: string;
}

export interface CreateTransferPayload {
  source_account_id: string;
  destination_account_id: string;
  amount: string;
  reference_id: string;
  description?: string;
}

export interface TransferDetailResponse {
  transfer: Transfer;
  source_transaction: Transaction;
  destination_transaction: Transaction;
  source_balance: string;
  destination_balance: string;
}

export const transferService = {
  async createTransfer(payload: CreateTransferPayload): Promise<TransferDetailResponse> {
    const res = await apiClient.post<TransferDetailResponse>('/transfers', payload);
    return res.data;
  },

  async getTransfers(page = 1, limit = 20): Promise<Transfer[]> {
    const res = await apiClient.get<Transfer[]>('/transfers', {
      params: { page, limit },
    });
    return res.data;
  },
};
