import { z } from "zod";

export const imageUploadSchema = z.object({
  id: z.string().uuid(),
  original_name: z.string(),
  content_hash: z.string().length(64),
  mime_type: z.string(),
  format: z.string(),
  width: z.number().int().positive(),
  height: z.number().int().positive(),
  channels: z.number().int().positive(),
  color_mode: z.string(),
  size_bytes: z.number().int().positive(),
  created_at: z.string(),
  expires_at: z.string(),
  content_url: z.string(),
});

const histogramSeriesSchema = z.object({ label: z.string(), values: z.array(z.number().int().nonnegative()) });

export const analysisSchema = z.object({
  id: z.string().uuid(),
  image_id: z.string().uuid(),
  analysis_version: z.string(),
  features: z.object({
    width: z.number().int().positive(), height: z.number().int().positive(), channels: z.number().int().positive(), color_mode: z.string(), file_size_bytes: z.number().int().positive(), aspect_ratio: z.number().positive(), min_intensity: z.number(), max_intensity: z.number(), mean_intensity: z.number(), median_intensity: z.number(), variance: z.number().nonnegative(), standard_deviation: z.number().nonnegative(), dynamic_range: z.number().nonnegative(), rms_contrast: z.number().nonnegative(), entropy: z.number().nonnegative(), edge_density: z.number().min(0).max(1), laplacian_variance: z.number().nonnegative(), sharpness_estimate: z.number().nonnegative(), brightness: z.number().min(0).max(1), saturation: z.number().min(0).max(1), gradient_mean: z.number().nonnegative(), gradient_standard_deviation: z.number().nonnegative(), high_frequency_energy: z.number().nonnegative(),
  }),
  histogram: z.object({ bins: z.array(z.number().int()), series: z.array(histogramSeriesSchema), unit: z.string() }),
  noise_estimate: z.object({ type: z.string(), level: z.number().min(0).max(1), method: z.string(), limitations: z.string() }),
});

export const apiErrorSchema = z.object({ error: z.object({ code: z.string(), message: z.string(), details: z.unknown().optional() }) });

export const algorithmInfoSchema = z.object({
  name: z.string(), label: z.string(), category: z.enum(["denoising", "enhancement", "compression"]), description: z.string(), defaults: z.record(z.union([z.string(), z.number(), z.boolean()])),
});

export const algorithmListSchema = z.object({ algorithms: z.array(algorithmInfoSchema) });

export const processingSchema = z.object({
  id: z.string().uuid(), image_id: z.string().uuid(), algorithm: z.string(), parameters: z.record(z.union([z.string(), z.number(), z.boolean()])), output_url: z.string(), output_format: z.string(), output_size_bytes: z.number().int().positive(), created_at: z.string(),
  metrics: z.object({ mse: z.number().nonnegative(), rmse: z.number().nonnegative(), psnr: z.number().nonnegative().nullable(), psnr_note: z.string().nullable(), ssim: z.number().min(-1).max(1).nullable(), ssim_note: z.string().nullable(), original_size_bytes: z.number().int().positive(), output_size_bytes: z.number().int().positive(), compression_ratio: z.number().positive(), size_reduction_percent: z.number(), execution_time_ms: z.number().nonnegative(), retained_coefficient_ratio: z.number().min(0).max(1).nullable(), representation_type: z.enum(["encoded_output", "mathematical_simulation"]), }),
});

