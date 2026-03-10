import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// En Docker: API_TARGET = http://auth_service:8000
// En dev local: API_TARGET = http://localhost:8000
const API_TARGET = process.env.VITE_API_URL || 'http://localhost:8000';
const STUDENTS_TARGET = process.env.VITE_STUDENTS_URL || 'http://localhost:8001';
const COURSES_TARGET = process.env.VITE_COURSES_URL || 'http://localhost:8002';
const ENROLLMENTS_TARGET = process.env.VITE_ENROLLMENTS_URL || 'http://localhost:8003';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    // true = acepta cualquier host (solo dev). En producción usar etapa 'prod' del Dockerfile.
    allowedHosts: true,
    proxy: {
      // 1. Microservicios específicos (deben ir primero)
      '/api/students': { 
        target: STUDENTS_TARGET, 
        changeOrigin: true,
        headers: { 'Host': 'localhost' },
        rewrite: (path) => path.replace(/^\/api\/students/, '/api')
      },
      '/api/courses': { 
        target: COURSES_TARGET, 
        changeOrigin: true,
        headers: { 'Host': 'localhost' },
        rewrite: (path) => path.replace(/^\/api\/courses/, '/api')
      },
      '/api/enrollments': { 
        target: ENROLLMENTS_TARGET, 
        changeOrigin: true,
        headers: { 'Host': 'localhost' },
        rewrite: (path) => path.replace(/^\/api\/enrollments/, '/api')
      },
      '/api/curriculum': { 
        target: process.env.VITE_CURRICULUM_URL || 'http://localhost:8005', 
        changeOrigin: true,
        headers: { 'Host': 'localhost' },
        rewrite: (path) => path.replace(/^\/api\/curriculum/, '/api')
      },
      '/api/grades': { 
        target: process.env.VITE_GRADES_URL || 'http://localhost:8004', 
        changeOrigin: true,
        headers: { 'Host': 'localhost' },
        rewrite: (path) => path.replace(/^\/api\/grades/, '/api')
      },
      
      // 2. Auth Service & Genéricos (último recurso para /api/*)
      '/api': {
        target: API_TARGET,
        changeOrigin: true,
        headers: { 'Host': 'localhost' },
      },
      
      // Panel Django viejo (enlaces directos)
      '/system-admin': { target: API_TARGET, changeOrigin: true, headers: { 'Host': 'localhost' } },
      '/panel/constancias': {
        target: API_TARGET,
        changeOrigin: true,
      },
    },
  },
});
