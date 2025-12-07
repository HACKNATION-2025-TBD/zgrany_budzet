import MC from '@/assets/mc.png';
import LoginImage from '@/assets/login.png';
import { Landmark, HandCoins, BanknoteArrowUp } from 'lucide-react';
import { RoleCard } from '@/components/role-card';
import { useUserMock } from '~/hooks/use-user-mock';

export function meta() {
  return [{ title: 'Login' }];
}

export default function Login() {
  const { setUserType } = useUserMock();

  return (
    <div className='grid grid-cols-2 gap-4'>
      <div>
        <header className='p-4 border-b border-secondary-foreground'>
          <img src={MC} alt='Ministerstwo Cyfryzacji' width={150} />
        </header>
        <h1 className='font-semibold text-2xl py-6'>Zaloguj się do usługi</h1>
        <p className='text-secondary-foreground'>Wybierz rolę:</p>
        <nav className='flex flex-col gap-4 py-4 mr-8'>
          <RoleCard
            to='/dashboard'
            icon={BanknoteArrowUp}
            title='Kierownictwo'
            description='Komórka organizacyjna MC odpowiedzialna za planowanie budżetu'
            onClick={() => setUserType('kierownictwo')}
          />
          <RoleCard
            to='/dashboard'
            icon={HandCoins}
            title='Biuro Budżetowo Finansowe'
            description='Kierownictwo Ministerstwa Cyfryzacji'
            onClick={() => setUserType('bbf')}
          />  
          <RoleCard
            to='/dashboard/1'
            icon={Landmark}
            title='Komórki organizacyjne'
            description='Departamenty i biura'
            onClick={() => setUserType('ko')}
          />
        </nav>
      </div>
      <img
        src={LoginImage}
        alt='login image'
        className='rounded-lg h-[80vh] object-cover object-center'
      />
    </div>
  );
}
