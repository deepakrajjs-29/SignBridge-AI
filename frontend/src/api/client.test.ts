import { beforeEach, describe, expect, test, vi } from "vitest";
import { token } from "./client";

// Vitest runs in a node environment here (no DOM), so provide a minimal
// localStorage stub so this test asserts the token value instead of
// failing with `localStorage is not defined`.
const store = new Map<string, string>();
beforeEach(() => {
  store.clear();
  vi.stubGlobal("localStorage", {
    getItem: (k: string) => (store.has(k) ? store.get(k)! : null),
    setItem: (k: string, v: string) => void store.set(k, v),
    removeItem: (k: string) => void store.delete(k),
    clear: () => store.clear(),
  });
});

describe("token default", () => {
  test("token defaults to change-me when nothing is stored", () => {
    localStorage.clear();
    expect(token()).toBe("change-me");
  });
});
