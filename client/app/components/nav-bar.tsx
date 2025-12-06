import { Link } from 'react-router';
import {
  NavigationMenu,
  NavigationMenuLink,
  NavigationMenuList,
} from './ui/navigation-menu';
import MC from '@/assets/mc.png';
import user from '@/assets/user.png';

export const NavBar = () => {
  return (
    <NavigationMenu className='px-12 py-4 border-border border-b w-screen max-w-screen justify-start flex'>
      <img src={MC} alt='Ministerstwo Cyfryzacji' width={100} />
      <NavigationMenuList className='px-4 border-l border-border ml-4 gap-4'>
        <NavigationMenuLink asChild>
          <Link to='/'>Budżety</Link>
        </NavigationMenuLink>
        <NavigationMenuLink asChild>
          <Link to='/'>Ustawienia</Link>
        </NavigationMenuLink>
      </NavigationMenuList>
      <NavigationMenuLink asChild>
        <div className='ml-auto flex flex-row gap-3 items-center justify-center'>
          <img src={user} alt='User' height={45} width={45} />
          <div className='flex gap-1/2 flex-col items-start font-medium text-sm'>
            <span>Joanna Kowalska</span>
            <span>jankow@mc.gov.pl</span>
          </div>
        </div>
      </NavigationMenuLink>
    </NavigationMenu>
  );
};
