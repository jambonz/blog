# SEO

How search/LLM optimization works on this blog: what's automatic, what you set
per post, and what's intentionally handled elsewhere. (Authoring basics live in
[WRITING.md](WRITING.md).)

SEO here is **three layers**: per-post frontmatter → a layout that turns it into
`<head>` tags → a few site-wide files. Astro has no magic — the `<head>` is just
HTML controlled in `src/layouts/BaseLayout.astro`.

## What you set per post (frontmatter)

| Field | Drives | Guidance |
|---|---|---|
| `title` | `<title>`, `og:title`, JSON-LD headline | Unique, ≤~60 chars, keyword near the front |
| `description` | meta description, `og:description`, JSON-LD, RSS | ~150–160 chars — also what LLMs quote |
| `date` / `updatedDate` | `article:published_time` / `modified_time`, JSON-LD | Freshness signal |
| `author` | `article:author`, JSON-LD author (+ `sameAs`, see below) | Real name → E-E-A-T |
| `tags` | `article:tag`, JSON-LD keywords | 3–6 specific terms |
| `coverImage` | `og:image` | Co-located image ~1200×630; omit → default card |
| `faq` | visible FAQ section + `FAQPage` JSON-LD | Q&A that AI/Google can lift directly (see WRITING.md) |
| `canonicalUrl` | overrides the self-referential canonical | Only for cross-posts; omit normally |
| `draft` | hides from production build/sitemap/RSS | Still visible on previews |

## What's automatic (layouts/config — don't touch per post)

Every page (`BaseLayout.astro`):
- `<title>`, meta description, and a self-referential absolute **canonical**.
- Open Graph (`og:type` = website on listing / article on posts) + Twitter `summary_large_image`; `og:image` = the post's `coverImage` or a branded default card.
- **GA4** analytics (shared property `G-H2EK984KDM`, same as the marketing site).
- RSS autodiscovery `<link rel="alternate">`.

Every post additionally:
- `article:*` OG tags and **`BlogPosting` JSON-LD**.
- **FAQPage JSON-LD** when `faq` is set (rendered visibly so the structured data is legitimate).

Structured-data identity (in `BaseLayout.astro`):
- **Organization** `jambonz` — `url`, `logo`, `sameAs` (GitHub, LinkedIn company, X). Reused as the JSON-LD publisher.
- **Author** — `Person` with per-author `sameAs` from the `authorProfiles` map (e.g. Dave Horton → LinkedIn + GitHub). Add new authors there.

Site-wide:
- **Sitemap** → `/blog/sitemap-index.xml` (absolute `jambonz.org/blog/...` URLs).
- **RSS** → `/blog/rss.xml`.
- **llms.txt** → `/blog/llms.txt` — link-first index of posts for LLM ingestion.

## Canonicalization (already set up)
- **Apex `jambonz.org` is canonical**; `www` 308-redirects to it.
- URLs are **slash-less** (`trailingSlash: 'never'`), matching the rest of the
  domain, so canonical/sitemap URLs resolve `200` with no redirect.
- Because `site` = `https://jambonz.org`, the vercel.app proxy origin is deduped
  by the canonical.

## For LLM / AI answer engines
Technical foundation (done): AI crawlers allowed in robots.txt, JSON-LD
(BlogPosting + FAQPage), Organization + author entities, `llms.txt`, clean
single-H1 semantics, front-loaded descriptions. The ongoing lever is **content**:
original data/benchmarks, question-shaped posts, comparison/"alternatives to"
content, and getting referenced on dev communities (GitHub, HN, Reddit).

## Handled elsewhere / open items
- **`robots.txt`** lives at `jambonz.org/robots.txt` — the **mt-website** Next app
  (`src/app/robots.ts`), not this repo — allow-all + both sitemaps.
- **Search Console:** both sitemaps are submitted to the `jambonz.org` Domain
  property (done). Monitor indexing there.
- **Per-post cover images:** posts share the default card until given a `coverImage`.
- **GA4 consent:** analytics runs site-wide; add a consent mechanism if your
  audience/GDPR posture requires it.

Implementation: `BaseLayout.astro` (head, JSON-LD, GA4), `PostLayout.astro` (FAQ
render), `src/pages/rss.xml.js`, `src/pages/llms.txt.ts`, `astro.config.mjs`
(sitemap, trailingSlash), and mt-website `src/app/robots.ts`.
