import { type RouteConfig, index, route } from '@react-router/dev/routes';

export default [
  route('', 'routes/navbar-layout.tsx', [
    route('', 'routes/page-layout.tsx', [
      index('routes/login.tsx'),
      route('dashboard', 'routes/dashboard.tsx'),
      route('dashboard/:id', 'routes/edit.tsx'),
    ]),
  ]),
] satisfies RouteConfig;
