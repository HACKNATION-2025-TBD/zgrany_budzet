import { useGridData } from '~/hooks/use-grid-data';
import { useForm } from '@tanstack/react-form';
import { budgetDocumentSchema } from '~/schema';
import { Button } from '~/components/ui/button';
import { Download, FileText, ListPlusIcon } from 'lucide-react';

export function meta() {
  return [{ title: 'Budżety' }];
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
      <div className='flex justify-between items-center'>
        <h1 className='font-semibold text-2xl py-6'>Budżety</h1>
        <div className='flex gap-[15px]'>
          <Button onClick={() => form.submit()} size='sm' variant='secondary'>
            <FileText />
            <span>Generuj pismo</span>
          </Button>
          <Button onClick={() => form.submit()} size='sm' variant='secondary'>
            <Download />
            Export
          </Button>
          <Button onClick={() => form.submit()} size='sm' variant='secondary'>
            <ListPlusIcon />
            Dodaj nowy wiersz
          </Button>
        </div>
      </div>
      <p>This is the edit screen.</p>
    </div>
  );
}
