import '@testing-library/jest-dom/vitest';

const mockStorage = {
  getItem: () => null,
  setItem: () => undefined,
  removeItem: () => undefined,
  clear: () => undefined,
};

Object.defineProperty(window, 'localStorage', {
  value: mockStorage,
  configurable: true,
});
