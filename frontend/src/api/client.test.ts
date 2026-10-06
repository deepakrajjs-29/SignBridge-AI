import { describe, expect, test } from "vitest";
import { token } from "./client";

describe("token default", () => {
  test("token defaults to change-me when nothing is stored", () => {
    localStorage.clear();
    expect(token()).toBe("change-me");
  });
});
