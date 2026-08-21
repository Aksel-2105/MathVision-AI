import { useState } from "react";
import { Outlet } from "react-router-dom";

import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

export function AppShell() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  return <div className="min-h-screen bg-page text-ink"><div className={`mobile-overlay ${mobileOpen ? "mobile-overlay-open" : ""}`} aria-hidden="true" onClick={() => setMobileOpen(false)} /><div className={`mobile-sidebar ${mobileOpen ? "mobile-sidebar-open" : ""}`} aria-hidden={!mobileOpen}>{mobileOpen && <Sidebar collapsed={false} onToggle={() => setMobileOpen(false)} onNavigate={() => setMobileOpen(false)} />}</div><div className="hidden lg:block"><Sidebar collapsed={collapsed} onToggle={() => setCollapsed((current) => !current)} /></div><div className={`app-content ${collapsed ? "app-content-collapsed" : ""}`}><TopBar onMenu={() => setMobileOpen(true)} /><main className="mx-auto w-full max-w-[1440px] px-4 py-6 sm:px-6 lg:px-8"><Outlet /></main></div></div>;
}
