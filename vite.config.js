import fs from 'node:fs';
import path from 'node:path';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

const projectRoot = path.resolve(__dirname);
const dataDirectory = path.resolve(projectRoot, 'data');

function resolveDataFile(relativeUrl) {
  const cleanedPath = decodeURIComponent(relativeUrl).replace(/^\/+/, '');
  const resolvedPath = path.resolve(dataDirectory, cleanedPath);
  const relativePath = path.relative(dataDirectory, resolvedPath);

  if (relativePath.startsWith('..') || path.isAbsolute(relativePath)) {
    return null;
  }

  return resolvedPath;
}

function rootDataPlugin() {
  return {
    name: 'root-data-plugin',
    configureServer(server) {
      server.middlewares.use((request, response, next) => {
        const requestUrl = request.url ? request.url.split('?')[0] : '';

        if (!requestUrl.startsWith('/data/')) {
          next();
          return;
        }

        const filePath = resolveDataFile(requestUrl.slice('/data/'.length));

        if (!filePath) {
          response.statusCode = 403;
          response.end('Forbidden');
          return;
        }

        if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
          response.statusCode = 404;
          response.end('Not Found');
          return;
        }

        fs.readFile(filePath, (error, content) => {
          if (error) {
            response.statusCode = 500;
            response.end('Failed to read data file');
            return;
          }

          response.setHeader('Content-Type', 'application/json; charset=utf-8');
          response.end(content);
        });
      });
    },
    writeBundle() {
      const outputDirectory = path.resolve(projectRoot, 'dist', 'data');

      fs.rmSync(outputDirectory, { force: true, recursive: true });
      fs.cpSync(dataDirectory, outputDirectory, { recursive: true });
    }
  };
}

export default defineConfig({
  base: './',
  plugins: [vue(), rootDataPlugin()],
  build: {
    rollupOptions: {
      input: {
        main: path.resolve(projectRoot, 'index.html'),
        notFound: path.resolve(projectRoot, '404.html')
      }
    }
  }
});
