'use client';

import { useMemo, useState } from 'react';
import {
  AllCommunityModule,
  ModuleRegistry,
  type ColDef,
} from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import { useQueryClient } from '@tanstack/react-query';
import type { BudgetDocument, KodZadaniowy, DocumentRow } from '~/schema';
import { useGridData } from '~/hooks/use-grid-data';
import { usePlanowanieBudzetu } from '~/hooks/use-planowanie-budzetu';
import { updatePlanowanieBudzetuCell } from '~/queries/planowanie-budzetu';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';
import { Button } from './ui/button';
import { useUserMock } from '~/hooks/use-user-mock';
import { History, Edit } from 'lucide-react';
import HistoryModal from './history-modal';
import { useFieldsHistoryStatus } from '~/hooks/use-field-history';

ModuleRegistry.registerModules([AllCommunityModule]);

const BudgetGrid = () => {
  const queryClient = useQueryClient();
  const { user } = useUserMock();
  const [isHistoryMode, setIsHistoryMode] = useState(false);
  const [historyModalData, setHistoryModalData] = useState<{
    field: string;
    value: any;
    rowId: number;
  } | null>(null);

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
  const { data: planowanieBudzetu, isLoading: isLoadingPlanowanie } =
    usePlanowanieBudzetu();

  // Map frontend field names to backend field names
  const mapFieldToBackendFieldName = (field: string): string => {
    const fieldMap: Record<string, string> = {
      czescBudzetowa: 'czesc_budzetowa_kod',
      dzial: 'dzial_kod',
      rozdzial: 'rozdzial_kod',
      paragraf: 'paragraf_kod',
      zrodloFinansowania: 'zrodlo_finansowania_kod',
      grupaWydatkow: 'grupa_wydatkow_id',
      nazwaProgramu: 'nazwa_projektu',
      planWI: 'budzet',
    };
    return fieldMap[field] || field;
  };

  // Transform planning data to budget document format
  const budgetDocument: BudgetDocument = useMemo(() => {
    if (!planowanieBudzetu) return [];

    return planowanieBudzetu.map((item): DocumentRow => {
      // Find corresponding objects from the grid data
      const dzial = dzialy?.find((d) => d.kod === item.dzial_kod) || null;
      const rozdzial =
        rozdzialy?.find((r) => r.kod === item.rozdzial_kod) || null;
      const paragraf =
        paragrafy?.find((p) => p.kod === item.paragraf_kod) || null;
      const czescBudzetowa =
        czesciBudzetowe?.find((c) => c.kod === item.czesc_budzetowa_kod) ||
        null;
      const zrodloFinansowania =
        zrodlaFinansowania?.find(
          (z) => z.kod === item.zrodlo_finansowania_kod
        ) || null;
      const grupaWydatkow =
        grupyWydatkow?.find((g) => g.id === item.grupa_wydatkow_id) || null;

      // For now, we'll use a mock kod zadaniowy since we don't have the mapping
      const kodZadaniowy = kodyZadaniowe?.[0] || null;

      return {
        id: item.id, // Add ID for updates
        dzial,
        rozdzial,
        paragraf,
        grupaWydatkow,
        czescBudzetowa,
        zrodloFinansowania,
        kodZadaniowy,
        nazwaProgramu: item.nazwa_projektu || 'nie dotyczy',
        planWI: item.budzet || 'nie dotyczy',
        roczneSegmenty: [0, 1, 2, 3].map((index) => ({
          year: new Date().getFullYear() + 1 + index,
          potrzebyFinansowe: 0,
          limitWydatków: 0,
          kwotaZawartejUmowy: 0,
          numerUmowy: 'nie dotyczy',
        })),
        dotacjaNumerUmowy: 'nie dotyczy',
        dotacjaPodstawaPrawna: '-',
        uwagi: '-',
      };
    });
  }, [
    planowanieBudzetu,
    dzialy,
    rozdzialy,
    paragrafy,
    grupyWydatkow,
    czesciBudzetowe,
    zrodlaFinansowania,
    kodyZadaniowe,
  ]);

  // Get the first row ID for history status (assuming we want to check history for the first item)
  const firstRowId: number | null =
    budgetDocument.length > 0 && budgetDocument[0].id
      ? budgetDocument[0].id
      : null;
  const { data: fieldsHistoryStatus } = useFieldsHistoryStatus(firstRowId);

  // Map grid field names to backend field names
  const mapFieldToBackend = (field: string): string => {
    const fieldMap: Record<string, string> = {
      czescBudzetowa: 'czesc_budzetowa_kod',
      dzial: 'dzial_kod',
      rozdzial: 'rozdzial_kod',
      paragraf: 'paragraf_kod',
      zrodloFinansowania: 'zrodlo_finansowania_kod',
      grupaWydatkow: 'grupa_wydatkow_id',
      nazwaProgramu: 'nazwa_projektu',
      planWI: 'budzet',
    };
    return fieldMap[field] || field;
  };

  // Handle cell value changes
  const handleCellValueChanged = async (event: any) => {
    const { data, colDef, newValue, oldValue } = event;

    if (newValue === oldValue) return; // No change

    const rowId = data.id;
    if (!rowId) {
      console.error('Row ID not found for update');
      return;
    }

    const field = colDef.field;
    const backendField = mapFieldToBackend(field);

    try {
      // Handle different field types
      let value: string | number | null = newValue;

      // For object fields, extract the kod or id
      if (typeof newValue === 'object' && newValue !== null) {
        if ('kod' in newValue) {
          value = newValue.kod;
        } else if ('id' in newValue) {
          value = newValue.id;
        } else if ('nazwa' in newValue) {
          // For grupa wydatkow, find the id by name
          const grupa = grupyWydatkow?.find((g) => g.nazwa === newValue.nazwa);
          value = grupa?.id || null;
        }
      }

      await updatePlanowanieBudzetuCell(rowId, {
        field: backendField,
        value: value,
      });

      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['planowanie-budzetu'] });

      // Invalidate history queries to refresh history status and data
      queryClient.invalidateQueries({
        queryKey: ['planowanie-budzetu-fields-history-status'],
      });
      queryClient.invalidateQueries({
        queryKey: ['planowanie-budzetu-field-history'],
      });
    } catch (error) {
      console.error('Failed to update cell:', error);
      // You might want to revert the change here or show an error message
    }
  };

  const formatKodAndNazwa = (params: {
    value: { kod: string; nazwa?: string; tresc?: string } | null;
  }) => {
    if (!params?.value) return '';

    return `${params.value.kod} - ${params.value?.nazwa ?? params.value?.tresc}`.trim();
  };

  const renderKodCellWithTooltip = (params: {
    value: { kod: string; nazwa?: string; tresc?: string } | null;
    colDef?: any;
    data?: any;
  }) => {
    if (!params?.value) return '';

    const handleCellClick = () => {
      if (isHistoryMode && params.colDef && params.data) {
        const backendFieldName = mapFieldToBackendFieldName(
          params.colDef.field
        );
        setHistoryModalData({
          field: backendFieldName,
          value: params.value,
          rowId: params.data.id,
        });
      }
    };

    // Check if this field has history
    const backendFieldName = mapFieldToBackendFieldName(
      params.colDef?.field || ''
    );
    const hasHistory = fieldsHistoryStatus?.fields?.[backendFieldName] || false;
    const showHistoryIcon = isHistoryMode && hasHistory;

    return (
      <Tooltip>
        <TooltipTrigger asChild>
          <div
            className={`w-full flex items-center gap-1 ${showHistoryIcon ? 'cursor-pointer hover:bg-blue-50 p-1 rounded' : ''}`}
            onClick={handleCellClick}
          >
            {showHistoryIcon && (
              <History className='h-3 w-3 text-blue-500 shrink-0' />
            )}
            <span className='truncate'>
              {params.value.kod ?? params.value?.nazwa ?? params.value}
            </span>
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

  const renderClickableCellWithTooltip = (params: {
    value: any;
    colDef?: any;
    data?: any;
  }) => {
    const displayValue = params.value || '';

    const handleCellClick = () => {
      if (isHistoryMode && params.colDef && params.data) {
        const backendFieldName = mapFieldToBackendFieldName(
          params.colDef.field
        );
        setHistoryModalData({
          field: backendFieldName,
          value: params.value,
          rowId: params.data.id,
        });
      }
    };

    // Check if this field has history
    const backendFieldName = mapFieldToBackendFieldName(
      params.colDef?.field || ''
    );
    const hasHistory = fieldsHistoryStatus?.fields?.[backendFieldName] || false;
    const showHistoryIcon = isHistoryMode && hasHistory;

    return (
      <div
        className={`w-full flex items-center gap-1 ${showHistoryIcon ? 'cursor-pointer hover:bg-blue-50 p-1 rounded' : ''}`}
        onClick={handleCellClick}
      >
        {showHistoryIcon && (
          <History className='h-3 w-3 text-blue-500 shrink-0' />
        )}
        <span className='truncate'>{displayValue}</span>
      </div>
    );
  };

  const headerStyle = {
    whiteSpace: 'pretty',
    overflow: 'hidden',
    display: '-webkit-box',
    WebkitBoxOrient: 'vertical',
    WebkitLineClamp: 2,
    fontSize: '12px',
  };

  const colDefs: ColDef[] = useMemo(
    () => [
      {
        headerName: 'Część budżetowa',
        field: 'czescBudzetowa' as const,
        editable: !isHistoryMode,
        valueFormatter: formatKodAndNazwa,
        cellRenderer: renderKodCellWithTooltip,
        cellEditor: 'agSelectCellEditor',
        cellEditorParams: {
          values:
            czesciBudzetowe?.sort((a, b) => a.kod.localeCompare(b.kod)) ?? [],
        },
        headerStyle,
      },
      {
        headerName: 'Dział',
        field: 'dzial' as const,
        editable: !isHistoryMode,
        valueFormatter: formatKodAndNazwa,
        cellRenderer: renderKodCellWithTooltip,
        cellEditor: 'agSelectCellEditor',
        cellEditorParams: {
          values: dzialy?.sort((a, b) => a.kod.localeCompare(b.kod)) ?? [],
        },
        headerStyle,
      },
      {
        headerName: 'Rozdział',
        field: 'rozdzial' as const,
        editable: !isHistoryMode,
        cellEditor: 'agSelectCellEditor',
        valueFormatter: formatKodAndNazwa,
        cellRenderer: renderKodCellWithTooltip,
        cellEditorParams: {
          values: rozdzialy?.sort((a, b) => a.kod.localeCompare(b.kod)) ?? [],
        },
        headerStyle,
      },
      {
        headerName: 'Paragraf',
        field: 'paragraf' as const,
        editable: !isHistoryMode,
        cellEditor: 'agSelectCellEditor',
        valueFormatter: formatKodAndNazwa,
        cellRenderer: renderKodCellWithTooltip,
        cellEditorParams: {
          values: paragrafy?.sort((a, b) => a.kod.localeCompare(b.kod)) ?? [],
        },
        headerStyle,
      },
      {
        headerName: 'Źródło finansowania',
        field: 'zrodloFinansowania' as const,
        editable: !isHistoryMode,
        cellEditor: 'agSelectCellEditor',
        valueFormatter: formatKodAndNazwa,
        cellRenderer: renderKodCellWithTooltip,
        cellEditorParams: {
          values:
            zrodlaFinansowania?.sort((a, b) => a.kod.localeCompare(b.kod)) ??
            [],
        },
        headerStyle,
      },
      {
        headerName: 'Grupa wydatków',
        field: 'grupaWydatkow' as const,
        cellRenderer: renderKodCellWithTooltip,
        editable: !isHistoryMode,
        cellEditor: 'agSelectCellEditor',
        cellEditorParams: {
          values: grupyWydatkow?.map((gw) => gw.nazwa).sort() ?? [],
        },
        headerStyle,
      },
      {
        headerName: 'Budżet zadaniowy (w pełnej szczegółowości)',
        field: 'kodZadaniowy' as const,
        cellRenderer: renderKodCellWithTooltip,
        editable: !isHistoryMode,
        cellEditor: 'agSelectCellEditor',
        cellEditorParams: {
          values:
            kodyZadaniowe?.sort((a, b) => a.kod.localeCompare(b.kod)) ?? [],
        },
        headerStyle,
      },
      {
        headerName: 'Budżet zadaniowy (nr funkcji, nr zadania)',
        field: 'kodZadaniowy' as const,
        cellRenderer: (params: {
          value: KodZadaniowy;
          colDef?: any;
          data?: any;
        }) => {
          const backendFieldName = mapFieldToBackendFieldName(
            params.colDef?.field || ''
          );
          const hasHistory =
            fieldsHistoryStatus?.fields?.[backendFieldName] || false;
          const showHistoryIcon = isHistoryMode && hasHistory;

          const handleCellClick = () => {
            if (showHistoryIcon && params.colDef && params.data) {
              setHistoryModalData({
                field: backendFieldName,
                value: params.value?.kod_krotki,
                rowId: params.data.id,
              });
            }
          };

          const displayValue = params.value?.kod_krotki || '';

          return (
            <div
              className={`w-full flex items-center gap-1 ${showHistoryIcon ? 'cursor-pointer hover:bg-blue-50 p-1 rounded' : ''}`}
              onClick={handleCellClick}
            >
              {showHistoryIcon && (
                <History className='h-3 w-3 text-blue-500 shrink-0' />
              )}
              <span className='truncate'>{displayValue}</span>
            </div>
          );
        },
        editable: false,
        headerStyle,
      },
      {
        headerName: 'Nazwa programu',
        field: 'nazwaProgramu' as const,
        editable: !isHistoryMode,
        cellEditor: 'agTextCellEditor',
        cellRenderer: isHistoryMode
          ? renderClickableCellWithTooltip
          : undefined,
        headerStyle,
      },
      {
        headerName: 'Nazwa komórki organizacyjnej',
        editable: false,
        cellRenderer: (params: { colDef?: any; data?: any }) => {
          const backendFieldName = 'komorka_organizacyjna_id'; // This field is not mapped in our function
          const hasHistory =
            fieldsHistoryStatus?.fields?.[backendFieldName] || false;
          const showHistoryIcon = isHistoryMode && hasHistory;

          const handleCellClick = () => {
            if (showHistoryIcon && params.colDef && params.data) {
              setHistoryModalData({
                field: backendFieldName,
                value: user.nazwaKomorkiOrganizacyjnej,
                rowId: params.data.id,
              });
            }
          };

          return (
            <div
              className={`w-full flex items-center gap-1 ${showHistoryIcon ? 'cursor-pointer hover:bg-blue-50 p-1 rounded' : ''}`}
              onClick={handleCellClick}
            >
              {showHistoryIcon && (
                <History className='h-3 w-3 text-blue-500 shrink-0' />
              )}
              <span className='truncate'>
                {user.nazwaKomorkiOrganizacyjnej}
              </span>
            </div>
          );
        },
        headerStyle,
      },
      {
        headerName: 'Plan WI',
        field: 'planWI' as const,
        editable: !isHistoryMode,
        cellEditor: 'agTextCellEditor',
        cellRenderer: isHistoryMode
          ? renderClickableCellWithTooltip
          : undefined,
        headerStyle,
      },
      ...[0, 1, 2, 3].map((index) => ({
        headerName: String(new Date().getFullYear() + 1 + index),
        children: [
          {
            headerName: 'Potrzeby finansowe na rok',
            field: `roczneSegmenty.${index}.potrzebyFinansowe` as const,
            editable: !isHistoryMode,
            cellEditor: 'agNumericCellEditor',
            cellRenderer: isHistoryMode
              ? renderClickableCellWithTooltip
              : undefined,
            cellEditorParams: {
              precision: 2,
            },
            headerStyle: { ...headerStyle, fontSize: '10px' },
          },
          {
            headerName: 'Limit wydatków na rok',
            field: `roczneSegmenty.${index}.limitWydatków` as const,
            editable: !isHistoryMode,
            cellEditor: 'agNumericCellEditor',
            cellRenderer: isHistoryMode
              ? renderClickableCellWithTooltip
              : undefined,
            cellEditorParams: {
              precision: 2,
            },
            headerStyle: { ...headerStyle, fontSize: '10px' },
          },
          {
            headerName:
              'Kwota na realizację zadań w roku, która nie została zabezpieczona w limicie',
            field: `roczneSegmenty.${index}.potrzebyFinansowe` as const,
            editable: false,
            cellEditor: 'agNumericCellEditor',
            cellEditorParams: {
              precision: 2,
            },
            cellRenderer: (params: any) => {
              const calculatedValue =
                params.data.roczneSegmenty[index].potrzebyFinansowe -
                params.data.roczneSegmenty[index].limitWydatków;

              // This is a calculated field, it doesn't have history in backend
              return calculatedValue;
            },
            headerStyle: { ...headerStyle, fontSize: '10px' },
          },
          {
            headerName:
              'Kwota zawartej umowy/wniosku o udzielenie zamówienia publicznego',
            field: `roczneSegmenty.${index}.kwotaZawartejUmowy` as const,
            editable: !isHistoryMode,
            cellEditor: 'agNumericCellEditor',
            cellRenderer: isHistoryMode
              ? renderClickableCellWithTooltip
              : undefined,
            cellEditorParams: {
              precision: 2,
            },
            headerStyle: { ...headerStyle, fontSize: '10px' },
          },
          {
            headerName:
              'Nr umowy/nr wniosku o udzielenie zamówienia publicznego',
            field: `roczneSegmenty.${index}.numerUmowy` as const,
            editable: !isHistoryMode,
            cellEditor: 'agTextCellEditor',
            cellRenderer: isHistoryMode
              ? renderClickableCellWithTooltip
              : undefined,
            headerStyle: { ...headerStyle, fontSize: '10px' },
          },
        ],
      })),
      {
        headerName:
          'Jesli dotacja - z kim zawarta umowa/planowana do zawarcia umowa',
        field: 'dotacjaNumerUmowy' as const,
        editable: true,
        cellEditor: 'agTextCellEditor',
        headerStyle,
      },
      {
        headerName: 'Podstawa prawna udzielenia dotacji',
        field: 'dotacjaPodstawaPrawna' as const,
        editable: true,
        cellEditor: 'agTextCellEditor',
        headerStyle,
      },
      {
        headerName: 'Uwagi',
        field: 'uwagi' as const,
        editable: true,
        cellEditor: 'agTextCellEditor',
        headerStyle,
      },
    ],
    [
      dzialy,
      rozdzialy,
      paragrafy,
      grupyWydatkow,
      czesciBudzetowe,
      zrodlaFinansowania,
      kodyZadaniowe,
      isHistoryMode,
      user,
      fieldsHistoryStatus,
    ]
  );

  const defaultColDef = {
    flex: 1,
  };

  return (
    <div className='relative w-full h-full overflow-auto'>
      <div className='flex justify-between items-center p-4 bg-white'>
        <h2 className='text-lg font-semibold'>Planowanie Budżetu</h2>
        <Button
          variant={isHistoryMode ? 'default' : 'outline'}
          onClick={() => setIsHistoryMode(!isHistoryMode)}
          className='flex items-center gap-2'
        >
          {isHistoryMode ? (
            <>
              <Edit className='h-4 w-4' />
              Tryb edycji
            </>
          ) : (
            <>
              <History className='h-4 w-4' />
              Tryb historii
            </>
          )}
        </Button>
      </div>

      <AgGridReact
        className='min-w-0 overflow-visible w-[4000px]'
        headerHeight={70}
        rowData={budgetDocument}
        columnDefs={colDefs}
        editType='singleCell'
        stopEditingWhenCellsLoseFocus={true}
        onCellEditingStopped={(event) => {}}
        onCellEditingStarted={(event) => {}}
        onCellValueChanged={handleCellValueChanged}
        defaultColDef={defaultColDef}
      />

      <HistoryModal
        isOpen={!!historyModalData}
        onClose={() => setHistoryModalData(null)}
        cellData={historyModalData}
      />
    </div>
  );
};

export default BudgetGrid;
