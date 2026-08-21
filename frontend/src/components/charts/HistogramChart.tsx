import type { HistogramData } from "../../schemas/api";

const seriesColors = ["#2563EB", "#DC2626", "#16A34A"];

type HistogramChartProps = { histogram: HistogramData };

export function HistogramChart({ histogram }: HistogramChartProps) {
  const width = 720;
  const height = 250;
  const padding = { top: 18, right: 18, bottom: 30, left: 42 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  const maxValue = Math.max(...histogram.series.flatMap((series) => series.values), 1);
  const buildPath = (values: number[]) => values.map((value, index) => { const x = padding.left + (index / Math.max(values.length - 1, 1)) * chartWidth; const y = padding.top + chartHeight - (value / maxValue) * chartHeight; return `${index === 0 ? "M" : "L"}${x.toFixed(2)} ${y.toFixed(2)}`; }).join(" ");
  return <figure aria-labelledby="histogram-title"><div className="mb-4 flex flex-wrap items-center justify-between gap-3"><div><h3 id="histogram-title" className="text-base font-semibold text-ink">Intensity histogram</h3><p className="mt-1 text-xs text-ink-muted">Pixel count by intensity from 0 to 255.</p></div><div className="flex flex-wrap gap-3">{histogram.series.map((series, index) => <span className="flex items-center gap-2 text-xs text-ink-muted" key={series.label}><span className="size-2 rounded-full" style={{ backgroundColor: seriesColors[index] ?? "#0891B2" }} />{series.label}</span>)}</div></div><div className="overflow-x-auto rounded-xl border border-line bg-surface-muted/40 p-2"><svg className="min-w-[560px]" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Image intensity histogram"><title>Image intensity histogram</title><line x1={padding.left} x2={width - padding.right} y1={height - padding.bottom} y2={height - padding.bottom} stroke="currentColor" className="text-line" /><line x1={padding.left} x2={padding.left} y1={padding.top} y2={height - padding.bottom} stroke="currentColor" className="text-line" /><text x={padding.left} y={height - 8} className="fill-ink-muted text-[11px]">0</text><text x={width - padding.right - 18} y={height - 8} className="fill-ink-muted text-[11px]">255</text>{histogram.series.map((series, index) => <path key={series.label} d={buildPath(series.values)} fill="none" stroke={seriesColors[index] ?? "#0891B2"} strokeWidth="2" vectorEffect="non-scaling-stroke" />)}</svg></div><figcaption className="mt-3 text-xs leading-5 text-ink-muted">The histogram describes the uploaded image only; it is not a quality score.</figcaption></figure>;
}
