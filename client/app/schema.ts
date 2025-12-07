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

export const planowanieBudzetuCreateSchema = z.object({
  nazwa_projektu: z.string().optional(),
  nazwa_zadania: z.string().optional(),
  szczegolowe_uzasadnienie_realizacji: z.string().optional(),
  budzet: z.string().optional(),
  czesc_budzetowa_kod: z.string().min(1, "Część budżetowa jest wymagana"),
  dzial_kod: z.string().min(1, "Dział jest wymagany"),
  rozdzial_kod: z.string().min(1, "Rozdział jest wymagany"),
  paragraf_kod: z.string().min(1, "Paragraf jest wymagany"),
  zrodlo_finansowania_kod: z.string().min(1, "Źródło finansowania jest wymagane"),
  grupa_wydatkow_id: z.number().min(1, "Grupa wydatków jest wymagana"),
  komorka_organizacyjna_id: z.number().min(1, "Komórka organizacyjna jest wymagana"),
});

export type PlanowanieBudzetuCreate = z.infer<typeof planowanieBudzetuCreateSchema>;

export const planowanieBudzetuResponseSchema = z.object({
  id: z.number(),
  nazwa_projektu: z.string().nullable(),
  nazwa_zadania: z.string().nullable(),
  szczegolowe_uzasadnienie_realizacji: z.string().nullable(),
  budzet: z.string().nullable(),
  czesc_budzetowa_kod: z.string().nullable(),
  dzial_kod: z.string().nullable(),
  rozdzial_kod: z.string().nullable(),
  paragraf_kod: z.string().nullable(),
  zrodlo_finansowania_kod: z.string().nullable(),
  grupa_wydatkow_id: z.number().nullable(),
  komorka_organizacyjna_id: z.number().nullable(),
});

export type PlanowanieBudzetuResponse = z.infer<typeof planowanieBudzetuResponseSchema>;
