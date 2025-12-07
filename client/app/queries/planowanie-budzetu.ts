import { apiClient } from './client';
import type { PlanowanieBudzetuCreate, PlanowanieBudzetuResponse } from '~/schema';

export interface CreatePlanowanieBudzetuResponse {
  id: number;
  message: string;
}

export async function createPlanowanieBudzetu(
  data: PlanowanieBudzetuCreate
): Promise<CreatePlanowanieBudzetuResponse> {
  const response = await apiClient.post('/planowanie_budzetu', data);
  return response.data;
}

export async function getPlanowanieBudzetu(): Promise<PlanowanieBudzetuResponse[]> {
  const response = await apiClient.get('/planowanie_budzetu');
  return response.data;
}
