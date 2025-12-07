import { useQuery } from '@tanstack/react-query';
import { getPlanowanieBudzetu, getPlanowanieBudzetuById } from '~/queries/planowanie-budzetu';

export const usePlanowanieBudzetu = (id?: string) => {
  return useQuery({
    queryKey: id ? ['planowanie-budzetu', id] : ['planowanie-budzetu'],
    queryFn: async () => {
      if (id) {
        const singleItem = await getPlanowanieBudzetuById(id);
        // Zwracamy jako array żeby zachować kompatybilność z BudgetGrid
        return [singleItem];
      }
      return getPlanowanieBudzetu();
    },
    staleTime: 5 * 60 * 1000,
  });
};
