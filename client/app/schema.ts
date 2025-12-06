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

export const budgetDocumentRowSchema = z.object({
  dzial: z.array(dzialSchema).nullable().default(null),
  rozdzial: z.array(rozdzialSchema).nullable().default(null),
  paragraf: z.array(paragrafSchema).nullable().default(null),
  grupaWydatkow: z.array(grupaWydatkowSchema).nullable().default(null),
  czescBudzetowa: z.array(czescBudzetowaSchema).nullable().default(null),
});

export const budgetDocumentSchema = z.array(budgetDocumentRowSchema);

export type Dzial = z.infer<typeof dzialSchema>;
export type Rozdzial = z.infer<typeof rozdzialSchema>;
export type Paragraf = z.infer<typeof paragrafSchema>;
export type GrupaWydatkow = z.infer<typeof grupaWydatkowSchema>;
export type CzescBudzetowa = z.infer<typeof czescBudzetowaSchema>;
export type DocumentRow = z.infer<typeof budgetDocumentRowSchema>;
export type BudgetDocument = z.infer<typeof budgetDocumentSchema>;
