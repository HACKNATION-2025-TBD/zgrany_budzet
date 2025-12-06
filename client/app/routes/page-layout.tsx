import { Outlet } from 'react-router';

export default function PageLayout() {
  return (
    <div className='max-w-[1440px] mx-auto w-full p-2 lg:px-10 lg:py-8 overflow-hidden'>
      <Outlet />
    </div>
  );
}
