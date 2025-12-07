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

      <div  style={{ height: '500px', border: '1px solid #ddd' }}>
        <BudgetGrid />
      </div>
    </div>
  );
}
