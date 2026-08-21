import { BrainCircuit, LoaderCircle, ShieldAlert, Sparkles } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { MetricCard } from "../components/common/MetricCard";
import { StatusBadge } from "../components/common/StatusBadge";
import { getModelStatus, trainRecommendationModel } from "../services/api";
import type { ModelStatusResponse } from "../schemas/api";

const emptyStatus: ModelStatusResponse = {
  trained: false, model_version: null, trained_at: null, sample_count: 0, class_count: 0,
  classes: [], validation_accuracy: null, validation_method: null, feature_names: [], limitations: [],
};

export function ModelInsightsPage() {
  const [status, setStatus] = useState<ModelStatusResponse>(emptyStatus);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try { setStatus(await getModelStatus()); } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Model status could not be loaded."); }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  const train = async () => {
    setBusy(true); setError(null);
    try { await trainRecommendationModel(); await refresh(); } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "The model could not be trained."); } finally { setBusy(false); }
  };

  return <div className="space-y-8 pb-10">
    <header className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><p className="eyebrow">Phase 5 · Explainable recommendation</p><h1 className="mt-2 text-3xl font-semibold tracking-tight text-ink">Model Insights</h1><p className="mt-3 max-w-2xl leading-7 text-ink-muted">Train a transparent Random Forest from saved experiment outcomes, inspect its metadata, and understand the limits of each recommendation.</p></div><StatusBadge tone={status.trained ? "blue" : "muted"}>{status.trained ? "Model trained" : "Model not trained"}</StatusBadge></header>
    {error && <div className="error-panel" role="alert"><p className="font-semibold">Model request failed</p><p className="mt-1 text-sm">{error}</p></div>}
    <section className="rounded-2xl border border-violet/20 bg-violet/5 p-5 sm:p-7"><div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-start"><div className="flex gap-4"><div className="rounded-xl bg-violet/15 p-3 text-violet"><BrainCircuit size={24} /></div><div><p className="eyebrow text-violet">Recommendation model</p><h2 className="mt-2 text-2xl font-semibold text-ink">Learn from your measured experiments.</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-ink-muted">Each saved experiment contributes its source-image features and highest-scoring processing algorithm. The model never presents a recommendation without its training metadata and limitations.</p></div></div><button type="button" className="primary-button shrink-0" onClick={train} disabled={busy}>{busy ? <><LoaderCircle className="animate-spin" size={17} />Training...</> : <><Sparkles size={17} />Train model</>}</button></div></section>
    <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"><MetricCard label="Training samples" value={String(status.sample_count)} helper="Saved experiments with runs" /><MetricCard label="Algorithm classes" value={String(status.class_count)} helper={status.classes.join(", ") || "Not available"} /><MetricCard label="Validation accuracy" value={status.validation_accuracy === null ? "N/A" : `${(status.validation_accuracy * 100).toFixed(1)}%`} helper={status.validation_method ?? "Dataset too small"} /><MetricCard label="Model version" value={status.model_version ?? "Not trained"} helper={status.trained_at ? new Date(status.trained_at).toLocaleString() : "Train after saving experiments"} /></section>
    <section className="grid gap-6 lg:grid-cols-2"><div className="rounded-2xl border border-line bg-surface p-5 shadow-card sm:p-7"><p className="eyebrow">Feature space</p><h2 className="mt-2 text-xl font-semibold text-ink">Inputs used by the model</h2><div className="mt-5 flex flex-wrap gap-2">{status.feature_names.length ? status.feature_names.map((feature) => <span className="rounded-full border border-line bg-surface-muted px-3 py-1.5 font-mono text-xs text-ink-muted" key={feature}>{feature}</span>) : <p className="text-sm text-ink-muted">Train the model to register its feature space.</p>}</div></div><div className="rounded-2xl border border-amber-200 bg-amber-50 p-5 sm:p-7 dark:border-amber-900 dark:bg-amber-950/20"><div className="flex items-center gap-2 text-amber-700 dark:text-amber-300"><ShieldAlert size={18} /><p className="eyebrow text-amber-700 dark:text-amber-300">Truthful limitations</p></div><ul className="mt-4 space-y-3 text-sm leading-6 text-amber-900 dark:text-amber-200">{(status.limitations.length ? status.limitations : ["No model has been trained yet."]).map((limitation) => <li className="flex gap-2" key={limitation}><span aria-hidden="true">•</span><span>{limitation}</span></li>)}</ul></div></section>
  </div>;
}
