import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import worker from '../dist/server/index.js';
const request = (path, options) => worker.fetch(new Request('https://superclean.ca' + path, options), {});

test('all legacy redirects preserve query strings and resolve in one hop', async () => {
  for (const line of fs.readFileSync(new URL('../public/_redirects', import.meta.url), 'utf8').trim().split('\n')) {
    const [source, target] = line.split(/\s+/);
    const response = await request(source + '?utm_source=legacy');
    assert.equal(response.status, 301, source);
    const destination = new URL(target, 'https://superclean.ca'); destination.search = '?utm_source=legacy';
    assert.equal(response.headers.get('location'), destination.href);
    if (target.startsWith('/')) assert.equal((await request(target)).status, 200, target);
  }
});
test('canonical host and slash normalization do not loop', async () => {
  const response = await worker.fetch(new Request('https://www.superclean.ca/contact/?service=Windows'), {});
  assert.equal(response.status, 301); assert.equal(response.headers.get('location'), 'https://superclean.ca/contact?service=Windows');
  assert.equal((await request('/contact')).status, 200);
});
test('real pages, HEAD, indexing and 404 response stay correct', async () => {
  const home = await request('/'); assert.equal(home.status, 200); assert.equal(home.headers.get('x-robots-tag'), null); assert.ok(home.headers.get('content-security-policy'));
  const quote = await request('/contact'); assert.match(await quote.text(), /https:\/\/formspree.io\/f\/xvkovbqq/);
  assert.equal(await (await request('/contact', {method:'HEAD'})).text(), '');
  assert.equal((await request('/source/build.py')).status, 404);
  assert.equal((await request('/no-such-page')).status, 404);
  const alternate = await worker.fetch(new Request('https://superclean-ca.dimagrafov.chatgpt.site/'), {}); assert.equal(alternate.headers.get('x-robots-tag'), 'noindex, follow');
});

test('local service routes preserve their canonical URL, quote context and indexing policy', async () => {
  const routes = fs.readdirSync(new URL('../public/services/', import.meta.url), {recursive:true})
    .filter(file => file.includes('/') && file.endsWith('.html'))
    .map(file => '/services/' + file.slice(0,-5));
  assert.ok(routes.includes('/services/graffiti-removal/north-york'));
  const sitemap = await (await request('/sitemap.xml')).text();
  for (const route of routes) {
    const response = await request(route);
    assert.equal(response.status, 200, route);
    const html = await response.text();
    assert.ok(html.includes(`<link rel="canonical" href="https://superclean.ca${route}">`), route);
    assert.equal((html.match(/<h1>/g) || []).length, 1, route);
    assert.match(html, /href="\/contact\?service=[^"]+&amp;city=[^"]+"/, route);
    const shouldIndex = html.includes('name="robots" content="index,follow"');
    assert.equal(sitemap.includes(`<loc>https://superclean.ca${route}</loc>`), shouldIndex, route);
    const normalized = await request(route + '/?utm_source=local');
    assert.equal(normalized.status, 301, route);
    assert.equal(normalized.headers.get('location'), 'https://superclean.ca' + route + '?utm_source=local');
  }
});
