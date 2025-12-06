import { useQuery } from '@tanstack/react-query';
import { apiClient } from './client';
import type { Rozdzial } from '~/schema';

export const useRozdzialy = () => {
  return useQuery({
    queryKey: ['rozdzialy'],
    queryFn: async (): Promise<Rozdzial[]> => {
      const response = await apiClient.get('/rozdzialy');
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
};
