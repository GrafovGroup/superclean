import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';

const routes = JSON.parse(fs.readFileSync('content/city-image-routes.json', 'utf8'));
routes.push(...JSON.parse(fs.readFileSync('content/city-image-legacy-routes.json', 'utf8')));
test('all city service pages use a unique image with matching English/French references', () => {
  const digests = new Set();
  assert.equal(routes.length, 216);
  for (const {service, city, key, en, fr} of routes) {
    const image = `/assets/photos/cities/${key || service + '-' + city}.webp`;
    const data = fs.readFileSync('public' + image);
    const digest = crypto.createHash('sha256').update(data).digest('hex');
    assert.ok(!digests.has(digest), `Duplicate image: ${image}`);
    digests.add(digest);
    assert.ok(data.length < 350_000, `Image too large: ${image}`);
    for (const route of [en, fr]) {
      const html = fs.readFileSync('public' + route + '.html', 'utf8');
      const tag = [...html.matchAll(/<img\b[^>]*>/g)].map(m => m[0]).find(t => t.includes(image));
      assert.ok(tag, `Missing city image on ${route}`);
      assert.ok(/alt="[^"]+"/.test(tag), `Missing alt text on ${route}`);
      assert.ok(!tag.includes(`/${service}-640.webp`), `Stale mobile image on ${route}`);
      assert.ok(!html.includes('image-credits-link'), `Footer credits returned on ${route}`);
    }
  }
  assert.equal(digests.size, 216);
});
