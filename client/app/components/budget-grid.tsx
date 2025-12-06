'use client';

import { useMemo } from 'react';
import {
  AllCommunityModule,
  ModuleRegistry,
  type ColDef,
} from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import type { BudgetDocument } from '~/schema';
import { useGridData } from '~/hooks/use-grid-data';

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
    isLoading: isLoadingGridData,
  } = useGridData();

  const formatKodAndNazwa = (item: {
    value: { kod: string; nazwa?: string; tresc?: string } | null;
  }) => {
    if (!item?.value) return '';

    return `${item.value.kod} - ${item.value?.nazwa ?? item.value?.tresc}`.trim();
  };

  const colDefs: ColDef[] = useMemo(
    () => [
      {
        field: 'czescBudzetowa' as const,
        valueParser: (params) => {
          console.log('Value parser called with params:', params);
          const newValue = params.newValue;
          console.log(params);

          if (Number.isNaN(Number(newValue))) {
            return params.oldValue;
          }
          return newValue;
        },
        editable: true,
        valueFormatter: formatKodAndNazwa,
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
        cellEditorParams: {
          values: rozdzialy?.sort((a, b) => a.kod.localeCompare(b.kod)) ?? [],
        },
      },
      {
        field: 'paragraf' as const,
        editable: true,
        cellEditor: 'agSelectCellEditor',
        valueFormatter: formatKodAndNazwa,
        cellEditorParams: {
          values: paragrafy?.sort((a, b) => a.kod.localeCompare(b.kod)) ?? [],
        },
      },
      {
        field: 'zrodloFinansowania' as const,
        editable: true,
        cellEditor: 'agSelectCellEditor',
        valueFormatter: formatKodAndNazwa,
        cellEditorParams: {
          values:
            zrodlaFinansowania?.sort((a, b) => a.kod.localeCompare(b.kod)) ??
            [],
        },
      },
      {
        field: 'grupaWydatkow' as const,
        editable: true,
        cellEditor: 'agSelectCellEditor',
        cellEditorParams: {
          values: grupyWydatkow?.map((gw) => gw.nazwa).sort() ?? [],
        },
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
