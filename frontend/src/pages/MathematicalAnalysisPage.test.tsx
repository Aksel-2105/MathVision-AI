import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { MathematicalAnalysisPage } from "./MathematicalAnalysisPage";
import { AppProviders } from "../app/providers";
import type { MathematicalAnalysisResponse } from "../schemas/api";

const response = vi.hoisted(() => ({ id: "223e4567-e89b-12d3-a456-426614174000", image_id: "123e4567-e89b-12d3-a456-426614174000", analysis_version: "1.0.0", status: "complete", computed_at: "2026-08-04T00:00:00Z", duration_ms: 10, progress: [], source: { shape: [4, 4], dtype: "uint8", channels: 1 }, overview: { brightness: "Moderate", contrast: "Moderate", entropy: "Moderate", sharpness: "Relative derivative indicator: low", noise_estimate: "Low-to-moderate", compression_potential: "Moderate", interpretation: "Measured from pixels." }, matrix: { representation: "I ∈ R^(m×n)", rows: 4, columns: 4, scalar_value_count: 16, memory_bytes: 16, data_type: "uint8", bit_depth: 8, value_domain: [0, 255], coordinate_convention: "zero-based", origin: { row: 0, column: 0 }, values: [[1, 2], [3, 4]], limitations: "Small sample." }, statistics: {}, probability: {}, histograms: {}, gradients: {}, frequency: {}, dct: {}, wavelets: {}, svd: {}, color: {}, texture: {}, noise: {}, local_maps: {}, geometry: {}, compression: {}, report: { title: "Mathematical Image Analysis Report", main_findings: [], careful_diagnosis: "Measured.", recommended_next_operation: "Compare.", limitations: [] } })) as MathematicalAnalysisResponse;

vi.mock("../services/api", () => ({ mathematicalAnalysisExportUrl: (id: string, format: string) => `/export/${id}.${format}`, runMathematicalAnalysis: vi.fn().mockResolvedValue(response) }));

describe("MathematicalAnalysisPage", () => {
  it("loads the dedicated mathematical workspace and exposes all tabs", async () => {
    render(<AppProviders><MemoryRouter initialEntries={["/workspace/images/123e4567-e89b-12d3-a456-426614174000/mathematical-analysis"]}><Routes><Route path="workspace/images/:imageId/mathematical-analysis" element={<MathematicalAnalysisPage />} /></Routes></MemoryRouter></AppProviders>);
    expect(await screen.findByRole("heading", { name: /advanced mathematical analysis/i })).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole("button", { name: /matrix representation/i })).toBeInTheDocument());
    expect(screen.getByRole("button", { name: /mathematical report/i })).toBeInTheDocument();
  });
});
