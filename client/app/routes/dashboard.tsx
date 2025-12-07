import BudgetGrid from '~/components/budget-grid';

export function meta() {
  return [{ title: 'Dashboard - Budżet' }];
}

export default function Dashboard() {
  return (
    <div className='p-6 space-y-6'>
      <div className='flex justify-between items-center'>
        <div>
          <h1 className='text-3xl font-bold text-gray-900'>
            Dashboard Budżetowy
          </h1>
          <p className='text-gray-600'>
            Przegląd wykonania budżetu według działów
          </p>
        </div>
      </div>

      <div className='bg-white rounded-lg shadow-sm border'>
        <div className='p-4 border-b border-gray-200'>
          <h2 className='text-xl font-semibold text-gray-800'>
            Wykonanie budżetu wg działów
          </h2>
        </div>
        <div className='p-4' style={{ height: '500px' }}>
          <BudgetGrid />
        </div>
      </div>
    </div>
  );
}
