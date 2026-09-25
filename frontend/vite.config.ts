import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
  const envDir = path.resolve(__dirname, '..');
  const env = loadEnv(mode, envDir, '');
  const backendTarget = env.VITE_BACKEND_PROXY_TARGET || 'http://127.0.0.1:8400';

  return {
    envDir,
    plugins: [react(), tailwindcss()],
    server: {
      host: '0.0.0.0',
      port: 3010,
      strictPort: true,
      allowedHosts: true,
      proxy: {
        '/api': {
          target: backendTarget,
          changeOrigin: true,
        },
        '/health': {
          target: backendTarget,
          changeOrigin: true,
        },
      },
    },
    preview: {
      host: '0.0.0.0',
      port: 3010,
      strictPort: true,
    },
  };
});
