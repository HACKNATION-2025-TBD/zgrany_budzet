'use client';

import { useMemo } from 'react';
import {
  AllCommunityModule,
  ModuleRegistry,
  type ColDef,
} from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import type { BudgetDocument, KodZadaniowy, DocumentRow } from '~/schema';
import { useGridData } from '~/hooks/use-grid-data';
import { usePlanowanieBudzetu } from '~/hooks/use-planowanie-budzetu';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';
import { useUserMock } from '~/hooks/use-user-mock';

ModuleRegistry.registerModules([AllCommunityModule]);

const BudgetGrid = () => {
  const { user } = useUserMock();
  const {
    dzialy,
    rozdzialy,
    paragrafy,
    grupyWydatkow,
    czesciBudzetowe,
    zrodlaFinansowania,
    kodyZadaniowe,
    isLoading: isLoadingGridData,
  } = useGridData();
  const { data: planowanieBudzetu, isLoading: isLoadingPlanowanie } = usePlanowanieBudzetu();

  // Transform planning data to budget document format
  const budgetDocument: BudgetDocument = useMemo(() => {
    if (!planowanieBudzetu) return [];

    return planowanieBudzetu.map((item): DocumentRow => {
      // Find corresponding objects from the grid data
      const dzial = dzialy?.find(d => d.kod === item.dzial_kod) || null;
      const rozdzial = rozdzialy?.find(r => r.kod === item.rozdzial_kod) || null;
      const paragraf = paragrafy?.find(p => p.kod === item.paragraf_kod) || null;
      const czescBudzetowa = czesciBudzetowe?.find(c => c.kod === item.czesc_budzetowa_kod) || null;
      const zrodloFinansowania = zrodlaFinansowania?.find(z => z.kod === item.zrodlo_finansowania_kod) || null;
      const grupaWydatkow = grupyWydatkow?.find(g => g.id === item.grupa_wydatkow_id) || null;
      
      // For now, we'll use a mock kod zadaniowy since we don't have the mapping
      const kodZadaniowy = kodyZadaniowe?.[0] || null;

      return {
        dzial,
        rozdzial,
        paragraf,
        grupaWydatkow,
        czescBudzetowa,
        zrodloFinansowania,
        kodZadaniowy,
        nazwaProgramu: item.nazwa_projektu || 'nie dotyczy',
        planWI: item.budzet || 'nie dotyczy',
      };
    });
  }, [planowanieBudzetu, dzialy, rozdzialy, paragrafy, grupyWydatkow, czesciBudzetowe, zrodlaFinansowania, kodyZadaniowe]);

  const formatKodAndNazwa = (params: {
    value: { kod: string; nazwa?: string; tresc?: string } | null;
  }) => {
    if (!params?.value) return '';

    return `${params.value.kod} - ${params.value?.nazwa ?? params.value?.tresc}`.trim();
  };

  const renderKodCellWithTooltip = (params: {
    value: { kod: string; nazwa?: string; tresc?: string } | null;
  }) => {
    if (!params?.value) return '';

    return (
      <Tooltip>
        <TooltipTrigger asChild>
          <div className='w-full'>
            {params.value.kod ?? params.value?.nazwa ?? params.value}
          </div>
        </TooltipTrigger>
        <TooltipContent side='bottom' className='max-w-sm'>
          <span>
            {params.value?.nazwa ??
              params.value?.tresc ??
              params.value?.kod ??
              params.value}
          </span>
        </TooltipContent>
      </Tooltip>
    );
  };

  const colDefs: ColDef[] = useMemo(
    () => [
      {
        headerName: 'Część budżetowa',
        field: 'czescBudzetowa' as const,
        editable: true,
        valueFormatter: formatKodAndNazwa,
        cellRenderer: renderKodCellWithTooltip,
        cellEditor: 'agSelectCellEditor',
        cellEditorParams: {
          values:
            czesciBudzetowe?.sort((a, b) => a.kod.localeCompare(b.kod)) ?? [],
        },
      },
      {
        headerName: 'Dział',
        field: 'dzial' as const,
        editable: true,
        valueFormatter: formatKodAndNazwa,
        cellRenderer: renderKodCellWithTooltip,
        cellEditor: 'agSelectCellEditor',
        cellEditorParams: {
          values: dzialy?.sort((a, b) => a.kod.localeCompare(b.kod)) ?? [],
        },
      },
      {
        headerName: 'Rozdział',
        field: 'rozdzial' as const,
        editable: true,
        cellEditor: 'agSelectCellEditor',
        valueFormatter: formatKodAndNazwa,
        cellRenderer: renderKodCellWithTooltip,
        cellEditorParams: {
          values: rozdzialy?.sort((a, b) => a.kod.localeCompare(b.kod)) ?? [],
        },
      },
      {
        headerName: 'Paragraf',
        field: 'paragraf' as const,
        editable: true,
        cellEditor: 'agSelectCellEditor',
        valueFormatter: formatKodAndNazwa,
        cellRenderer: renderKodCellWithTooltip,
        cellEditorParams: {
          values: paragrafy?.sort((a, b) => a.kod.localeCompare(b.kod)) ?? [],
        },
      },
      {
        headerName: 'Źródło finansowania',
        field: 'zrodloFinansowania' as const,
        editable: true,
        cellEditor: 'agSelectCellEditor',
        valueFormatter: formatKodAndNazwa,
        cellRenderer: renderKodCellWithTooltip,
        cellEditorParams: {
          values:
            zrodlaFinansowania?.sort((a, b) => a.kod.localeCompare(b.kod)) ??
            [],
        },
      },
      {
        headerName: 'Grupa wydatków',
        field: 'grupaWydatkow' as const,
        cellRenderer: renderKodCellWithTooltip,
        editable: true,
        cellEditor: 'agSelectCellEditor',
        cellEditorParams: {
          values: grupyWydatkow?.map((gw) => gw.nazwa).sort() ?? [],
        },
      },
      {
        headerName: 'Budżet zadaniowy (w pełnej szczegółowości)',
        field: 'kodZadaniowy' as const,
        cellRenderer: renderKodCellWithTooltip,
        editable: true,
        cellEditor: 'agSelectCellEditor',
        cellEditorParams: {
          values:
            kodyZadaniowe?.sort((a, b) => a.kod.localeCompare(b.kod)) ?? [],
        },
      },
      {
        headerName: 'Budżet zadaniowy (nr funkcji, nr zadania)',
        field: 'kodZadaniowy' as const,
        cellRenderer: (params: { value: KodZadaniowy }) => {
          return params.value.kod_krotki;
        },
        editable: false,
      },
      {
        headerName: 'Nazwa programu',
        field: 'nazwaProgramu' as const,
        editable: true,
        cellEditor: 'agTextCellEditor',
      },
      {
        headerName: 'Nazwa komórki organizacyjnej',
        editable: false,
        cellRenderer: () => {
          return user.nazwaKomorkiOrganizacyjnej;
        },
      },
      {
        headerName: 'Plan WI',
        field: 'planWI' as const,
        editable: true,
        cellEditor: 'agTextCellEditor',
      },
    ],
    [
      czesciBudzetowe,
      dzialy,
      rozdzialy,
      paragrafy,
      zrodlaFinansowania,
      grupyWydatkow,
    ]
  );

  const defaultColDef = {
    flex: 1,
  };

  return (
    <AgGridReact
      rowData={budgetDocument}
      columnDefs={colDefs}
      editType='singleCell'
      stopEditingWhenCellsLoseFocus={true}
      onCellEditingStopped={(event) => {
        console.log('Cell editing stopped:', event);
      }}
      onCellEditingStarted={(event) => {
        console.log('Cell editing started:', event);
      }}
      onCellValueChanged={(event) => {
        console.log('Cell value changed:', event);
      }}
      defaultColDef={defaultColDef}
    />
  );
};

export default BudgetGrid;
