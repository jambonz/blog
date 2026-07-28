// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

import mdx from '@astrojs/mdx';

// https://astro.build/config
export default defineConfig({
  // Generates sitemap-index.xml from `site` + page paths -> https://jambonz.org/blog/...
  integrations: [sitemap(), mdx()],
  // The blog is served under jambonz.org/blog. The root domain is a separate
  // Next.js app; an mt-website rewrite proxies /blog/* to this deployment.
  site: 'https://jambonz.org',
  base: '/blog',
  // jambonz.org (Next.js) strips trailing slashes, and the marketing pages are
  // slash-less, so the blog matches: no trailing slash on any URL, and pages are
  // emitted as <slug>.html (not <slug>/index.html) so they serve at the slash-less
  // path without a redirect. Keeps canonical/sitemap URLs identical to what serves.
  trailingSlash: 'never',
  // Emit files physically under dist/blog/ so the Vercel deploy serves them at
  // /blog/... with standard static handling (correct trailing-slash behavior,
  // no custom rewrite needed). Vercel's web root is dist/.
  outDir: './dist/blog',
  markdown: {
    shikiConfig: {
      themes: {
        light: 'github-light',
        dark: 'github-dark',
      },
    },
  },
});