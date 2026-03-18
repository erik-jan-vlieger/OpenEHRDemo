import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  root: '.',
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        ulcusCruris: resolve(__dirname, 'ulcus-cruris.html'),
        diabetischeVoet: resolve(__dirname, 'diabetische-voet.html'),
        wondprotocol: resolve(__dirname, 'wondprotocol.html'),
      },
    },
  },
  server: {
    port: 5173,
    open: true,
  },
});
