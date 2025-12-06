import { useLocalStorageValue } from './use-local-storage-value';

const userMockData = {
  kierownictwo: {
    name: 'Joanna Kowalska',
    role: 'Kierownictwo',
    email: 'joakow@mc.gov.pl',
  },
  bbf: {
    name: 'Beata Fąk',
    role: 'Biuro Budżetowo-Finansowe',
    email: 'annnow@mc.gov.pl',
  },
  ko: {
    name: 'Karolina Olycz',
    role: 'Komórki organizacyjne',
    email: 'karoly@mc.gov.pl',
  },
} as Record<UserType, { name: string; role: string; email: string }>;

export type UserType = 'kierownictwo' | 'bbf' | 'ko';

export function useUserMock() {
  const [userType, setUserType] = useLocalStorageValue<UserType>(
    'userType',
    'ko'
  );

  return { setUserType, user: userMockData[userType] };
}
