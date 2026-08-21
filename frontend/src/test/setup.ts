import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

afterEach(() => cleanup());

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({ matches: query.includes("dark"), media: query, onchange: null, addListener: () => undefined, removeListener: () => undefined, addEventListener: () => undefined, removeEventListener: () => undefined, dispatchEvent: () => false }),
});

Object.defineProperty(URL, "createObjectURL", { writable: true, value: () => "blob:mathvision-test" });
Object.defineProperty(URL, "revokeObjectURL", { writable: true, value: () => undefined });
