import { apiClient } from './client';
import type { PlanowanieBudzetuCreate } from '~/schema';

export interface PlanowanieBudzetuResponse {
  id: number;
  message: string;
}

export async function createPlanowanieBudzetu(
  data: PlanowanieBudzetuCreate
): Promise<PlanowanieBudzetuResponse> {
  const response = await apiClient.post('/planowanie_budzetu', data);
  return response.data;
}
