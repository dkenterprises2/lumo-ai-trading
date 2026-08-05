"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

export type ColorThemeId = "slate-cyan" | "obsidian-blue" | "emerald-mint" | "violet-neon" | "fluent-light";

export interface ThemeOption {
  id: ColorThemeId;
  name: string;
  description: string;
  accentColor: string;
  bgHex: string;
  previewClass: string;
}

export const COLOR_THEMES: ThemeOption[] = [
  {
    id: "slate-cyan",
    name: "Enterprise Slate & Cyan",
    description: "Classic high-contrast dark terminal with cyan highlights",
    accentColor: "#06b6d4",
    bgHex: "#020617",
    previewClass: "bg-slate-950 border-cyan-500 text-slate-100"
  },
  {
    id: "obsidian-blue",
    name: "Obsidian & Electric Blue",
    description: "Deep obsidian backdrop with royal blue accents",
    accentColor: "#3b82f6",
    bgHex: "#090d16",
    previewClass: "bg-zinc-950 border-blue-500 text-zinc-100"
  },
  {
    id: "emerald-mint",
    name: "Emerald & Jade Mint",
    description: "Dark mint slate with glowing emerald accents",
    accentColor: "#10b981",
    bgHex: "#021a14",
    previewClass: "bg-emerald-950 border-emerald-500 text-emerald-100"
  },
  {
    id: "violet-neon",
    name: "Cyberpunk Violet & Neon",
    description: "Deep violet obsidian with electric purple accents",
    accentColor: "#a855f7",
    bgHex: "#0b0518",
    previewClass: "bg-purple-950 border-purple-500 text-purple-100"
  },
  {
    id: "fluent-light",
    name: "Fluent Pure Light",
    description: "Clean modern light theme with soft metallic borders",
    accentColor: "#0284c7",
    bgHex: "#f8fafc",
    previewClass: "bg-slate-100 border-sky-500 text-slate-900"
  }
];

interface ThemeContextType {
  theme: ColorThemeId;
  setTheme: (theme: ColorThemeId) => void;
  currentThemeOption: ThemeOption;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<ColorThemeId>("slate-cyan");

  useEffect(() => {
    const savedTheme = localStorage.getItem("lumo_color_theme") as ColorThemeId;
    if (savedTheme && COLOR_THEMES.some((t) => t.id === savedTheme)) {
      setThemeState(savedTheme);
      applyThemeToDocument(savedTheme);
    } else {
      applyThemeToDocument("slate-cyan");
    }
  }, []);

  const setTheme = (newTheme: ColorThemeId) => {
    setThemeState(newTheme);
    localStorage.setItem("lumo_color_theme", newTheme);
    applyThemeToDocument(newTheme);
  };

  const applyThemeToDocument = (t: ColorThemeId) => {
    if (typeof document !== "undefined") {
      const root = document.documentElement;
      root.setAttribute("data-theme", t);
      document.body.setAttribute("data-theme", t);
    }
  };

  const currentThemeOption = COLOR_THEMES.find((t) => t.id === theme) || COLOR_THEMES[0];

  return (
    <ThemeContext.Provider value={{ theme, setTheme, currentThemeOption }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};
