import { useQuery } from '@tanstack/react-query';
import { apiClient } from './client';
import type { Paragraf } from '~/schema';

export const useParagrafy = () => {
  return useQuery({
    queryKey: ['paragrafy'],
    queryFn: async (): Promise<Paragraf[]> => {
      const response = await apiClient.get('/paragrafy');
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
};
