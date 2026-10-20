// @vitest-environment jsdom
import { afterEach, expect, test, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import Settings from "./Settings";

afterEach(() => {
  cleanup();
  localStorage.removeItem("sb_threshold");
});

test("policy-honesty note states the server accept threshold and slider semantics", () => {
  render(<Settings currentTheme="dark" onThemeChange={vi.fn()} />);
  expect(
    screen.getByText(
      "Server accept threshold: 0.57 (model policy). Predictions below this appear as Provisional and are never auto-added; your slider can only add a stricter personal gate on top."
    )
  ).toBeTruthy();
});
