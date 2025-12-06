export interface Dzial {
  kod: string;
  nazwa: string;
  PKD: string;
}

export interface Rozdzial {
  kod: string;
  nazwa: string;
  dzial: string;
}

export interface Paragraf {
  kod: string;
  tresc: string;
}

export interface GrupaWydatkow {
  id: number;
  nazwa: string;
  paragrafy: string[] | string; // single string is for grupa wydatkow that has dynamic 4th digit
}

export interface CzescBudzetowa {
  kod: string;
  nazwa: string;
}

// Budget-related interfaces
export interface IBudgetItem {
  id: string;
  kod: string;
  nazwa: string;
  planowane: number;
  wykonane: number;
  procent_wykonania: number;
  kategoria: string;
  zrodlo_finansowania: string;
}

export interface IDzial {
  kod: string;
  nazwa: string;
  PKD?: string;
}

export interface IRozdzial {
  kod: string;
  nazwa: string;
  dzial_kod: string;
}

export interface IParagraf {
  kod: string;
  nazwa: string;
  rozdzial_kod: string;
}

export interface IGrupaWydatkow {
  kod: string;
  nazwa: string;
}

export interface IZrodloFinansowania {
  kod: string;
  nazwa: string;
}

export interface ICzescBudzetowa {
  kod: string;
  nazwa: string;
}
