import { Link } from 'react-router';

export function meta() {
  return [{ title: 'Login' }];
}

export default function Login() {
  return (
    <div>
      <h2>Login Screen</h2>
      <p>Login to access your dashboard and edit screen.</p>
      <nav>
        <Link to='/dashboard'>Go to Dashboard</Link>
        <br />
        <Link to='/edit'>Go to Edit Screen</Link>
      </nav>
    </div>
  );
}
