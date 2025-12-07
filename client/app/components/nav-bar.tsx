import { Link } from 'react-router';
import {
  NavigationMenu,
  NavigationMenuLink,
  NavigationMenuList,
} from './ui/navigation-menu';
import MC from '@/assets/mc.png';
import userImg from '@/assets/user.png';
import { useUserMock } from '~/hooks/use-user-mock';

export const NavBar = () => {
  const { user } = useUserMock();

  return (
    <NavigationMenu className='px-12 py-4 border-border border-b w-screen max-w-screen justify-start flex'>
      <Link to='/'>
        <img src={MC} alt='Ministerstwo Cyfryzacji' width={100} />
      </Link>
      <NavigationMenuList className='px-4 border-l border-border ml-4 gap-4'>
        <NavigationMenuLink asChild>
          <Link to='/'>Budżety</Link>
        </NavigationMenuLink>
        <NavigationMenuLink className="hover:opacity-50 hover:cursor-not-allowed pointer-events-none">
          <span>Ustawienia</span>
        </NavigationMenuLink>
      </NavigationMenuList>
      <NavigationMenuLink asChild>
        <div className='ml-auto flex flex-row gap-3 items-center justify-center'>
          <img src={userImg} alt='User' height={45} width={45} />
          <div className='flex gap-1/2 flex-col items-start font-medium text-sm'>
            <span>{user.name}</span>
            <span>{user.email}</span>
          </div>
        </div>
      </NavigationMenuLink>
    </NavigationMenu>
  );
};
