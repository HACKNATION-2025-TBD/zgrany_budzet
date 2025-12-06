import { budgetDocumentRowSchema, budgetDocumentSchema } from '~/schema';
import { Button } from '~/components/ui/button';
import { Download, FileText, ListPlusIcon } from 'lucide-react';
import BudgetGrid from '~/components/budget-grid';
import { useState } from 'react';

export function meta() {
  return [{ title: 'Budżety' }];
}

export default function Edit() {
  const [budgetDocument, setBudgetDocument] = useState(
    budgetDocumentSchema.parse([])
  );

  return (
    <div>
      <div className='flex justify-between items-center'>
        <h1 className='font-semibold text-2xl py-6'>Budżety</h1>
        <div className='flex gap-[15px]'>
          <Button onClick={() => {}} size='sm' variant='secondary'>
            <FileText />
            <span>Generuj pismo</span>
          </Button>
          <Button onClick={() => {}} size='sm' variant='secondary'>
            <Download />
            Export
          </Button>
          <Button
            onClick={() => {
              setBudgetDocument((prev) => [
                ...prev,
                budgetDocumentRowSchema.parse({}),
              ]);
            }}
            size='sm'
            variant='secondary'
          >
            <ListPlusIcon />
            Dodaj nowy wiersz
          </Button>
        </div>
      </div>

      <div className='bg-white rounded-lg shadow-sm border'>
        <div className='p-4 border-b border-gray-200'>tutaj filtry</div>
        <div className='p-4' style={{ height: '500px' }}>
          <BudgetGrid budgetDocument={budgetDocument} />
        </div>
      </div>
    </div>
  );
}
