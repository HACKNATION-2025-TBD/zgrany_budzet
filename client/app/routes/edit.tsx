import { useGridData } from '~/hooks/use-grid-data';

export function meta() {
  return [{ title: 'Edit' }];
}

export default function Edit() {
  const {
    dzialy,
    rozdzialy,
    paragrafy,
    grupyWydatkow,
    czesciBudzetowe,
    isLoading,
  } = useGridData();

  if (!isLoading) {
    console.log({
      dzialy,
      rozdzialy,
      paragrafy,
      grupyWydatkow,
      czesciBudzetowe,
    });
  }

  return (
    <div>
      <h2>Edit Screen</h2>
      <p>This is the edit screen.</p>
    </div>
  );
}
