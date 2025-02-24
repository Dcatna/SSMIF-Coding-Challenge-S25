import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import * as Papa from "papaparse";



export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}


export type Result<T, E = string> =
  | { error: E; ok: false }
  | { data: T; ok: true };

export function successResult<T, E = string>(data: T): Result<T, E> {
  return { data, ok: true };
}

export function failureResult<T, E = string>(error: E): Result<T, E> {
  return { error, ok: false };
}

export async function loadCSV(filePath: string) {
  return new Promise((resolve, reject) => {
    fetch(filePath)
      .then(response => response.text())
      .then(csvText => {
        Papa.parse(csvText, {
          header: true, // Use first row as column names
          skipEmptyLines: true,
          complete: (results) => resolve(results.data),
          error: (error : unknown) => reject(error),
        });
      });
  });
}
