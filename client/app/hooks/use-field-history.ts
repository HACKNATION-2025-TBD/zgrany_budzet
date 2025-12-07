import { useQuery } from '@tanstack/react-query';
import { getPlanowanieBudzetuFieldsHistoryStatus, getPlanowanieBudzetuFieldHistory } from '~/queries/planowanie-budzetu';

export function useFieldsHistoryStatus(planowanieBudzetuId: number | null) {
  return useQuery({
    queryKey: ['planowanie-budzetu-fields-history-status', planowanieBudzetuId],
    queryFn: () => getPlanowanieBudzetuFieldsHistoryStatus(planowanieBudzetuId!),
    enabled: !!planowanieBudzetuId,
  });
}

export function useFieldHistory(planowanieBudzetuId: number | null, fieldName: string | null) {
  return useQuery({
    queryKey: ['planowanie-budzetu-field-history', planowanieBudzetuId, fieldName],
    queryFn: () => getPlanowanieBudzetuFieldHistory(planowanieBudzetuId!, fieldName!),
    enabled: !!planowanieBudzetuId && !!fieldName,
  });
}
