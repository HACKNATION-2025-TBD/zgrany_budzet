import { useQuery } from '@tanstack/react-query';
import { apiClient } from './client';
import type { Post } from './types';

export const usePost = () => {
  return useQuery({
    queryKey: ['posts'],
    queryFn: async (): Promise<Post[]> => {
      const response = await apiClient.get('/posts');
      return response.data;
    },
    staleTime: 5 * 60 * 1000, 
  });
};
