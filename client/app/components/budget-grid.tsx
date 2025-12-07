'use client';

import { useMemo } from 'react';
import {
  AllCommunityModule,
  ModuleRegistry,
  type ColDef,
} from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import type { BudgetDocument, KodZadaniowy } from '~/schema';
import { useGridData } from '~/hooks/use-grid-data';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';

ModuleRegistry.registerModules([AllCommunityModule]);

type BudgetGridProps = {
  budgetDocument: BudgetDocument;
};

const BudgetGrid = ({ budgetDocument }: BudgetGridProps) => {
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
        field: 'grupaWydatkow' as const,
        cellRenderer: renderKodCellWithTooltip,
        editable: true,
        cellEditor: 'agSelectCellEditor',
        cellEditorParams: {
          values: grupyWydatkow?.map((gw) => gw.nazwa).sort() ?? [],
        },
      },
      {
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
        field: 'kodZadaniowy' as const,
        cellRenderer: (params: { value: KodZadaniowy }) => {
          return params.value.kod_krotki;
        },
        editable: false,
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
