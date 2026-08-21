import { Activity } from "lucide-react";

export function BrandMark() {
  return <div className="flex items-center gap-3" aria-label="MathVision AI"><div className="grid size-10 place-items-center rounded-xl bg-brand text-white shadow-sm" aria-hidden="true"><Activity size={22} strokeWidth={2.5} /></div><div className="min-w-0"><p className="truncate text-sm font-semibold tracking-tight text-ink">MathVision AI</p><p className="text-xs text-ink-muted">Scientific image intelligence</p></div></div>;
}
