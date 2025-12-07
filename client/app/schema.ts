import { z } from 'zod';

export const dzialSchema = z.object({
  kod: z.string(),
  nazwa: z.string(),
  PKD: z.string(),
});

export const rozdzialSchema = z.object({
  kod: z.string(),
  nazwa: z.string(),
  dzial: z.string(),
});

export const paragrafSchema = z.object({
  kod: z.string(),
  tresc: z.string(),
});

export const grupaWydatkowSchema = z.object({
  id: z.number(),
  nazwa: z.string(),
  paragrafy: z.union([z.array(z.string()), z.string()]),
});

export const czescBudzetowaSchema = z.object({
  kod: z.string(),
  nazwa: z.string(),
});

export const zrodloFinansowaniaSchema = z.object({
  kod: z.string(),
  nazwa: z.string(),
  opis: z.string().optional(),
});

export const kodZadaniowySchema = z.object({
  kod: z.string(),
  kod_krotki: z.string(),
  nazwa: z.string(),
});

export const budgetDocumentRowYearlySegmentSchema = z.object({
  year: z.number().default(new Date().getFullYear()),
  potrzebyFinansowe: z.number().default(0),
  limitWydatków: z.number().default(0),
  kwotaZawartejUmowy: z.number().default(0),
  numerUmowy: z.string().default('nie dotyczy'),
});

export const budgetDocumentRowSchema = z.object({
  dzial: dzialSchema.nullable().default(null),
  rozdzial: rozdzialSchema.nullable().default(null),
  paragraf: paragrafSchema.nullable().default(null),
  grupaWydatkow: grupaWydatkowSchema.nullable().default(null),
  czescBudzetowa: czescBudzetowaSchema.nullable().default(null),
  zrodloFinansowania: zrodloFinansowaniaSchema.nullable().default(null),
  kodZadaniowy: kodZadaniowySchema.nullable().default(null),
  nazwaProgramu: z.string().default('nie dotyczy'),
  planWI: z.string().default('nie dotyczy'),
  roczneSegmenty: z
    .array(budgetDocumentRowYearlySegmentSchema)
    .length(4)
    .default(() => {
      const nextYear = new Date().getFullYear() + 1;
      return new Array(4)
        .fill(null)
        .map((_, index) =>
          budgetDocumentRowYearlySegmentSchema.parse({ year: nextYear + index })
        );
    }),
});

export const budgetDocumentSchema = z.array(budgetDocumentRowSchema);

export type Dzial = z.infer<typeof dzialSchema>;
export type Rozdzial = z.infer<typeof rozdzialSchema>;
export type Paragraf = z.infer<typeof paragrafSchema>;
export type GrupaWydatkow = z.infer<typeof grupaWydatkowSchema>;
export type CzescBudzetowa = z.infer<typeof czescBudzetowaSchema>;
export type ZrodloFinansowania = z.infer<typeof zrodloFinansowaniaSchema>;
export type DocumentRow = z.infer<typeof budgetDocumentRowSchema>;
export type BudgetDocument = z.infer<typeof budgetDocumentSchema>;
export type KodZadaniowy = z.infer<typeof kodZadaniowySchema>;
