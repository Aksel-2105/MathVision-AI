import type { ReactNode } from "react";

type StatusBadgeProps = { children: ReactNode; tone?: "blue" | "violet" | "muted" };

export function StatusBadge({ children, tone = "blue" }: StatusBadgeProps) { return <span className={`status-badge status-badge-${tone}`}>{children}</span>; }
