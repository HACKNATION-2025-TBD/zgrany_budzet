import { budgetDocumentSchema } from '~/schema';
import { Button } from '~/components/ui/button';
import {
  Download,
  FileLockIcon,
  FileText,
  History,
  ListPlusIcon,
} from 'lucide-react';
import BudgetGrid from '~/components/budget-grid';
import { useState } from 'react';
import { useUserMock } from '~/hooks/use-user-mock';
import { NewBudgetDocumentRowModal } from '~/modals/new-budget-document-row-modal';

export function meta() {
  return [{ title: 'Budżety' }];
}

export default function Edit() {
  const { user } = useUserMock();
  const [budgetDocument, setBudgetDocument] = useState(
    budgetDocumentSchema.parse([])
  );

  return (
    <div>
      <div className='flex justify-between items-center mb-6'>
        <div >
          <h1 className='text-3xl font-bold text-gray-900'>
            Dashboard Budżetowy
          </h1>
          <p className='text-gray-600'>
            Przegląd wykonania budżetu według konkretnego działu
          </p>
        </div>
        <div className='flex gap-[15px]'>
          {user.role !== 'ko' && (
            <Button onClick={() => {}} size='sm' variant='secondary'>
              <FileLockIcon />
              <span>Zablokuj</span>
            </Button>
          )}
          {user.role !== 'ko' && (
            <Button onClick={() => {}} size='sm' variant='secondary'>
              <History />
              <span>Wersje</span>
            </Button>
          )}
          {user.role !== 'ko' && (
            <Button onClick={() => {}} size='sm' variant='secondary'>
              <FileText />
              <span>Generuj pismo</span>
            </Button>
          )}
          {user.role !== 'ko' && (
            <Button onClick={() => {}} size='sm' variant='secondary'>
              <Download />
              Export
            </Button>
          )}
          <NewBudgetDocumentRowModal
            onAdd={(newRow) => setBudgetDocument((prev) => [...prev, newRow])}
          >
            <Button size='sm' variant='secondary'>
              <ListPlusIcon />
              Dodaj nowy wiersz
            </Button>
          </NewBudgetDocumentRowModal>
        </div>
      </div>
      <div  style={{ height: '500px', border: '1px solid #ddd' }}>
          <BudgetGrid />
        </div>
    </div>
  );
}
