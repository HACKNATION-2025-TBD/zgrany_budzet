import { useDzialy } from '~/queries';

export function meta() {
  return [{ title: 'Dashboard' }];
}

export default function Dashboard() {
  const { data: dzialy, isLoading, isError, error } = useDzialy();

  if (isLoading) {
    console.log('is loading');
  }

  if (isError) {
    console.log('Error loading dashboard data:', error);
  }

  return (
    <div>
      <h2>Dashboard</h2>
      <p>This is the dashboard screen.</p>
    </div>
  );
}
