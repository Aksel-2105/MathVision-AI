import { algorithmListSchema, analysisSchema, apiErrorSchema, comparisonSchema, experimentDetailSchema, experimentListSchema, experimentSummarySchema, imageUploadSchema, mathematicalAnalysisSchema, modelStatusSchema, processingSchema, recommendationSchema, trainingSchema, type AlgorithmInfo, type AlgorithmName, type AnalysisResponse, type ComparisonResponse, type ExperimentDetail, type ExperimentSummary, type ImageUploadResponse, type MathematicalAnalysisResponse, type ModelStatusResponse, type ParameterValue, type ProcessingResponse, type RecommendationResponse, type TrainingResponse } from "../schemas/api";

// An empty base URL makes production requests same-origin. Local Vite development
// proxies /api to the FastAPI process; Docker Compose can still override this with
// VITE_API_BASE_URL=http://localhost:8000.
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

export class ApiClientError extends Error {
  readonly code: string;

  constructor(message: string, code = "api_error") {
    super(message);
    this.name = "ApiClientError";
    this.code = code;
  }
}

async function readJson(response: Response): Promise<unknown> {
  try { return await response.json(); } catch { return null; }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, init);
  } catch {
    throw new ApiClientError("Network connection failed. Check that the API is running.", "network_error");
  }
  const payload = await readJson(response);
  if (!response.ok) {
    const parsed = apiErrorSchema.safeParse(payload);
    throw new ApiClientError(parsed.success ? parsed.data.error.message : "The API request failed.", parsed.success ? parsed.data.error.code : "api_error");
  }
  return payload as T;
}

export async function uploadImage(file: File): Promise<ImageUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  return imageUploadSchema.parse(await request<unknown>("/api/v1/images/upload", { method: "POST", body: formData }));
}

export async function analyzeImage(imageId: string): Promise<AnalysisResponse> {
  return analysisSchema.parse(await request<unknown>(`/api/v1/analysis/${imageId}`, { method: "POST" }));
}

export async function getAlgorithms(): Promise<AlgorithmInfo[]> {
  const response = algorithmListSchema.parse(await request<unknown>("/api/v1/processing/algorithms"));
  return response.algorithms;
}

export async function processImage(imageId: string, algorithm: AlgorithmName, parameters: Record<string, ParameterValue>): Promise<ProcessingResponse> {
  return processingSchema.parse(await request<unknown>("/api/v1/processing", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ image_id: imageId, algorithm, parameters }) }));
}

export async function compareProcessing(processingIds: string[]): Promise<ComparisonResponse> {
  return comparisonSchema.parse(await request<unknown>("/api/v1/comparisons", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ processing_ids: processingIds }) }));
}

export async function createExperiment(imageId: string, name: string, description?: string): Promise<ExperimentSummary> {
  return experimentSummarySchema.parse(await request<unknown>("/api/v1/experiments", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ image_id: imageId, name, description: description || null }) }));
}

export async function addExperimentRun(experimentId: string, processingId: string): Promise<void> {
  await request<unknown>(`/api/v1/experiments/${experimentId}/runs`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ processing_id: processingId }) });
}

export async function listExperiments(imageId?: string): Promise<ExperimentSummary[]> {
  const query = imageId ? `?image_id=${encodeURIComponent(imageId)}` : "";
  return experimentListSchema.parse(await request<unknown>(`/api/v1/experiments${query}`)).experiments;
}

export async function getExperiment(experimentId: string): Promise<ExperimentDetail> {
  return experimentDetailSchema.parse(await request<unknown>(`/api/v1/experiments/${experimentId}`));
}

export async function getExperimentComparison(experimentId: string): Promise<ComparisonResponse> {
  return comparisonSchema.parse(await request<unknown>(`/api/v1/experiments/${experimentId}/comparison`));
}

export async function deleteExperiment(experimentId: string): Promise<void> {
  await request<unknown>(`/api/v1/experiments/${experimentId}`, { method: "DELETE" });
}

export function experimentExportUrl(experimentId: string, format: "json" | "csv"): string { return `${API_BASE_URL}/api/v1/experiments/${experimentId}/export?format=${format}`; }

export function absoluteContentUrl(contentUrl: string): string {
  return new URL(contentUrl, API_BASE_URL || window.location.origin).toString();
}

export async function getModelStatus(): Promise<ModelStatusResponse> {
  return modelStatusSchema.parse(await request<unknown>("/api/v1/recommendations/model"));
}

export async function trainRecommendationModel(): Promise<TrainingResponse> {
  return trainingSchema.parse(await request<unknown>("/api/v1/recommendations/train", { method: "POST" }));
}

export async function recommendImage(imageId: string): Promise<RecommendationResponse> {
  return recommendationSchema.parse(await request<unknown>("/api/v1/recommendations", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ image_id: imageId }) }));
}

export async function runMathematicalAnalysis(imageId: string, gridSize: 4 | 8 | 16 = 4): Promise<MathematicalAnalysisResponse> {
  return mathematicalAnalysisSchema.parse(await request<unknown>(`/api/v1/mathematical-analysis/${imageId}?grid_size=${gridSize}`, { method: "POST" }));
}

export function mathematicalAnalysisExportUrl(analysisId: string, format: "json" | "csv"): string {
  return `${API_BASE_URL}/api/v1/mathematical-analysis/${analysisId}/export?format=${format}`;
}
