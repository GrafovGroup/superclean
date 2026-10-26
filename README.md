# Superclean Canada

Production: https://superclean.ca

## Run and verify

Requires Node.js 22 or later. No third-party runtime dependencies.

- `npm run build` generates the Worker and assets in `dist/`.
- `npm test` checks routing and simulated form outcomes.
- `node scripts/audit.mjs` audits page links, headings, favicons and quote pages.
- `npm run dev -- --port 4173` serves the local development preview.

`public/` contains editable pages and assets. `scripts/handler.js` implements production routing. `.openai/hosting.json` retains the existing Sites identity. GitHub is the source backup; pushing here does not automatically deploy the live site. Do not commit credentials or customer inquiry records.

## Inquiry delivery

English `/contact` and French `/demande-de-devis` submit to the existing Formspree endpoint. The public form ID is not a secret. Delivery settings remain in Formspree. Confirm receipt in the destination inbox after deployment; automated tests simulate provider outcomes and do not send email.

## Language coverage

French service and location coverage includes 292 counterpart pages: 52 core services, 208 service/city pages, 8 additional local service pages, 13 provinces/territories, 9 city guides and 2 directories. The overview and quote form are also available in French. The product catalogue (23 categories and its directory) and industries (7 sectors and their directory) also have French counterparts. Policy, resource and other corporate pages remain English.

Edit `content/services-fr.tsv`, `content/regions-fr.json` and `content/cities-fr.json`, `content/products-fr.tsv` and `content/industries-fr.tsv`, then run `python3 scripts/build-french.py` (Python 3 required only for regeneration). The generated HTML is committed, so normal Node builds require no Python. `content/language-routes.json` records all equivalent URLs.

The owner confirmed live quote receipt in the inbox on October 26, 2026.
