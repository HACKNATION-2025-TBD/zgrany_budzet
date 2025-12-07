import { useEffect, useState, type PropsWithChildren } from 'react';
import { Button } from '~/components/ui/button';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '~/components/ui/dialog';
import { useForm, type AnyFieldApi } from '@tanstack/react-form';
import { budgetDocumentRowSchema, type DocumentRow } from '~/schema';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '~/components/ui/select';
import { useGridData } from '~/hooks/use-grid-data';
import {
  Field,
  FieldDescription,
  FieldError,
  FieldLabel,
} from '~/components/ui/field';
import { Input } from '~/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '~/components/ui/tabs';

const schema = budgetDocumentRowSchema.required().superRefine((data, ctx) => {
  Object.entries(data).forEach(([key, value]) => {
    if (value === null || value === undefined || value === '') {
      ctx.addIssue({
        code: 'custom',
        message: `Pole jest wymagane.`,
        path: [key],
      });
    }
  });

  if (data.rozdzial && data.dzial && data.rozdzial.dzial !== data.dzial.kod) {
    ctx.addIssue({
      code: 'custom',
      message: 'Rozdział nie należy do wybranego działu.',
      path: ['rozdzial'],
    });
  }

  if (data.paragraf && data.grupaWydatkow && data.zrodloFinansowania) {
    if (Array.isArray(data.grupaWydatkow.paragrafy)) {
      if (!data.grupaWydatkow.paragrafy.includes(data.paragraf.kod)) {
        ctx.addIssue({
          code: 'custom',
          message: 'Paragraf nie należy do wybranej grupy wydatków.',
          path: ['paragraf'],
        });
      }
    } else {
      if (
        !['1', '2', '5', '6', '7', '8', '9'].includes(
          data.zrodloFinansowania?.kod
        )
      ) {
        ctx.addIssue({
          code: 'custom',
          message:
            'Źródło finansowania nie jest zgodne z wybraną grupą wydatków.',
          path: ['zrodloFinansowania'],
        });
      }
    }
  }
});

type NewBudgetDocumentRowModalProps = {
  onAdd?: (row: DocumentRow) => void;
};

