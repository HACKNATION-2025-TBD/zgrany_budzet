import { Outlet, useNavigation } from 'react-router';
import { NavBar } from '~/components/nav-bar';

export default function PageLayout() {
  const navigation = useNavigation();

  return (
    <div className='w-screen h-screen overflow-hidden'>
      {window.location?.pathname !== '/' && <NavBar />}
      <Outlet />
    </div>
  );
}
