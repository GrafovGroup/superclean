import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const routes = JSON.parse(fs.readFileSync(path.join(root, 'content/city-image-routes.json'), 'utf8'));
routes.push(...JSON.parse(fs.readFileSync(path.join(root, 'content/city-image-legacy-routes.json'), 'utf8')));
const escape = value => value.replaceAll('&', '&amp;').replaceAll('"', '&quot;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
let updated = 0;
for (const {service, city, key, en, fr} of routes) {
  const image = `/assets/photos/cities/${key || service + '-' + city}.webp`;
  if (!fs.existsSync(path.join(root, 'public', image))) continue;
  for (const route of [en, fr]) {
    const file = path.join(root, 'public', route + '.html');
    const original = fs.readFileSync(file, 'utf8');
    const title = original.match(/<h1[^>]*>(.*?)<\/h1>/s)?.[1].replace(/<[^>]*>/g, '').replaceAll('&amp;', '&') || service.replaceAll('-', ' ');
    let matched = false;
    const html = original.replace(/<img\b[^>]*>/g, tag => {
      if (matched || !tag.includes('/assets/photos/')) return tag;
      matched = true;
      return tag.replace(/src="[^"]*"/, `src="${image}"`)
        .replace(/ srcset="[^"]*"/g, '')
        .replace(/ width="[^"]*"/, ' width="1000"')
        .replace(/ height="[^"]*"/, ' height="750"')
        .replace(/alt="[^"]*"/, `alt="${escape(title)}"`);
    });
    if (!matched) throw new Error(`No service image found on ${route}`);
    if (html !== original) { fs.writeFileSync(file, html); updated++; }
  }
}
console.log(`City imagery: updated ${updated} English/French pages.`);
