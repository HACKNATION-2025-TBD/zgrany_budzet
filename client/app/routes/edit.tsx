import { useGridData } from '~/hooks/use-grid-data';
import { useForm } from '@tanstack/react-form';
import { budgetDocumentSchema } from '~/schema';

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
    isLoading: isLoadingGridData,
  } = useGridData();

  const { form } = useForm({
    defaultValues: budgetDocumentSchema.parse([]),
    onSubmit: (values) => {
      console.log('Form submitted with values:', values);
    },
  });

  return (
    <div>
      <h2>Edit Screen</h2>
      <p>This is the edit screen.</p>
    </div>
  );
}
