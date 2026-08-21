import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AppProviders } from "../app/providers";
import { getModelStatus, trainRecommendationModel } from "../services/api";
import { ModelInsightsPage } from "./ModelInsightsPage";

vi.mock("../services/api", () => ({ getModelStatus: vi.fn(), trainRecommendationModel: vi.fn() }));

const untrained = { trained: false, model_version: null, trained_at: null, sample_count: 0, class_count: 0, classes: [], validation_accuracy: null, validation_method: null, feature_names: [], limitations: [] };
const trained = { trained: true, model_version: "random-forest-v1", trained_at: "2026-08-04T00:00:00Z", sample_count: 8, class_count: 2, classes: ["median", "gaussian"], validation_accuracy: 0.75, validation_method: "stratified_holdout_25_percent", feature_names: ["entropy", "edge_density"], limitations: ["Small dataset."] };

describe("ModelInsightsPage", () => {
  beforeEach(() => { vi.mocked(getModelStatus).mockReset(); vi.mocked(trainRecommendationModel).mockReset(); });

  it("trains and displays truthful model metadata", async () => {
    vi.mocked(getModelStatus).mockResolvedValueOnce(untrained).mockResolvedValueOnce(trained);
    vi.mocked(trainRecommendationModel).mockResolvedValue({ model_version: trained.model_version, trained_at: trained.trained_at, sample_count: trained.sample_count, class_count: trained.class_count, classes: trained.classes, validation_accuracy: trained.validation_accuracy, validation_method: trained.validation_method, feature_names: trained.feature_names, limitations: trained.limitations });
    render(<AppProviders><MemoryRouter><ModelInsightsPage /></MemoryRouter></AppProviders>);
    await waitFor(() => expect(screen.getByText(/model not trained/i)).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: /train model/i }));
    await waitFor(() => expect(trainRecommendationModel).toHaveBeenCalled());
    expect(await screen.findByText(/model trained/i)).toBeInTheDocument();
    expect(screen.getByText("75.0%", { exact: false })).toBeInTheDocument();
    expect(screen.getByText("Small dataset.")).toBeInTheDocument();
  });
});
