/* eslint-disable react-refresh/only-export-components */
import { BlockMath } from "react-katex";
import type { ReactNode } from "react";

import type { MathematicalSection } from "../../schemas/api";

export function value(section: MathematicalSection, key: string): unknown { return section[key]; }
export function numberValue(section: MathematicalSection, key: string): number | null { const item = section[key]; return typeof item === "number" && Number.isFinite(item) ? item : null; }
export function stringValue(section: MathematicalSection, key: string): string | null { const item = section[key]; return typeof item === "string" ? item : null; }
export function numberArray(item: unknown): number[] { return Array.isArray(item) ? item.filter((entry): entry is number => typeof entry === "number" && Number.isFinite(entry)) : []; }
export function numberMatrix(item: unknown): number[][] { return Array.isArray(item) ? item.map((row) => numberArray(row)) : []; }

export function FormulaExplanation({ formula, symbols, method, interpretation, limitations }: { formula?: unknown; symbols?: unknown; method?: unknown; interpretation?: unknown; limitations?: unknown }) {
  const symbolText = symbols && typeof symbols === "object" ? Object.entries(symbols).map(([key, item]) => `${key}: ${String(item)}`).join(" · ") : undefined;
  const formulaText = formula === undefined || formula === null ? null : String(formula);
  const methodText = method === undefined || method === null ? null : String(method);
  const interpretationText = interpretation === undefined || interpretation === null ? null : String(interpretation);
  const limitationsText = limitations === undefined || limitations === null ? null : String(limitations);
  return <div className="mt-4 rounded-xl border border-cyan/20 bg-cyan/5 p-4"><p className="eyebrow text-cyan">Mathematical context</p>{formulaText && <div className="mt-3 overflow-x-auto text-ink"><BlockMath math={formulaText} /></div>}{symbolText && <p className="mt-2 text-xs leading-5 text-ink-muted"><span className="font-semibold text-ink">Symbols:</span> {symbolText}</p>}{methodText && <p className="mt-2 text-xs leading-5 text-ink-muted"><span className="font-semibold text-ink">Method:</span> {methodText}</p>}{interpretationText && <p className="mt-2 text-sm leading-6 text-ink"><span className="font-semibold">Interpretation:</span> {interpretationText}</p>}{limitationsText && <p className="mt-2 text-xs leading-5 text-ink-muted"><span className="font-semibold text-amber-700 dark:text-amber-300">Limitations:</span> {limitationsText}</p>}</div>;
}

export function SectionCard({ title, eyebrow, children, className = "" }: { title: string; eyebrow?: string; children: ReactNode; className?: string }) {
  return <section className={`rounded-2xl border border-line bg-surface p-5 shadow-card sm:p-7 ${className}`}><div><p className="eyebrow text-cyan">{eyebrow ?? "Mathematical analysis"}</p><h2 className="mt-2 text-xl font-semibold tracking-tight text-ink">{title}</h2></div><div className="mt-5">{children}</div></section>;
}

export function Metric({ label, item, unit = "", interpretation }: { label: string; item: unknown; unit?: string; interpretation?: string }) {
  const shown = typeof item === "number" ? item.toLocaleString(undefined, { maximumFractionDigits: 4 }) : String(item ?? "Not available");
  return <div className="rounded-xl border border-line bg-surface-muted/50 p-4"><p className="text-xs font-semibold uppercase tracking-[0.1em] text-ink-muted">{label}</p><p className="mt-2 font-mono text-xl font-semibold text-ink">{shown}{item !== null && item !== undefined && unit ? <span className="ml-1 text-xs font-normal text-ink-muted">{unit}</span> : null}</p>{interpretation && <p className="mt-2 text-xs leading-5 text-ink-muted">{interpretation}</p>}</div>;
}

export function MetricGrid({ items }: { items: Array<{ label: string; value: unknown; unit?: string; interpretation?: string }> }) { return <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{items.map((item) => <Metric key={item.label} label={item.label} item={item.value} unit={item.unit} interpretation={item.interpretation} />)}</div>; }

export function LineChart({ values, label, color = "#0891B2" }: { values: number[]; label: string; color?: string }) {
  const width = 720; const height = 220; const max = Math.max(...values, 1); const path = values.map((item, index) => `${index === 0 ? "M" : "L"}${(index / Math.max(1, values.length - 1) * width).toFixed(2)} ${(height - item / max * (height - 20)).toFixed(2)}`).join(" ");
  return <figure className="rounded-xl border border-line bg-surface-muted/40 p-3"><p className="mb-2 text-xs font-semibold text-ink-muted">{label}</p><div className="overflow-x-auto"><svg className="min-w-[560px]" viewBox={`0 0 ${width} ${height}`} role="img" aria-label={label}><path d={path} fill="none" stroke={color} strokeWidth="2" vectorEffect="non-scaling-stroke" /></svg></div></figure>;
}

export function Heatmap({ values, label }: { values: number[][]; label: string }) {
  const rows = values.length; const cols = Math.max(...values.map((row) => row.length), 1); const flat = values.flat(); const min = Math.min(...flat, 0); const max = Math.max(...flat, 1); const width = Math.max(240, cols * 28); const height = Math.max(180, rows * 28);
  return <figure className="rounded-xl border border-line bg-surface-muted/40 p-3"><p className="mb-2 text-xs font-semibold text-ink-muted">{label}</p><div className="overflow-auto"><svg width={width} height={height} role="img" aria-label={label}>{values.map((row, y) => row.map((item, x) => { const ratio = (item - min) / Math.max(1e-12, max - min); return <rect key={`${y}-${x}`} x={x * (width / cols)} y={y * (height / Math.max(1, rows))} width={width / cols + 1} height={height / Math.max(1, rows) + 1} fill={`rgb(${Math.round(8 + 20 * ratio)} ${Math.round(145 + 80 * ratio)} ${Math.round(178 + 60 * ratio)})`}><title>{`row ${y}, column ${x}: ${item.toFixed(4)}`}</title></rect>; }))}</svg></div></figure>;
}

export function KeyValueTable({ values }: { values: unknown }) {
  if (!values || typeof values !== "object" || Array.isArray(values)) return <p className="text-sm text-ink-muted">No tabular values available.</p>;
  return <div className="overflow-x-auto rounded-xl border border-line"><table className="w-full text-left text-sm"><tbody>{Object.entries(values).map(([key, item]) => <tr className="border-b border-line last:border-0" key={key}><th className="whitespace-nowrap px-3 py-2 font-medium text-ink-muted">{key.replaceAll("_", " ")}</th><td className="px-3 py-2 font-mono text-ink">{typeof item === "object" ? JSON.stringify(item) : String(item)}</td></tr>)}</tbody></table></div>;
}

export function MatrixPreview({ values, label }: { values: number[][]; label: string }) { return <div><p className="mb-2 text-sm font-semibold text-ink">{label}</p><div className="overflow-auto rounded-xl border border-line"><table className="font-mono text-xs"><tbody>{values.map((row, index) => <tr key={index}>{row.map((item, column) => <td className="border-b border-r border-line px-2 py-1 text-right" key={`${index}-${column}`}>{typeof item === "number" ? item.toFixed(2) : String(item)}</td>)}</tr>)}</tbody></table></div></div>; }
