// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  // Generates sitemap-index.xml from `site` + page paths -> https://jambonz.org/blog/...
  integrations: [sitemap()],
  // The blog is served under jambonz.org/blog. The root domain is a separate
  // Next.js app; an mt-website rewrite proxies /blog/* to this deployment.
  site: 'https://jambonz.org',
  base: '/blog',
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