export const experimentSummarySchema = z.object({ id: z.string().uuid(), name: z.string(), description: z.string().nullable(), source_image_id: z.string().uuid(), source_image_name: z.string(), created_at: z.string(), updated_at: z.string(), run_count: z.number().int().nonnegative() });
export const experimentRunSchema = z.object({ id: z.string().uuid(), processing_id: z.string().uuid(), algorithm: z.string(), parameters: z.record(z.union([z.string(), z.number(), z.boolean()])), metrics: processingSchema.shape.metrics, output_url: z.string(), created_at: z.string() });
export const experimentDetailSchema = experimentSummarySchema.extend({ runs: z.array(experimentRunSchema) });
export const experimentListSchema = z.object({ experiments: z.array(experimentSummarySchema) });
export const comparisonSchema = z.object({ source_image_id: z.string().uuid(), rows: z.array(z.object({ processing_id: z.string().uuid(), algorithm: z.string(), parameters: z.record(z.union([z.string(), z.number(), z.boolean()])), metrics: processingSchema.shape.metrics, output_url: z.string(), rank: z.number().int().positive(), ranking_score: z.number().min(0).max(1) })), ranking_policy: z.string() });
const recommendationFields = { model_version: z.string(), trained_at: z.string(), sample_count: z.number().int().nonnegative(), class_count: z.number().int().nonnegative(), classes: z.array(z.string()), validation_accuracy: z.number().min(0).max(1).nullable(), validation_method: z.string(), feature_names: z.array(z.string()), limitations: z.array(z.string()) };
export const trainingSchema = z.object(recommendationFields).extend({ sample_count: z.number().int().positive(), class_count: z.number().int().positive() });
export const modelStatusSchema = z.object({ trained: z.boolean(), model_version: z.string().nullable(), trained_at: z.string().nullable(), sample_count: z.number().int().nonnegative(), class_count: z.number().int().nonnegative(), classes: z.array(z.string()), validation_accuracy: z.number().min(0).max(1).nullable(), validation_method: z.string().nullable(), feature_names: z.array(z.string()), limitations: z.array(z.string()) });
export const recommendationSchema = z.object({ id: z.string().uuid(), image_id: z.string().uuid(), model_version: z.string(), recommended_algorithm: z.string(), confidence: z.number().min(0).max(1), probabilities: z.record(z.number().min(0).max(1)), features: z.record(z.number()), feature_importance: z.record(z.number().nonnegative()), explanation: z.string(), limitations: z.array(z.string()), generated_at: z.string() });
const mathematicalSectionSchema = z.record(z.unknown());
export const mathematicalAnalysisSchema = z.object({
  id: z.string().uuid(), image_id: z.string().uuid(), analysis_version: z.string(), status: z.string(), computed_at: z.string(), duration_ms: z.number().nonnegative(), progress: z.array(z.record(z.unknown())), source: mathematicalSectionSchema,
  overview: mathematicalSectionSchema, matrix: mathematicalSectionSchema, statistics: mathematicalSectionSchema, probability: mathematicalSectionSchema, histograms: mathematicalSectionSchema, gradients: mathematicalSectionSchema, frequency: mathematicalSectionSchema, dct: mathematicalSectionSchema, wavelets: mathematicalSectionSchema, svd: mathematicalSectionSchema, color: mathematicalSectionSchema, texture: mathematicalSectionSchema, noise: mathematicalSectionSchema, local_maps: mathematicalSectionSchema, geometry: mathematicalSectionSchema, compression: mathematicalSectionSchema, report: mathematicalSectionSchema,
});

export type ImageUploadResponse = z.infer<typeof imageUploadSchema>;
export type AnalysisResponse = z.infer<typeof analysisSchema>;
export type HistogramData = AnalysisResponse["histogram"];
export type AlgorithmInfo = z.infer<typeof algorithmInfoSchema>;
export type AlgorithmName = AlgorithmInfo["name"];
export type ParameterValue = string | number | boolean;
export type ProcessingResponse = z.infer<typeof processingSchema>;
export type ExperimentSummary = z.infer<typeof experimentSummarySchema>;
export type ExperimentDetail = z.infer<typeof experimentDetailSchema>;
export type ComparisonResponse = z.infer<typeof comparisonSchema>;
export type TrainingResponse = z.infer<typeof trainingSchema>;
export type ModelStatusResponse = z.infer<typeof modelStatusSchema>;
export type RecommendationResponse = z.infer<typeof recommendationSchema>;
export type MathematicalSection = z.infer<typeof mathematicalSectionSchema>;
export type MathematicalAnalysisResponse = z.infer<typeof mathematicalAnalysisSchema>;
