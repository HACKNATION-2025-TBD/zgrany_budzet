import { useQuery } from '@tanstack/react-query';
import { apiClient } from './client';
import type { ZrodloFinansowania } from '~/schema';

export const useZrodlaFinansowania = () => {
  return useQuery({
    queryKey: ['zrodla_finansowania'],
    queryFn: async (): Promise<ZrodloFinansowania[]> => {
      const response = await apiClient.get('/zrodla_finansowania');
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
};
