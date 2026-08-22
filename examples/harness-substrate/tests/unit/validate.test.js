// UNIT test -- pura, sin DB, sin servidor, sin red. Corre en milisegundos.
import { describe, it, expect } from 'vitest';
import { isValidTitle } from '../../src/utils/validate.js';

describe('isValidTitle()', () => {
  it('acepta un string de 1-200 caracteres', () => {
    expect(isValidTitle('comprar pan')).toBe(true);
  });

  it('rechaza string vacio', () => {
    expect(isValidTitle('')).toBe(false);
  });

  it('rechaza mas de 200 caracteres', () => {
    expect(isValidTitle('a'.repeat(201))).toBe(false);
  });

  it('rechaza valores que no son string', () => {
    expect(isValidTitle(123)).toBe(false);
    expect(isValidTitle(null)).toBe(false);
    expect(isValidTitle(undefined)).toBe(false);
  });
});
