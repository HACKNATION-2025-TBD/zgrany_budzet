

import { usePost } from '../queries';

export function meta() {
  return [{ title: 'Dashboard' }];
}

export default function Dashboard() {
  const { data: posts, isLoading, isError, error } = usePost();

  if (isLoading) {
    console.log('is loading');
  }

  if (isError) {
    console.log('Error loading dashboard data:', error);
  }

  if (posts) {
    console.log('Dashboard data:', posts);
  }

  return (
    <div>
      <h2>Dashboard</h2>
      <p>This is the dashboard screen.</p>
    </div>
  );
}
