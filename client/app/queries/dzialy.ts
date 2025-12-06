import { useQuery } from '@tanstack/react-query';
import { apiClient } from './client';
import type { Dzial } from '~/schema';

export const useDzialy = () => {
  return useQuery({
    queryKey: ['dzialy'],
    queryFn: async (): Promise<Dzial[]> => {
      const response = await apiClient.get('/dzialy');
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
};
