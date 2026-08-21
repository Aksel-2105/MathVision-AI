import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { AppProviders } from "./providers";
import { HomePage } from "../pages/HomePage";

describe("HomePage", () => {
  it("shows the foundation scope and primary navigation actions", () => {
    render(<AppProviders><MemoryRouter><HomePage /></MemoryRouter></AppProviders>);
    expect(screen.getByText("Image intelligence grounded in mathematics.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /start image analysis/i })).toHaveAttribute("href", "/workspace");
    expect(screen.getByText(/Upload data remains temporary/i)).toBeInTheDocument();
  });
});
