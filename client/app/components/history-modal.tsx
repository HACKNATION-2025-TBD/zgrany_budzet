import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Clock, User, Edit } from 'lucide-react';
import { useFieldHistory } from '~/hooks/use-field-history';

interface HistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  cellData: {
    field: string;
    value: any;
    rowId: number;
  } | null;
}

const HistoryModal = ({ isOpen, onClose, cellData }: HistoryModalProps) => {
  const { data: historyData, isLoading } = useFieldHistory(
    cellData?.rowId || null, 
    cellData?.field || null
  );

  const formatFieldName = (field: string): string => {
    const fieldNameMap: Record<string, string> = {
      'czesc_budzetowa_kod': 'Część budżetowa',
      'dzial_kod': 'Dział',
      'rozdzial_kod': 'Rozdział',
      'paragraf_kod': 'Paragraf',
      'zrodlo_finansowania_kod': 'Źródło finansowania',
      'grupa_wydatkow_id': 'Grupa wydatków',
      'nazwa_projektu': 'Nazwa programu',
      'budzet': 'Plan WI',
      'nazwa_zadania': 'Nazwa zadania',
      'szczegolowe_uzasadnienie_realizacji': 'Szczegółowe uzasadnienie realizacji',
    };
    return fieldNameMap[field] || field;
  };

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) {
      return 'Puste';
    }
    if (typeof value === 'object' && value.kod) {
      return `${value.kod} - ${value.nazwa || value.tresc || ''}`;
    }
    return String(value);
  };

  const formatTimestamp = (timestamp: string): string => {
    return new Date(timestamp).toLocaleString('pl-PL', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Historia zmian - {cellData ? formatFieldName(cellData.field) : ''}
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4 overflow-y-auto max-h-96">
          {isLoading ? (
            <div className="text-center py-8 text-gray-500">
              <Clock className="h-6 w-6 mx-auto mb-2 animate-spin" />
              Ładowanie historii...
            </div>
          ) : !historyData?.history || historyData.history.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Brak historii zmian dla tego pola
            </div>
          ) : (
            historyData.history.map((entry, index) => {
              const prevEntry = historyData.history[index + 1];
              const isFirstEntry = index === historyData.history.length - 1;
              
              return (
                <div
                  key={`${entry.timestamp}-${index}`}
                  className="border rounded-lg p-4 space-y-3 bg-white shadow-sm"
                >
                  <div className="flex items-center justify-between">
                    <span className="bg-blue-100 text-blue-800 flex items-center gap-1 px-2 py-1 rounded text-xs font-medium">
                      <Edit className="h-3 w-3" />
                      {isFirstEntry ? 'Utworzono' : 'Edytowano'}
                    </span>
                    <span className="text-sm text-gray-500">
                      {formatTimestamp(entry.timestamp)}
                    </span>
                  </div>
                  
                  <div className="space-y-2">
                    {!isFirstEntry ? (
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <span className="text-xs font-medium text-gray-600 uppercase tracking-wide">
                            Poprzednia wartość
                          </span>
                          <div className="mt-1 p-2 bg-red-50 border border-red-200 rounded text-sm">
                            {prevEntry ? formatValue(prevEntry.value) : <em className="text-gray-400">Puste</em>}
                          </div>
                        </div>
                        <div>
                          <span className="text-xs font-medium text-gray-600 uppercase tracking-wide">
                            Nowa wartość
                          </span>
                          <div className="mt-1 p-2 bg-green-50 border border-green-200 rounded text-sm">
                            {formatValue(entry.value)}
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div>
                        <span className="text-xs font-medium text-gray-600 uppercase tracking-wide">
                          Wartość początkowa
                        </span>
                        <div className="mt-1 p-2 bg-green-50 border border-green-200 rounded text-sm">
                          {formatValue(entry.value)}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default HistoryModal;
