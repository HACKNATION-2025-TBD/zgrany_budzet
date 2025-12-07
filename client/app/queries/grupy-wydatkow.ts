import { useQuery } from '@tanstack/react-query';
import { apiClient } from './client';
import type { GrupaWydatkow } from '~/schema';

export const useGrupyWydatkow = () => {
  return useQuery({
    queryKey: ['grupy_wydatkow'],
    queryFn: async (): Promise<GrupaWydatkow[]> => {
      const response = await apiClient.get('/grupy_wydatkow');
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
};
