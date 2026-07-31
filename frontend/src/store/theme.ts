import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ThemeState {
  darkMode: boolean
  toggleDarkMode: () => void
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      darkMode: true,
      toggleDarkMode: () =>
        set((s) => {
          const next = !s.darkMode
          document.documentElement.setAttribute('data-theme', next ? 'dark' : 'light')
          return { darkMode: next }
        }),
    }),
    { name: 'chre-theme' },
  ),
)
