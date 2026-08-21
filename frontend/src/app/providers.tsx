import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { type PropsWithChildren, useEffect, useState } from "react";

import { ThemeContext, type Theme } from "./theme";

export function ThemeProvider({ children }: PropsWithChildren) {
  const [theme, setTheme] = useState<Theme>(() => window.localStorage.getItem("mathvision-theme") === "dark" ? "dark" : "light");

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    document.documentElement.style.colorScheme = theme;
    window.localStorage.setItem("mathvision-theme", theme);
  }, [theme]);

  const value = { theme, toggleTheme: () => setTheme((current) => current === "light" ? "dark" : "light") };
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 30_000, retry: 1 } } });

export function AppProviders({ children }: PropsWithChildren) {
  return <QueryClientProvider client={queryClient}><ThemeProvider>{children}</ThemeProvider></QueryClientProvider>;
}
