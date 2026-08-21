import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { AppProviders } from "../app/providers";
import { MathematicsPage } from "./MathematicsPage";

describe("MathematicsPage", () => {
  it("presents implemented transforms, metrics, equations, and limitations", () => {
    render(<AppProviders><MemoryRouter><MathematicsPage /></MemoryRouter></AppProviders>);
    expect(screen.getByRole("heading", { name: /from pixels to measurable evidence/i })).toBeInTheDocument();
    expect(screen.getByText(/Discrete Wavelet Transform/i)).toBeInTheDocument();
    expect(screen.getByText(/Peak Signal-to-Noise Ratio/i)).toBeInTheDocument();
    expect(screen.getByText(/no single metric is a complete definition/i)).toBeInTheDocument();
  });
});
