const GLOBAL_BASE_KEY = '__OI_RECORDS_BASE_PATH__';

function normalizeBasePath(basePath) {
  if (!basePath || typeof basePath !== 'string') {
    return '/';
  }

  const withLeadingSlash = basePath.startsWith('/') ? basePath : `/${basePath}`;
  return withLeadingSlash.endsWith('/') ? withLeadingSlash : `${withLeadingSlash}/`;
}

export function getAppBasePath() {
  if (typeof window === 'undefined') {
    return '/';
  }

  return normalizeBasePath(window[GLOBAL_BASE_KEY] || '/');
}

export function buildAppPath(relativePath = '') {
  const basePath = getAppBasePath();
  const cleanedPath = relativePath.replace(/^\/+/, '');

  return cleanedPath ? `${basePath}${cleanedPath}` : basePath;
}

