import fs from 'node:fs';
import path from 'node:path';
import './refresh-imagery.mjs';
import './refresh-city-imagery.mjs';
import {execFileSync} from 'node:child_process';
execFileSync('python3', [path.resolve(import.meta.dirname, 'improve-search-ux.py')], {stdio: 'inherit'});

const root = path.resolve(import.meta.dirname, '..');
const publicDir = path.join(root, 'public');
const dist = path.join(root, 'dist');
const documents = {};
for (const file of fs.readdirSync(publicDir, {recursive: true})) {
  const absolute = path.join(publicDir, file);
  if (!fs.statSync(absolute).isFile() || file.startsWith('assets/')) continue;
  if (file.endsWith('.html')) {
    documents[file === 'index.html' ? '/' : '/' + file.slice(0, -5)] = {body: fs.readFileSync(absolute, 'utf8'), type: 'text/html; charset=utf-8'};
  } else if (['robots.txt', 'sitemap.xml', JSON.parse(fs.readFileSync(path.join(root, 'content/indexnow.json'), 'utf8')).keyFile].includes(file)) {
    documents['/' + file] = {body: fs.readFileSync(absolute, 'utf8'), type: file.endsWith('.xml') ? 'application/xml; charset=utf-8' : 'text/plain; charset=utf-8'};
  }
}
const redirects = {};
for (const line of fs.readFileSync(path.join(publicDir, '_redirects'), 'utf8').trim().split('\n')) {
  const [source, target, status] = line.trim().split(/\s+/);
  if (status !== '301') throw new Error('Unsupported redirect');
  redirects[source] = target;
}
const csp = fs.readFileSync(path.join(publicDir, '_headers'), 'utf8').match(/Content-Security-Policy: (.+)/)[1];
fs.rmSync(dist, {recursive: true, force: true});
fs.mkdirSync(path.join(dist, 'server'), {recursive: true});
fs.mkdirSync(path.join(dist, 'client'), {recursive: true});
fs.cpSync(path.join(publicDir, 'assets'), path.join(dist, 'client/assets'), {recursive: true});
fs.writeFileSync(path.join(dist, 'server/index.js'),
  `const documents=${JSON.stringify(documents)};\nconst redirects=${JSON.stringify(redirects)};\nconst csp=${JSON.stringify(csp)};\n` + fs.readFileSync(path.join(root, 'scripts/handler.js'), 'utf8'));
console.log(`Built ${Object.keys(documents).length} documents and ${Object.keys(redirects).length} redirect variants.`);
