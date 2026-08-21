import { Clock3, Download, FlaskConical, LoaderCircle, Trash2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { StatusBadge } from "../components/common/StatusBadge";
import { deleteExperiment, experimentExportUrl, getExperiment, listExperiments } from "../services/api";
import type { ExperimentDetail, ExperimentSummary } from "../schemas/api";

export function ExperimentsPage() {
  const { experimentId } = useParams();
  const [experiments, setExperiments] = useState<ExperimentSummary[]>([]);
  const [detail, setDetail] = useState<ExperimentDetail | null>(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setBusy(true); setError(null);
    try {
      const records = await listExperiments();
      setExperiments(records);
      if (experimentId) setDetail(await getExperiment(experimentId));
    } catch (loadError) { setError(loadError instanceof Error ? loadError.message : "Experiment history could not be loaded."); } finally { setBusy(false); }
  }, [experimentId]);

  useEffect(() => { void load(); }, [load]);

  const remove = async (id: string) => {
    if (!window.confirm("Delete this experiment history?")) return;
    try { await deleteExperiment(id); setExperiments((current) => current.filter((item) => item.id !== id)); if (detail?.id === id) setDetail(null); } catch (deleteError) { setError(deleteError instanceof Error ? deleteError.message : "The experiment could not be deleted."); }
  };

  if (busy) return <div className="empty-panel"><LoaderCircle className="animate-spin text-cyan" size={24} /><p className="mt-3 text-sm text-ink-muted">Loading experiment history...</p></div>;
  return <div className="space-y-8 pb-10"><header className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><p className="eyebrow">Phase 4 · History</p><h1 className="mt-2 text-3xl font-semibold tracking-tight text-ink">Experiments and saved runs.</h1><p className="mt-3 max-w-2xl leading-7 text-ink-muted">Persistent experiment metadata and metric snapshots remain available after the temporary processing output expires.</p></div><StatusBadge tone="violet">{experiments.length} saved</StatusBadge></header>{error && <div className="error-panel" role="alert">{error}</div>}{experiments.length === 0 ? <div className="empty-panel"><FlaskConical className="text-cyan" size={26} /><h2 className="mt-4 text-lg font-semibold text-ink">No experiments yet</h2><p className="mt-2 text-sm leading-6 text-ink-muted">Process an image in the Workspace, then save its runs as an experiment.</p><Link className="primary-button mx-auto mt-5 w-fit" to="/workspace">Open workspace</Link></div> : <div className="grid gap-4">{experiments.map((experiment) => <article className="rounded-2xl border border-line bg-surface p-5 shadow-card sm:p-7" key={experiment.id}><div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start"><div><div className="flex items-center gap-3"><FlaskConical className="text-cyan" size={20} /><h2 className="text-xl font-semibold text-ink">{experiment.name}</h2></div><p className="mt-2 text-sm text-ink-muted">{experiment.description || "No description"} · {experiment.source_image_name}</p><p className="mt-3 flex items-center gap-2 text-xs text-ink-muted"><Clock3 size={14} />Updated {new Date(experiment.updated_at).toLocaleString()} · {experiment.run_count} run{experiment.run_count === 1 ? "" : "s"}</p></div><div className="flex flex-wrap gap-2"><Link className="secondary-button" to={`/compare?experiment=${experiment.id}`}>Compare</Link><a className="secondary-button" href={experimentExportUrl(experiment.id, "csv")}><Download size={16} />CSV</a><button className="icon-button" type="button" aria-label={`Delete ${experiment.name}`} onClick={() => void remove(experiment.id)}><Trash2 size={17} /></button></div></div></article>)}</div>}{detail && <section className="rounded-2xl border border-cyan/20 bg-cyan/5 p-5 sm:p-7"><p className="eyebrow text-cyan">Selected experiment</p><h2 className="mt-2 text-2xl font-semibold text-ink">{detail.name}</h2><div className="mt-5 overflow-x-auto rounded-xl border border-line bg-surface"><table className="w-full min-w-[680px] text-left text-sm"><thead className="border-b border-line bg-surface-muted/70 text-xs uppercase tracking-[0.1em] text-ink-muted"><tr><th className="px-4 py-3">Algorithm</th><th className="px-4 py-3">MSE</th><th className="px-4 py-3">SSIM</th><th className="px-4 py-3">PSNR</th><th className="px-4 py-3">Saved at</th></tr></thead><tbody>{detail.runs.map((run) => <tr className="border-b border-line last:border-0" key={run.id}><td className="px-4 py-3 font-semibold">{run.algorithm}</td><td className="px-4 py-3 font-mono">{run.metrics.mse.toFixed(2)}</td><td className="px-4 py-3 font-mono">{run.metrics.ssim?.toFixed(3) ?? "N/A"}</td><td className="px-4 py-3 font-mono">{run.metrics.psnr?.toFixed(2) ?? "Perfect"}</td><td className="px-4 py-3 text-ink-muted">{new Date(run.created_at).toLocaleString()}</td></tr>)}</tbody></table></div></section>}</div>;
}
