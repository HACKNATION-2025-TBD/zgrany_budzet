import { useQuery } from '@tanstack/react-query';
import { apiClient } from './client';
import type { CzescBudzetowa } from '~/schema';

export const useCzesciBudzetowe = () => {
  return useQuery({
    queryKey: ['czesci_budzetowe'],
    queryFn: async (): Promise<CzescBudzetowa[]> => {
      const response = await apiClient.get('/czesci_budzetowe');
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
};
