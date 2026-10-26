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

The French service overview and quote form are available. Detailed service, location, product and policy pages remain predominantly English and need a separate full translation pass.
