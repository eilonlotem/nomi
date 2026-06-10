import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => ({
  plugins: [vue()],
  // Strip console.* and debugger statements only in production builds
  esbuild: {
    drop: mode === 'production' ? ['console', 'debugger'] : [],
  },
}))
