import type { ReactNode } from "react";

type MetricCardProps = { label: string; value: string; helper?: string; icon?: ReactNode };

export function MetricCard({ label, value, helper, icon }: MetricCardProps) { return <article className="metric-card"><div className="flex items-start justify-between gap-3"><p className="text-xs font-semibold uppercase tracking-[0.12em] text-ink-muted">{label}</p>{icon && <span className="text-cyan">{icon}</span>}</div><p className="mt-3 font-mono text-2xl font-semibold tracking-tight text-ink">{value}</p>{helper && <p className="mt-2 text-xs text-ink-muted">{helper}</p>}</article>; }
