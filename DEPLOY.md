# Deploying the blog

The blog is a standalone static Astro site. It is built to run at the
`/blog` path in **every** environment (`base: '/blog'` in `astro.config.mjs`),
so what you preview standalone is byte-for-byte what ships once it's mounted
under jambonz.org. That lets you develop and deploy it independently now, and
wire it into the main site later with a one-line change.

## How the `/blog` path works

Astro prefixes every in-page URL with `/blog` (e.g. `href="/blog/my-post/"`,
`src="/blog/_astro/img.webp"`), and `outDir: './dist/blog'` (astro.config.mjs)
makes it write the **files** physically under that path:

```
dist/blog/index.html     dist/blog/my-post/index.html     dist/blog/_astro/img.webp
```

Vercel serves `dist/` as the web root, so those files are served at `/blog/...`
with its standard static handling — correct trailing-slash and directory-index
behavior, no custom path rewrite to get wrong. `vercel.json` only points Vercel
at the right output dir and redirects the bare domain root to `/blog/`:

```jsonc
{
  "outputDirectory": "dist",
  "redirects": [{ "source": "/", "destination": "/blog/", "permanent": false }]
}
```

The deployment is fully navigable at `<deploy>/blog/`. `npm run dev` and
`npm run preview` serve the same `/blog/` paths locally.

## Phase 1 — Deploy standalone (now)

1. New Vercel project pointed at this repo. Framework preset: **Astro**
   (zero-config, static — no adapter). Build `astro build`, output `dist/`.
2. Vercel reads `vercel.json` automatically. Your site is live and fully
   working at `https://jambonz-blog.vercel.app/blog/` (and `/` redirects there).

Develop locally with `npm run dev` (→ http://localhost:4321/blog/); `npm run
build && npm run preview` mirrors production. Iterate, add posts, share the
Vercel URL for review — all without touching jambonz.org.

## Phase 2 — Mount under jambonz.org/blog (later)

Because the standalone deploy already serves under `/blog`, integration is a
plain pass-through proxy — no path rewriting to reason about.

**a. Add a rewrite to `mt-website/next.config.ts`** (the blog's production
domain is `jambonz-blog.vercel.app`), alongside the existing `redirects()`:

```ts
module.exports = {
  async rewrites() {
    return [
      { source: '/blog', destination: 'https://jambonz-blog.vercel.app/blog' },
      { source: '/blog/:path*', destination: 'https://jambonz-blog.vercel.app/blog/:path*' },
    ];
  },
  async redirects() {
    return [ /* ... existing /docs redirects unchanged ... */ ];
  },
};
```

Deploy mt-website, then verify (test with and without a trailing slash, since
Astro uses directory URLs and inbound links may omit it):

```bash
curl -sI https://jambonz.org/blog/ | head -1
curl -sI https://jambonz.org/blog/streaming-text-from-llms/ | head -1
curl -sI https://jambonz.org/blog/streaming-text-from-llms  | head -1
```

**b. Repoint the links in mt-website** from the Hashnode blog to `/blog`:

| File | Current |
|------|---------|
| `src/components/Header/HeaderMenu.tsx` (two spots) | `https://blog.jambonz.org/` |
| `src/components/Footer/FooterMenu.tsx` | `https://blog.jambonz.org/` |
| `src/sections/TopBar/TopBar.tsx` | `https://blog.jambonz.org/installing-jambonz-using-aws-marketplace` |

The home page hard-codes three featured articles in
`src/app/(home)/sections/HeadingBlog/HeadingBlog.tsx` with
`https://blog.jambonz.org/<slug>` URLs — switch to `/blog/<slug>` once those
posts are ported (keep slugs identical; see MIGRATION.md).

**c. Redirect the old Hashnode blog** — 301 `blog.jambonz.org/<slug>` →
`jambonz.org/blog/<slug>`. Identical slugs make this a clean 1:1 map.
