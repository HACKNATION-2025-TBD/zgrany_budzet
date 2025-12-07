import { useQuery } from '@tanstack/react-query';
import { getPlanowanieBudzetu } from '~/queries/planowanie-budzetu';

export const usePlanowanieBudzetu = () => {
  return useQuery({
    queryKey: ['planowanie-budzetu'],
    queryFn: getPlanowanieBudzetu,
  });
};
