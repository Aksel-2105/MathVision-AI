import { BarChart3, LoaderCircle, Trophy } from "lucide-react";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { StatusBadge } from "../components/common/StatusBadge";
import { getExperimentComparison, listExperiments } from "../services/api";
import type { ComparisonResponse, ExperimentSummary } from "../schemas/api";

export function ComparisonPage() {
  const [params] = useSearchParams();
  const [experiments, setExperiments] = useState<ExperimentSummary[]>([]);
  const initialId = params.get("experiment") ?? "";
  const [selectedId, setSelectedId] = useState(initialId);
  const [comparison, setComparison] = useState<ComparisonResponse | null>(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { void listExperiments().then((records) => { setExperiments(records); setSelectedId((current) => current || initialId || records[0]?.id || ""); }).catch((loadError: unknown) => setError(loadError instanceof Error ? loadError.message : "Experiments could not be loaded.")); }, [initialId]);
  useEffect(() => { if (!selectedId) { setBusy(false); return; } setBusy(true); void getExperimentComparison(selectedId).then(setComparison).catch((loadError: unknown) => setError(loadError instanceof Error ? loadError.message : "Comparison could not be loaded.")).finally(() => setBusy(false)); }, [selectedId]);

  return <div className="space-y-8 pb-10"><header className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><p className="eyebrow">Phase 4 · Comparison</p><h1 className="mt-2 text-3xl font-semibold tracking-tight text-ink">Rank saved processing runs.</h1><p className="mt-3 max-w-2xl leading-7 text-ink-muted">The ranking is transparent: structural similarity, PSNR, and execution speed are combined into one reproducible score.</p></div><StatusBadge tone="violet">Measured ranking</StatusBadge></header>{error && <div className="error-panel" role="alert">{error}</div>}{experiments.length === 0 ? <div className="empty-panel"><BarChart3 className="text-cyan" size={26} /><h2 className="mt-4 text-lg font-semibold text-ink">Nothing to compare</h2><p className="mt-2 text-sm text-ink-muted">Save an experiment from the Workspace first.</p></div> : <><label className="block max-w-xl"><span className="field-label">Experiment</span><select className="field-input mt-2" value={selectedId} onChange={(event) => setSelectedId(event.target.value)}>{experiments.map((experiment) => <option value={experiment.id} key={experiment.id}>{experiment.name} · {experiment.run_count} runs</option>)}</select></label>{busy ? <div className="empty-panel"><LoaderCircle className="animate-spin text-cyan" size={24} /><p className="mt-3 text-sm text-ink-muted">Calculating ranking...</p></div> : comparison && <section className="rounded-2xl border border-line bg-surface p-5 shadow-card sm:p-7"><div className="flex items-start gap-3"><Trophy className="mt-1 text-amber-500" size={22} /><div><h2 className="text-xl font-semibold text-ink">Ranking result</h2><p className="mt-1 text-sm text-ink-muted">{comparison.ranking_policy}</p></div></div><div className="mt-6 overflow-x-auto"><table className="w-full min-w-[720px] text-left text-sm"><thead className="border-b border-line text-xs uppercase tracking-[0.1em] text-ink-muted"><tr><th className="px-4 py-3">Rank</th><th className="px-4 py-3">Algorithm</th><th className="px-4 py-3">SSIM</th><th className="px-4 py-3">PSNR</th><th className="px-4 py-3">Time</th><th className="px-4 py-3">Score</th></tr></thead><tbody>{comparison.rows.map((row) => <tr className="border-b border-line last:border-0" key={row.processing_id}><td className="px-4 py-4 font-mono font-semibold">#{row.rank}</td><td className="px-4 py-4 font-semibold">{row.algorithm}</td><td className="px-4 py-4 font-mono">{row.metrics.ssim?.toFixed(3) ?? "N/A"}</td><td className="px-4 py-4 font-mono">{row.metrics.psnr?.toFixed(2) ?? "Perfect"}</td><td className="px-4 py-4 font-mono">{row.metrics.execution_time_ms.toFixed(1)} ms</td><td className="px-4 py-4 font-mono text-cyan">{row.ranking_score.toFixed(3)}</td></tr>)}</tbody></table></div></section>}</>}</div>;
}
