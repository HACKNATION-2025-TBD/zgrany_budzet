import { Link } from 'react-router';
import MC from '@/assets/mc.png';
import { Button } from '@/components/ui/button';

export function meta() {
  return [{ title: 'Login' }];
}

export default function Login() {
  return (
    <div>
      <header className='p-4 border-b border-gov-gray-500'>
        <img src={MC} alt='Ministerstwo Cyfryzacji' width={150} />
      </header>
      <h1 className='font-semibold text-2xl py-6'>Zaloguj się do usługi</h1>
      <p className='text-gov-gray-500'>Wybierz rolę:</p>
      <nav className='flex flex-col gap-4 py-4'>
        <Link to='/dashboard'>
          <Button>Kierownictwo</Button>
        </Link>
        <Link to='/edit'>
          <Button>Komórki organizacyjne</Button>
        </Link>
      </nav>
    </div>
  );
}
