import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AppProviders } from "../app/providers";
import { getExperimentComparison, listExperiments } from "../services/api";
import { ComparisonPage } from "./ComparisonPage";

vi.mock("../services/api", () => ({ getExperimentComparison: vi.fn(), listExperiments: vi.fn() }));

const experiment = { id: "123e4567-e89b-12d3-a456-426614174000", name: "Sweep", description: null, source_image_id: "223e4567-e89b-12d3-a456-426614174000", source_image_name: "sample.png", created_at: "2026-08-04T00:00:00Z", updated_at: "2026-08-04T00:00:00Z", run_count: 2 };
const metrics = { mse: 4, rmse: 2, psnr: 42, psnr_note: null, ssim: 0.98, ssim_note: null, original_size_bytes: 100, output_size_bytes: 120, compression_ratio: 0.83, size_reduction_percent: -20, execution_time_ms: 3.2, retained_coefficient_ratio: null, representation_type: "encoded_output" as const };

describe("ComparisonPage", () => {
  beforeEach(() => { vi.mocked(listExperiments).mockReset(); vi.mocked(getExperimentComparison).mockReset(); });

  it("loads a saved experiment and displays its transparent ranking", async () => {
    vi.mocked(listExperiments).mockResolvedValue([experiment]);
    vi.mocked(getExperimentComparison).mockResolvedValue({ source_image_id: experiment.source_image_id, ranking_policy: "score policy", rows: [{ processing_id: "323e4567-e89b-12d3-a456-426614174000", algorithm: "median", parameters: {}, metrics, output_url: "/output", rank: 1, ranking_score: 0.91 }] });
    render(<AppProviders><MemoryRouter initialEntries={[`/compare?experiment=${experiment.id}`]}><ComparisonPage /></MemoryRouter></AppProviders>);
    await waitFor(() => expect(getExperimentComparison).toHaveBeenCalledWith(experiment.id));
    expect(await screen.findByText("Ranking result")).toBeInTheDocument();
    expect(screen.getByText("score policy")).toBeInTheDocument();
    expect(screen.getByText("#1")).toBeInTheDocument();
  });
});
