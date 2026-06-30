# SEO

How search/LLM optimization works on this blog, what's automatic, and what you
set per post. (Authoring basics live in [WRITING.md](WRITING.md).)

SEO here is **three layers**: per-post frontmatter → a layout that turns it into
`<head>` tags → a few site-wide files. Astro has no magic — the `<head>` is just
HTML we control in `src/layouts/BaseLayout.astro`.

## What you set per post (frontmatter)

| Field | Drives | Guidance |
|---|---|---|
| `title` | `<title>`, `og:title`, JSON-LD headline | Unique, ≤~60 chars, keyword near the front |
| `description` | meta description, `og:description`, JSON-LD, RSS | ~150–160 chars, written to earn the click — **also what LLMs quote** |
| `date` / `updatedDate` | `article:published_time` / `modified_time`, JSON-LD | Freshness signal |
| `author` | `article:author`, JSON-LD author | Real name → E-E-A-T |
| `tags` | `article:tag`, JSON-LD keywords | 3–6 specific terms, not keyword soup |
| `coverImage` | `og:image` (social/search/LLM thumbnail) | Co-located image, ideally ~1200×630. Omit and the post uses the default card. |

All of these are defined in `src/content.config.ts`.

## What's automatic (handled by the layouts/config — you don't touch these)

Every page (`BaseLayout.astro`):
- `<title>`, meta `description`
- `<link rel="canonical">` — self-referential, absolute. Correct **under the
  Vercel proxy** because `astro.config.mjs` sets `site: 'https://jambonz.org'`
  + base `/blog`, so it resolves to `https://jambonz.org/blog/<slug>/` (not the
  `vercel.app` mirror). This dedupes the two and points ranking at the real URL.
- Open Graph (`og:type` = `website` on the listing, `article` on posts) + Twitter card
- `og:image` — the post's `coverImage`, or `public/og-default.jpg` as a branded fallback
- RSS autodiscovery `<link rel="alternate" type="application/rss+xml">`

Every post additionally gets:
- `article:published_time` / `modified_time` / `author` / `tag`
- **`BlogPosting` JSON-LD** — Google rich results + machine-readable facts for LLMs

Site-wide:
- **Sitemap** (`@astrojs/sitemap`) → `/blog/sitemap-index.xml`, absolute `jambonz.org/blog/...` URLs
- **RSS feed** (`src/pages/rss.xml.js`) → `/blog/rss.xml`

Drafts (`draft: true`) are excluded from sitemap, RSS, and the build on production
(`VERCEL_ENV=production`) but still render on previews — see `src/utils/posts.ts`.

## For LLMs specifically
- **Clean semantic HTML** — one `<h1>`, real heading hierarchy (enforced when porting).
- **JSON-LD + author + date** give models provenance to cite.
- **Front-load the answer** — LLMs weight the first paragraph + description heavily.
- **Don't block AI crawlers** (GPTBot, ClaudeBot, PerplexityBot, Google-Extended) in
  robots.txt if you want to be cited.

## Not handled here (deliberately)
- **`robots.txt`** must live at `jambonz.org/robots.txt` — the domain root, which is
  the **mt-website** Next.js app, not this blog (the blog only owns `/blog/*`). It
  should carry `Sitemap: https://jambonz.org/blog/sitemap-index.xml`.
- **Per-post cover images** — posts currently share `og-default.jpg`; bespoke
  ~1200×630 covers lift social/search click-through.
- **Search Console** — submit `https://jambonz.org/blog/sitemap-index.xml` once live.

Highest-leverage order if extending: per-post cover images → robots.txt (mt-website)
→ Search Console submission.
