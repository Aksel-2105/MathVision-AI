import { PanelLeftClose, PanelLeftOpen, Settings2 } from "lucide-react";
import { NavLink } from "react-router-dom";

import { BrandMark } from "../common/BrandMark";
import { ThemeToggle } from "../common/ThemeToggle";
import { navigationItems } from "./navigation";

type SidebarProps = { collapsed: boolean; onToggle: () => void; onNavigate?: () => void };

export function Sidebar({ collapsed, onToggle, onNavigate }: SidebarProps) {
  return <aside className={`sidebar ${collapsed ? "sidebar-collapsed" : ""}`} aria-label="Primary navigation">
    <div className="flex items-center justify-between gap-3 px-4 py-5">{!collapsed && <BrandMark />}<button type="button" className="icon-button shrink-0" onClick={onToggle} aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"} title={collapsed ? "Expand sidebar" : "Collapse sidebar"}>{collapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}</button></div>
    <nav className="flex-1 space-y-1 px-3" aria-label="Application pages">{navigationItems.map(({ label, path, icon: Icon, phase }) => <NavLink key={path} to={path} end={path === "/"} onClick={onNavigate} className={({ isActive }) => `nav-item ${isActive ? "nav-item-active" : ""}`} title={collapsed ? `${label}${phase ? ` · ${phase}` : ""}` : undefined}><Icon size={19} aria-hidden="true" />{!collapsed && <><span className="truncate">{label}</span>{phase && <span className="ml-auto text-[10px] font-semibold text-ink-muted">{phase}</span>}</>}</NavLink>)}</nav>
    <div className="space-y-3 border-t border-line px-3 py-4">{!collapsed && <p className="px-3 text-[11px] font-semibold uppercase tracking-[0.18em] text-ink-muted">Platform status</p>}<div className={`flex items-center gap-3 rounded-xl bg-cyan/10 px-3 py-2.5 text-xs text-cyan ${collapsed ? "justify-center" : ""}`} title={collapsed ? "Platform status" : undefined}><span className="size-2 rounded-full bg-cyan" aria-hidden="true" />{!collapsed && <span>Phase 6 complete</span>}</div><div className={`flex items-center gap-2 ${collapsed ? "justify-center" : "justify-between"}`}><ThemeToggle />{!collapsed && <><span className="text-xs text-ink-muted">v0.1.0</span><button type="button" className="icon-button" aria-label="Open settings" title="Settings"><Settings2 size={18} /></button></>}</div></div>
  </aside>;
}
