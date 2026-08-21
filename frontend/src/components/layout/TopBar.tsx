import { Menu, Sparkles } from "lucide-react";

import { ThemeToggle } from "../common/ThemeToggle";

type TopBarProps = { onMenu: () => void };

export function TopBar({ onMenu }: TopBarProps) {
  return <header className="topbar"><button type="button" className="icon-button lg:hidden" onClick={onMenu} aria-label="Open navigation menu" title="Open navigation menu"><Menu size={20} /></button><div className="flex min-w-0 items-center gap-3"><div className="grid size-9 place-items-center rounded-lg bg-brand/10 text-brand lg:hidden"><Sparkles size={18} /></div><div className="min-w-0"><p className="truncate text-sm font-semibold text-ink">MathVision AI</p><p className="truncate text-xs text-ink-muted">Scientific image workspace</p></div></div><div className="ml-auto flex items-center gap-2"><span className="hidden rounded-full border border-line px-3 py-1 text-xs text-ink-muted sm:inline-flex">No image selected</span><ThemeToggle /></div></header>;
}
