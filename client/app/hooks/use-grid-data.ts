import { useDzialy } from '../queries';
import { useRozdzialy } from '../queries';
import { useParagrafy } from '../queries';
import { useGrupyWydatkow } from '../queries';
import { useCzesciBudzetowe } from '../queries';
import { useZrodlaFinansowania } from '../queries';

export const useGridData = () => {
  const { data: dzialy, isLoading: isLoadingDzialy } = useDzialy();
  const { data: rozdzialy, isLoading: isLoadingRozdzialy } = useRozdzialy();
  const { data: paragrafy, isLoading: isLoadingParagrafy } = useParagrafy();
  const { data: grupyWydatkow, isLoading: isLoadingGrupyWydatkow } =
    useGrupyWydatkow();
  const { data: czesciBudzetowe, isLoading: isLoadingCzesciBudzetowe } =
    useCzesciBudzetowe();
  const { data: zrodlaFinansowania, isLoading: isLoadingZrodlaFinansowania } =
    useZrodlaFinansowania();

  return {
    dzialy,
    rozdzialy,
    paragrafy,
    grupyWydatkow,
    czesciBudzetowe,
    zrodlaFinansowania,
    isLoading:
      isLoadingDzialy ||
      isLoadingRozdzialy ||
      isLoadingParagrafy ||
      isLoadingGrupyWydatkow ||
      isLoadingCzesciBudzetowe ||
      isLoadingZrodlaFinansowania,
  };
};
