import { BookOpenText, BrainCircuit, CircleHelp, FlaskConical, GitCompareArrows, House, ImageUp } from "lucide-react";
import type { LucideIcon } from "lucide-react";

export type NavigationItem = { label: string; path: string; icon: LucideIcon; phase?: string };

export const navigationItems: NavigationItem[] = [
  { label: "Home", path: "/", icon: House },
  { label: "Workspace", path: "/workspace", icon: ImageUp, phase: "P2" },
  { label: "Compare", path: "/compare", icon: GitCompareArrows, phase: "P4" },
  { label: "Mathematics", path: "/mathematics", icon: BookOpenText, phase: "P6" },
  { label: "Model Insights", path: "/model-insights", icon: BrainCircuit, phase: "P5" },
  { label: "Experiments", path: "/experiments", icon: FlaskConical, phase: "P4" },
  { label: "About", path: "/about", icon: CircleHelp, phase: "P6" },
];
