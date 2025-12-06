import { Link } from 'react-router';
import {
  NavigationMenu,
  NavigationMenuLink,
  NavigationMenuList,
} from './ui/navigation-menu';
import MC from '@/assets/mc.png';

export const NavBar = () => {
  return (
    <NavigationMenu>
      <img src={MC} alt='Ministerstwo Cyfryzacji' width={100} />
      <NavigationMenuList>
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
