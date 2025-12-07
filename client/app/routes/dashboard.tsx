import { Download, FileLockIcon, FileText } from 'lucide-react';
import BudgetGrid from '~/components/budget-grid';
import { Button } from '~/components/ui/button';
import { useUserMock } from '~/hooks/use-user-mock';

export function meta() {
  return [{ title: 'Dashboard - Budżet' }];
}

export default function Dashboard() {
  const { user } = useUserMock();
  return (
    <div className='p-6 space-y-6'>
      <div className='flex justify-between items-center'>
        <div className='flex flex-row items-center justify-between w-full'>
          <div>
            <h1 className='text-3xl font-bold text-gray-900'>
              Dashboard Budżetowy
            </h1>
            <p className='text-gray-600'>
              Przegląd wykonania budżetu według działów
            </p>
          </div>
          <div className='flex gap-[15px]'>
            {user.role !== 'ko' && (
              <Button onClick={() => {}} size='sm' variant='secondary' disabled>
                <FileLockIcon />
                <span>Zablokuj</span>
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
          </div>
        </div>
      </div>

      <div style={{ height: '500px', border: '1px solid #ddd' }}>
        <BudgetGrid />
      </div>
    </div>
  );
}
