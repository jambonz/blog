# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm run dev      # Start dev server at localhost:4321
npm run build    # Build production site to ./dist/
npm run preview  # Preview production build locally
```

When starting the dev server, use background mode:

```bash
astro dev --background
```

Manage the background server with `astro dev stop`, `astro dev status`, and `astro dev logs`.

## Architecture

This is an Astro 7 static site — the jambonz blog, served at **jambonz.org/blog**.
It deploys as its own Vercel project and is proxied under the main domain by an
`mt-website` rewrite. See `DEPLOY.md` for the topology and `MIGRATION.md` for
porting posts from Hashnode.

Key points:

- `base: '/blog'` in `astro.config.mjs` — every internal link must be built via
  `src/utils/url.ts` (`url('my-post')` -> `/blog/my-post/`), because Astro does
  not auto-prefix hand-written hrefs. `site` is `https://jambonz.org`.
- `src/pages/` - File-based routing. `index.astro` is the post listing (served
  at `/blog/`); `[slug].astro` renders a post (`/blog/<slug>/`). There is **no**
  `src/pages/blog/` subfolder — `base` already supplies the `/blog` segment.
- `src/layouts/` - `BaseLayout.astro` (head, theme toggle, brand nav, canonical
  + OpenGraph) and `PostLayout.astro` (post header, cover, tags, prose).
- `src/content/` - Blog content collection.
- `public/` - Static files (note: referenced as `/blog/...` since `base` applies).

## Content Collections

Each post is a **folder** so its images co-locate with its markdown:

```
src/content/blog/<slug>/
  index.md      # folder name is the slug -> /blog/<slug>/
  cover.jpg     # referenced relatively as ./cover.jpg
```

Flat `src/content/blog/<slug>.md` files also work (no co-located images).
Files/folders beginning with `_` are ignored by the loader.

Schema (`src/content.config.ts`):

```yaml
---
title: "Post Title"          # required
date: 2024-01-15             # required, coerced to UTC Date, rendered in UTC
updatedDate: 2024-02-01      # optional
description: "..."           # optional, used in <meta> + listing
author: "Dave Horton"        # optional, defaults to "jambonz"
tags: ["llm", "voice-ai"]    # optional
coverImage: "./cover.jpg"    # optional, co-located image (optimized) or remote URL
canonicalUrl: "https://..."  # optional; OMIT for migrated posts (self-canonical)
draft: false                 # optional; true hides from the live PRODUCTION site
---                          #   but still renders in local + Vercel preview builds
```

Posts are accessed via `getPosts()` (`src/utils/posts.ts`), which sorts newest
first and drops drafts only when `VERCEL_ENV === 'production'` — so authors can
preview unpublished posts on Vercel preview deployments. Rendered at
`/blog/<slug>/`. The `WRITING.md` guide documents the GitHub-web authoring flow
for non-developer content editors.

## Theming

The site supports light/dark mode via `data-theme` attribute on `<html>`:
- System preference respected by default
- Manual toggle stores preference in `localStorage`
- Code blocks use Shiki dual themes (`github-light`/`github-dark`) configured in `astro.config.mjs`

CSS custom properties for colors are defined in `BaseLayout.astro` and respond to both `prefers-color-scheme` media query and `data-theme` attribute.

## Astro Component Structure

Astro components (`.astro` files) have two parts:
1. **Frontmatter** (between `---` fences) - Server-side JavaScript for imports and data
2. **Template** - HTML-like markup with `<style>` and `<script>` tags

Styles in `<style>` tags are scoped to the component by default. Use `:global()` for styles that need to affect rendered markdown content.

## Documentation

Full documentation: https://docs.astro.build
