import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it } from "vitest";

import { AppProviders } from "../../app/providers";
import { AppShell } from "./AppShell";

function renderShell() { return render(<AppProviders><MemoryRouter><AppShell /></MemoryRouter></AppProviders>); }

describe("AppShell", () => {
  beforeEach(() => { window.localStorage.clear(); document.documentElement.className = ""; });

  it("renders accessible navigation and toggles the theme", () => {
    renderShell();
    expect(screen.getAllByRole("navigation").length).toBeGreaterThan(0);
    fireEvent.click(screen.getAllByRole("button", { name: /switch to dark theme/i })[0]);
    expect(document.documentElement).toHaveClass("dark");
    expect(window.localStorage.getItem("mathvision-theme")).toBe("dark");
  });

  it("provides a mobile navigation control", () => {
    renderShell();
    expect(screen.getByRole("button", { name: /open navigation menu/i })).toBeInTheDocument();
  });
});
