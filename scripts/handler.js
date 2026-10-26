// Bundled after the immutable public documents and exact legacy redirect map.
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const safeMethod = request.method === 'GET' || request.method === 'HEAD';
    const headers = new Headers({
      'X-Content-Type-Options': 'nosniff',
      'Referrer-Policy': 'strict-origin-when-cross-origin',
      'X-Frame-Options': 'DENY',
      'Content-Security-Policy': csp,
    });
    if (!safeMethod) return new Response('Method not allowed', {status: 405, headers: {...Object.fromEntries(headers), Allow: 'GET, HEAD'}});
    let normalized = url.pathname;
    if (normalized.endsWith('/index.html')) normalized = normalized.slice(0, -11) || '/';
    else if (normalized.endsWith('.html')) normalized = normalized.slice(0, -5);
    if (normalized !== '/') normalized = normalized.replace(/\/+$/, '');
    const legacy = redirects[url.pathname] || redirects[normalized];
    if (legacy || url.hostname === 'www.superclean.ca' || (normalized !== url.pathname && documents[normalized])) {
      const target = new URL(legacy && legacy.startsWith('https://') ? legacy : 'https://superclean.ca');
      if (!legacy || !legacy.startsWith('https://')) target.pathname = legacy || normalized;
      target.search = url.search;
      headers.set('Location', target.href);
      headers.set('Cache-Control', 'public, max-age=300');
      return new Response(null, {status: 301, headers});
    }
    if (url.pathname.startsWith('/assets/') && env.ASSETS) return env.ASSETS.fetch(request);
    const document = documents[normalized] || documents['/404'];
    const status = documents[normalized] && normalized !== '/404' ? 200 : 404;
    headers.set('Content-Type', document.type);
    headers.set('Cache-Control', 'public, max-age=0, must-revalidate');
    if (url.hostname !== 'superclean.ca' || status === 404) headers.set('X-Robots-Tag', 'noindex, follow');
    return new Response(request.method === 'HEAD' ? null : document.body, {status, headers});
  }
};
