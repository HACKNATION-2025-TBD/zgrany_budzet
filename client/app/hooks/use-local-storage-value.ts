const createStorageValueHook = (storageType: 'local' | 'session' = 'local') => {
  const storage = storageType === 'local' ? localStorage : sessionStorage;

  return <T>(key: string, initialValue: T) => {
    const getValue = () => {
      const saved = storage.getItem(key);
      if (!saved) {
        setValue(initialValue);
        return initialValue;
      }

      return JSON.parse(saved) as T;
    };

    const setValue = (value: T) => {
      storage.setItem(key, JSON.stringify(value));
    };

    return [getValue(), setValue] as const;
  };
};

export const useLocalStorageValue = createStorageValueHook('local');
export const useSessionStorageValue = createStorageValueHook('session');
