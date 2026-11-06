import motionCanvasModule from '@motion-canvas/vite-plugin';
import {defineConfig} from 'vite';

const motionCanvas = motionCanvasModule.default ?? motionCanvasModule;
export default defineConfig({
  plugins: [motionCanvas({project: './src/project.ts', output: './output', proxy: false})],
  server: {host: '127.0.0.1', port: 5199, strictPort: true},
});
