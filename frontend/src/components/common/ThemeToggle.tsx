import { Moon, Sun } from "lucide-react";

import { useTheme } from "../../app/theme";

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const nextTheme = theme === "light" ? "dark" : "light";
  return <button type="button" className="icon-button" onClick={toggleTheme} aria-label={`Switch to ${nextTheme} theme`} title={`Switch to ${nextTheme} theme`}>{theme === "light" ? <Moon size={18} /> : <Sun size={18} />}</button>;
}
