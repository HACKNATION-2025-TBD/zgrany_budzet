export interface Post {
  userId: number;
  id: number;
  title: string;
  body: string;
}

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
