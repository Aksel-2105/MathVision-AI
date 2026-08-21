import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AppProviders } from "../app/providers";
import { WorkspacePage } from "./WorkspacePage";
import { analyzeImage, processImage, uploadImage } from "../services/api";

vi.mock("../services/api", () => ({ absoluteContentUrl: (url: string) => url, analyzeImage: vi.fn(), processImage: vi.fn(), uploadImage: vi.fn() }));

const uploadedImage = {
  id: "123e4567-e89b-12d3-a456-426614174000", original_name: "sample.png", content_hash: "a".repeat(64), mime_type: "image/png", format: "PNG", width: 16, height: 12, channels: 3, color_mode: "RGB", size_bytes: 100, created_at: "2026-08-04T00:00:00Z", expires_at: "2026-08-05T00:00:00Z", content_url: "/api/v1/images/123/content",
};
const analysis = {
  id: "223e4567-e89b-12d3-a456-426614174000", image_id: uploadedImage.id, analysis_version: "2.0.0", features: { width: 16, height: 12, channels: 3, color_mode: "RGB", file_size_bytes: 100, aspect_ratio: 16 / 12, min_intensity: 20, max_intensity: 220, mean_intensity: 100, median_intensity: 100, variance: 20, standard_deviation: 4, dynamic_range: 200, rms_contrast: 4, entropy: 5.2, edge_density: 0.1, laplacian_variance: 22, sharpness_estimate: 22, brightness: 0.4, saturation: 0.2, gradient_mean: 2, gradient_standard_deviation: 1, high_frequency_energy: 0.1 }, histogram: { bins: [0, 1], series: [{ label: "Red", values: [10, 2] }], unit: "pixel_count" }, noise_estimate: { type: "none_detected", level: 0.01, method: "heuristic", limitations: "No clean reference." },
};
const processing = {
  id: "323e4567-e89b-12d3-a456-426614174000", image_id: uploadedImage.id, algorithm: "median", parameters: { kernel_size: 3 }, output_url: "/api/v1/processing/323e4567-e89b-12d3-a456-426614174000/content", output_format: "PNG", output_size_bytes: 120, created_at: "2026-08-04T00:00:00Z", metrics: { mse: 4, rmse: 2, psnr: 42, psnr_note: null, ssim: 0.98, ssim_note: null, original_size_bytes: 100, output_size_bytes: 120, compression_ratio: 0.83, size_reduction_percent: -20, execution_time_ms: 3.2, retained_coefficient_ratio: null, representation_type: "encoded_output" as const },
};

describe("WorkspacePage", () => {
  beforeEach(() => { vi.mocked(uploadImage).mockReset(); vi.mocked(analyzeImage).mockReset(); vi.mocked(processImage).mockReset(); });

  it("shows client validation errors before making an API request", () => {
    render(<AppProviders><MemoryRouter><WorkspacePage /></MemoryRouter></AppProviders>);
    fireEvent.change(screen.getByLabelText(/choose image file/i), { target: { files: [new File(["text"], "notes.txt", { type: "text/plain" })] } });
    expect(screen.getByRole("alert")).toHaveTextContent(/unsupported file type/i);
    expect(uploadImage).not.toHaveBeenCalled();
  });

  it("uploads a validated file and requests analysis", async () => {
    vi.mocked(uploadImage).mockResolvedValue(uploadedImage);
    vi.mocked(analyzeImage).mockResolvedValue(analysis);
    render(<AppProviders><MemoryRouter><WorkspacePage /></MemoryRouter></AppProviders>);
    const file = new File(["image"], "sample.png", { type: "image/png" });
    fireEvent.change(screen.getByLabelText(/choose image file/i), { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: /upload image/i }));
    await waitFor(() => expect(uploadImage).toHaveBeenCalledWith(file));
    fireEvent.click(screen.getByRole("button", { name: /quick analysis/i }));
    await waitFor(() => expect(analyzeImage).toHaveBeenCalledWith(uploadedImage.id));
    expect(await screen.findByText(/statistical analysis/i)).toBeInTheDocument();
  });

  it("processes the uploaded image and displays measured output", async () => {
    vi.mocked(uploadImage).mockResolvedValue(uploadedImage);
    vi.mocked(processImage).mockResolvedValue(processing);
    render(<AppProviders><MemoryRouter><WorkspacePage /></MemoryRouter></AppProviders>);
    const file = new File(["image"], "sample.png", { type: "image/png" });
    fireEvent.change(screen.getByLabelText(/choose image file/i), { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: /upload image/i }));
    await waitFor(() => expect(uploadImage).toHaveBeenCalled());
    fireEvent.click(screen.getByRole("button", { name: /^Process image$/ }));
    await waitFor(() => expect(processImage).toHaveBeenCalledWith(uploadedImage.id, "median", { kernel_size: 3 }));
    expect(await screen.findByText(/measured result/i)).toBeInTheDocument();
    expect(screen.getByText("42.00 dB")).toBeInTheDocument();
  });
});
