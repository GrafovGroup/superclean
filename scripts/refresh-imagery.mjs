import fs from 'node:fs';
import path from 'node:path';

const publicDir = path.resolve(import.meta.dirname, '../public');
const industries = ['offices', 'property-management', 'fitness-recreation', 'hospitality', 'public-facilities', 'retail', 'industrial'];
const homepage = {
  'commercial-janitorial': 'home-janitorial',
  'power-washing': 'home-power-washing',
  'post-construction-cleaning': 'home-construction',
  'building-structure-cleaning': 'home-high-dusting',
  'exhaust-hood-cleaning': 'home-hood',
  'window-cleaning': 'home-window',
  'gym-cleaning': 'home-gym',
};

for (const file of fs.readdirSync(publicDir, {recursive: true})) {
  if (!file.endsWith('.html')) continue;
  const full = path.join(publicDir, file);
  const before = fs.readFileSync(full, 'utf8');
  let html = before;
  for (const industry of industries) {
    html = html.replaceAll(`/assets/industry-${industry}.svg`, `/assets/photos/industry-${industry}-original.webp`)
      .replaceAll(`/assets/industry-${industry}-fr.svg`, `/assets/photos/industry-${industry}-original.webp`);
  }
  if (['index.html', 'services-de-nettoyage.html'].includes(file)) {
    html = html.replace(/<img\b[^>]*>/g, tag => {
      for (const [original, replacement] of Object.entries(homepage)) {
        if (!tag.includes(`/assets/photos/${original}.webp`)) continue;
        return tag.replaceAll(`/assets/photos/${original}.webp`, `/assets/photos/${replacement}-original.webp`)
          .replace(/ srcset="[^"]*"/g, '')
          .replace(/ alt="[^"]*"/, ` alt="${file === 'index.html' ? {
            'home-janitorial': 'Cleaning a glass partition in a commercial office',
            'home-power-washing': 'Pressure washing a commercial entrance',
            'home-construction': 'Vacuuming a newly completed office',
            'home-high-dusting': 'Removing overhead warehouse dust with an extension pole',
            'home-hood': 'Cleaning a commercial kitchen hood filter',
            'home-window': 'Washing storefront windows from ground level',
            'home-gym': 'Wiping a bench in a fitness centre',
          }[replacement] : {
            'home-janitorial': 'Nettoyage d’une cloison vitrée dans un bureau',
            'home-power-washing': 'Lavage à pression d’une entrée commerciale',
            'home-construction': 'Aspiration dans un bureau après construction',
            'home-high-dusting': 'Dépoussiérage en hauteur avec une perche dans un entrepôt',
            'home-hood': 'Nettoyage d’un filtre de hotte de cuisine commerciale',
            'home-window': 'Lavage des vitrines depuis le sol',
            'home-gym': 'Essuyage d’un banc dans un centre sportif',
          }[replacement]}"`);
      }
      return tag;
    });
  }
  if (html !== before) fs.writeFileSync(full, html);
}
