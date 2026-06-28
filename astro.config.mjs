// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  // The blog is served under jambonz.org/blog. The root domain is a separate
  // Next.js app; an mt-website rewrite proxies /blog/* to this deployment.
  site: 'https://jambonz.org',
  base: '/blog',
  markdown: {
    shikiConfig: {
      themes: {
        light: 'github-light',
        dark: 'github-dark',
      },
    },
  },
});