export const NewBudgetDocumentRowModal = ({
  children,
  onAdd,
}: PropsWithChildren<NewBudgetDocumentRowModalProps>) => {
  const [open, setOpen] = useState(false);
  const {
    dzialy,
    rozdzialy,
    paragrafy,
    grupyWydatkow,
    czesciBudzetowe,
    zrodlaFinansowania,
    kodyZadaniowe,
    isLoading: isLoadingGridData,
  } = useGridData();

  const form = useForm({
    defaultValues: budgetDocumentRowSchema.parse({}),
    onSubmit: (values) => {
      onAdd?.(values.value);
      setOpen(false);
      form.reset();
    },
    validators: {
      onChange: schema,
    },
  });

  useEffect(() => {
    if (!open) {
      form.reset();
    }
  }, [open, form]);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className='max-h-[90vh] min-h-0 max-w-[100vw]! w-[1200px] min-w-0 overflow-auto'>
        <DialogHeader>
          <DialogTitle>Dodaj nowy wiersz</DialogTitle>
          <DialogClose />
        </DialogHeader>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            e.stopPropagation();
            form.handleSubmit();
          }}
          className='overflow-auto! grid grid-cols-3 gap-4'
        >
          <form.Field name='czescBudzetowa'>
            {(field) => (
              <Field>
                <FieldLabel htmlFor='input-id'>Część budżetowa</FieldLabel>
                <Select
                  name='czescBudzetowa'
                  onValueChange={(kod) => {
                    const selectedCzescBudzetowa = czesciBudzetowe?.find(
                      (czescBudzetowa) => czescBudzetowa.kod === kod
                    );
                    if (selectedCzescBudzetowa)
                      field.handleChange(selectedCzescBudzetowa);
                  }}
                  value={field.state.value?.kod}
                >
                  <SelectTrigger disabled={isLoadingGridData}>
                    <SelectValue placeholder='Wybierz część budżetową'>
                      {field.state.value?.kod ?? ''}
                    </SelectValue>
                  </SelectTrigger>
                  <SelectContent>
                    {czesciBudzetowe?.map((czescBudzetowa) => (
                      <SelectItem
                        key={czescBudzetowa.kod}
                        value={czescBudzetowa.kod}
                      >
                        {czescBudzetowa?.kod} -{' '}
                        {czescBudzetowa?.nazwa.substring(0, 50)}
                        {czescBudzetowa?.nazwa.length > 50 ? '...' : ''}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FieldDescription className='text-xs'>
                  {field.state.value?.nazwa}
                </FieldDescription>
                <FieldError>
                  <FieldInfo field={field} />
                </FieldError>
              </Field>
            )}
          </form.Field>

          <form.Field name='dzial'>
            {(field) => (
              <Field>
                <FieldLabel htmlFor='input-id'>Dział</FieldLabel>
                <Select
                  name='dzial'
                  onValueChange={(kod) => {
                    const selectedDzial = dzialy?.find(
                      (dzial) => dzial.kod === kod
                    );
                    if (selectedDzial) field.handleChange(selectedDzial);
                  }}
                  value={field.state.value?.kod}
                >
                  <SelectTrigger disabled={isLoadingGridData}>
                    <SelectValue placeholder='Wybierz dział'>
                      {field.state.value?.kod ?? ''}
                    </SelectValue>
                  </SelectTrigger>
                  <SelectContent>
                    {dzialy?.map((dzial) => (
                      <SelectItem key={dzial.kod} value={dzial.kod}>
                        {dzial?.kod} - {dzial?.nazwa.substring(0, 50)}
                        {dzial?.nazwa.length > 50 ? '...' : ''}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FieldDescription className='text-xs'>
                  {field.state.value?.nazwa}
                </FieldDescription>
                <FieldError>
                  <FieldInfo field={field} />
                </FieldError>
              </Field>
            )}
          </form.Field>

          <form.Field name='rozdzial'>
            {(field) => (
              <Field>
                <FieldLabel htmlFor='input-id'>Rozdział</FieldLabel>
                <Select
                  name='rozdzial'
                  onValueChange={(kod) => {
                    const selectedRozdzial = rozdzialy?.find(
                      (rozdzial) => rozdzial.kod === kod
                    );
                    if (selectedRozdzial) field.handleChange(selectedRozdzial);
                  }}
                  value={field.state.value?.kod}
                >
                  <SelectTrigger disabled={isLoadingGridData}>
                    <SelectValue placeholder='Wybierz rozdział'>
                      {field.state.value?.kod ?? ''}
                    </SelectValue>
                  </SelectTrigger>
                  <SelectContent>
                    {rozdzialy?.map((rozdzial) => (
                      <SelectItem key={rozdzial.kod} value={rozdzial.kod}>
                        {rozdzial?.kod} - {rozdzial?.nazwa.substring(0, 50)}
                        {rozdzial?.nazwa.length > 50 ? '...' : ''}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FieldDescription className='text-xs'>
                  {field.state.value?.nazwa}
                </FieldDescription>
                <FieldError>
                  <FieldInfo field={field} />
                </FieldError>
              </Field>
            )}
          </form.Field>

          <form.Field name='paragraf'>
            {(field) => (
              <Field>
                <FieldLabel htmlFor='input-id'>Paragraf</FieldLabel>
                <Select
                  name='paragraf'
                  onValueChange={(kod) => {
                    const selectedParagraf = paragrafy?.find(
                      (paragraf) => paragraf.kod === kod
                    );
                    if (selectedParagraf) field.handleChange(selectedParagraf);
                  }}
                  value={field.state.value?.kod}
                >
                  <SelectTrigger disabled={isLoadingGridData}>
                    <SelectValue placeholder='Wybierz paragraf'>
                      {field.state.value?.kod ?? ''}
                    </SelectValue>
                  </SelectTrigger>
                  <SelectContent>
                    {paragrafy?.map((paragraf) => (
                      <SelectItem key={paragraf.kod} value={paragraf.kod}>
                        {paragraf?.kod} - {paragraf?.tresc.substring(0, 50)}
                        {paragraf?.tresc.length > 50 ? '...' : ''}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FieldDescription className='text-xs'>
                  {field.state.value?.tresc}
                </FieldDescription>
                <FieldError>
                  <FieldInfo field={field} />
                </FieldError>
              </Field>
            )}
          </form.Field>

          <form.Field name='zrodloFinansowania'>
            {(field) => (
              <Field>
                <FieldLabel htmlFor='input-id'>Źródło finansowania</FieldLabel>
                <Select
                  name='zrodloFinansowania'
                  onValueChange={(kod) => {
                    const selectedZrodloFinansowania = zrodlaFinansowania?.find(
                      (zrodlo) => zrodlo.kod === kod
                    );
                    if (selectedZrodloFinansowania)
                      field.handleChange(selectedZrodloFinansowania);
                  }}
                  value={field.state.value?.kod}
                >
                  <SelectTrigger disabled={isLoadingGridData}>
                    <SelectValue placeholder='Wybierz źródło finansowania'>
                      {field.state.value?.kod ?? ''}
                    </SelectValue>
                  </SelectTrigger>
                  <SelectContent>
                    {zrodlaFinansowania?.map((zrodlo) => (
                      <SelectItem key={zrodlo.kod} value={zrodlo.kod}>
                        {zrodlo?.kod} - {zrodlo?.nazwa}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FieldDescription className='text-xs'>
                  {field.state.value?.nazwa}
                </FieldDescription>
                <FieldError>
                  <FieldInfo field={field} />
                </FieldError>
              </Field>
            )}
          </form.Field>

          <form.Field name='grupaWydatkow'>
            {(field) => (
              <Field>
                <FieldLabel htmlFor='input-id'>Grupa wydatków</FieldLabel>
                <Select
                  name='grupaWydatkow'
                  onValueChange={(nazwa) => {
                    const selectedGrupaWydatkow = grupyWydatkow?.find(
                      (grupa) => grupa.nazwa === nazwa
                    );
                    if (selectedGrupaWydatkow)
                      field.handleChange(selectedGrupaWydatkow);
                  }}
                  value={field.state.value?.nazwa}
                >
                  <SelectTrigger disabled={isLoadingGridData}>
                    <SelectValue placeholder='Wybierz grupę wydatków'>
                      {field.state.value?.nazwa ?? ''}
                    </SelectValue>
                  </SelectTrigger>
                  <SelectContent>
                    {grupyWydatkow?.map((grupa) => (
                      <SelectItem key={grupa.nazwa} value={grupa.nazwa}>
                        {grupa?.nazwa.substring(0, 50)}
                        {grupa?.nazwa.length > 50 ? '...' : ''}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FieldDescription className='text-xs'>
                  {field.state.value?.nazwa}
                </FieldDescription>
                <FieldError>
                  <FieldInfo field={field} />
                </FieldError>
              </Field>
            )}
          </form.Field>

          <form.Field name='kodZadaniowy'>
            {(field) => (
              <Field>
                <FieldLabel htmlFor='input-id'>
                  Budżet zadaniowy (w pełnej szczegółowości)
                </FieldLabel>
                <Select
                  name='kodZadaniowy'
                  onValueChange={(kod) => {
                    const selectedKodZadaniowy = kodyZadaniowe?.find(
                      (kodZadaniowy) => kodZadaniowy.kod === kod
                    );
                    if (selectedKodZadaniowy)
                      field.handleChange(selectedKodZadaniowy);
                  }}
                  value={field.state.value?.nazwa}
                >
                  <SelectTrigger disabled={isLoadingGridData}>
                    <SelectValue placeholder='Wybierz kod zadaniowy'>
                      {field.state.value?.kod ?? ''}
                    </SelectValue>
                  </SelectTrigger>
                  <SelectContent>
                    {kodyZadaniowe?.map((kodZadaniowy) => (
                      <SelectItem
                        key={kodZadaniowy.kod}
                        value={kodZadaniowy.kod}
                      >
                        {kodZadaniowy?.kod} -{' '}
                        {kodZadaniowy?.nazwa.substring(0, 50)}
                        {kodZadaniowy?.nazwa.length > 50 ? '...' : ''}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FieldDescription className='text-xs'>
                  {field.state.value?.nazwa}
                </FieldDescription>
                <FieldError>
                  <FieldInfo field={field} />
                </FieldError>
              </Field>
            )}
          </form.Field>

          <form.Field name='nazwaProgramu'>
            {(field) => (
              <Field>
                <FieldLabel htmlFor='input-id'>Nazwa programu</FieldLabel>
                <Input
                  name='nazwaProgramu'
                  placeholder='Wprowadz nazwę programu'
                  value={field.state.value ?? ''}
                  onChange={(e) => field.handleChange(e.target.value)}
                />
                <FieldError>
                  <FieldInfo field={field} />
                </FieldError>
              </Field>
            )}
          </form.Field>

          <form.Field name='planWI'>
            {(field) => (
              <Field>
                <FieldLabel htmlFor='input-id'>Plan WI</FieldLabel>
                <Input
                  name='planWI'
                  placeholder='Wprowadź plan WI'
                  value={field.state.value ?? ''}
                  onChange={(e) => field.handleChange(e.target.value)}
                />
                <FieldError>
                  <FieldInfo field={field} />
                </FieldError>
              </Field>
            )}
          </form.Field>

          <Tabs
            defaultValue={String(form.state.values.roczneSegmenty[0].year)}
            className='col-span-3 w-full mx-auto border border-card-foreground rounded-md p-4'
          >
            <TabsList className='gap-10 border-boerder mb-4'>
              {form.state.values.roczneSegmenty.map((segment) => (
                <TabsTrigger key={segment.year} value={String(segment.year)}>
                  {segment.year}
                </TabsTrigger>
              ))}
            </TabsList>
            {form.state.values.roczneSegmenty.map((segment) => (
              <TabsContent
                key={segment.year}
                value={String(segment.year)}
                className='grid grid-cols-2 gap-x-8 gap-y-4'
              >
                <form.Field
                  name={`roczneSegmenty[${form.state.values.roczneSegmenty.findIndex((s) => s.year === segment.year)}].potrzebyFinansowe`}
                >
                  {(field) => (
                    <Field>
                      <FieldLabel htmlFor='input-id'>
                        Potrzeby finansowe na rok {segment.year}
                      </FieldLabel>
                      <Input
                        name={`roczneSegmenty[${form.state.values.roczneSegmenty.findIndex((s) => s.year === segment.year)}].potrzebyFinansowe`}
                        type='number'
                        placeholder='Wprowadź potrzeby finansowe'
                        value={field.state.value ?? 0}
                        onChange={(e) => field.handleChange(+e.target.value)}
                      />
                      <FieldError>
                        <FieldInfo field={field} />
                      </FieldError>
                    </Field>
                  )}
                </form.Field>

                <form.Field
                  name={`roczneSegmenty[${form.state.values.roczneSegmenty.findIndex((s) => s.year === segment.year)}].limitWydatków`}
                >
                  {(field) => (
                    <Field>
                      <FieldLabel htmlFor='input-id'>
                        Limit wydatków na rok {segment.year}
                      </FieldLabel>
                      <Input
                        name={`roczneSegmenty[${form.state.values.roczneSegmenty.findIndex((s) => s.year === segment.year)}].limitWydatków`}
                        type='number'
                        placeholder='Wprowadź limit wydatków'
                        value={field.state.value ?? 0}
                        onChange={(e) => field.handleChange(+e.target.value)}
                      />
                      <FieldError>
                        <FieldInfo field={field} />
                      </FieldError>
                    </Field>
                  )}
                </form.Field>

                <form.Field
                  name={`roczneSegmenty[${form.state.values.roczneSegmenty.findIndex((s) => s.year === segment.year)}].kwotaZawartejUmowy`}
                >
                  {(field) => (
                    <Field>
                      <FieldLabel htmlFor='input-id'>
                        Kwota zawartej umowy/wniosku o udzielenie zamówienia
                        publicznego
                      </FieldLabel>
                      <Input
                        name={`roczneSegmenty[${form.state.values.roczneSegmenty.findIndex((s) => s.year === segment.year)}].kwotaZawartejUmowy`}
                        type='number'
                        placeholder='Wprowadź kwotę zawartej umowy'
                        value={field.state.value ?? 0}
                        onChange={(e) => field.handleChange(+e.target.value)}
                      />
                      <FieldError>
                        <FieldInfo field={field} />
                      </FieldError>
                    </Field>
                  )}
                </form.Field>

                <form.Field
                  name={`roczneSegmenty[${form.state.values.roczneSegmenty.findIndex((s) => s.year === segment.year)}].numerUmowy`}
                >
                  {(field) => (
                    <Field>
                      <FieldLabel htmlFor='input-id'>
                        Nr umowy/nr wniosku o udzielenie zamówienia publicznego
                      </FieldLabel>
                      <Input
                        name={`roczneSegmenty[${form.state.values.roczneSegmenty.findIndex((s) => s.year === segment.year)}].numerUmowy`}
                        placeholder='Wprowadź numer umowy'
                        value={field.state.value ?? ''}
                        onChange={(e) => field.handleChange(e.target.value)}
                      />
                      <FieldError>
                        <FieldInfo field={field} />
                      </FieldError>
                    </Field>
                  )}
                </form.Field>
              </TabsContent>
            ))}
          </Tabs>
        </form>

        <DialogFooter>
          <Button
            type='submit'
            className='w-30'
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              form.handleSubmit();
            }}
            disabled={isLoadingGridData || !form.state.isValid}
          >
            Dodaj
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

function FieldInfo({ field }: { field: AnyFieldApi }) {
  return (
    <>
      {field.state.meta.isTouched && !field.state.meta.isValid ? (
        <em>{field.state.meta.errors.map((err) => err.message).join(',')}</em>
      ) : null}
    </>
  );
}
