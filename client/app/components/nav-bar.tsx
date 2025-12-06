import { Link } from 'react-router';
import {
  NavigationMenu,
  NavigationMenuLink,
  NavigationMenuList,
} from './ui/navigation-menu';
import MC from '@/assets/mc.png';

export const NavBar = () => {
  return (
    <NavigationMenu className='px-12 py-4 border-border border-b w-screen max-w-screen justify-start flex'>
      <img src={MC} alt='Ministerstwo Cyfryzacji' width={100} />
      <NavigationMenuList className='px-4 border-l border-border ml-4'>
        <NavigationMenuLink asChild>
          <Link to='/'>Budżety</Link>
        </NavigationMenuLink>
        <NavigationMenuLink asChild>
          <Link to='/'>Ustawienia</Link>
        </NavigationMenuLink>
      </NavigationMenuList>
    </NavigationMenu>
  );
};
