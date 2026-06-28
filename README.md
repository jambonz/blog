# jambonz blog

The [jambonz](https://jambonz.org) blog — a static [Astro](https://astro.build)
site served at **jambonz.org/blog**.

## Develop

```sh
npm install
npm run dev      # http://localhost:4321/blog/
npm run build    # static output to ./dist/
npm run preview  # serve the production build locally
```

## How it's wired

- Built to run under the `/blog` path (`base: '/blog'` in `astro.config.mjs`).
- Deploys as its own Vercel project; the main site (`jambonz/mt-website`)
  proxies `/blog/*` to it. See **[DEPLOY.md](DEPLOY.md)**.
- Posts are markdown in `src/content/blog/`. To add one — or port a post from
  the old Hashnode blog — see **[MIGRATION.md](MIGRATION.md)**.
- Writing posts via the GitHub web UI (for non-developers): **[WRITING.md](WRITING.md)**.
- Architecture and content-schema details: **[AGENTS.md](AGENTS.md)**.
