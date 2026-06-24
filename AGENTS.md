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

This is an Astro 7 site using the basics starter template. Key directories:

- `src/pages/` - File-based routing (`.astro` files become routes)
- `src/layouts/` - Page wrapper components
- `src/components/` - Reusable Astro components
- `src/assets/` - Images and assets processed by Astro
- `public/` - Static files served as-is

## Astro Component Structure

Astro components (`.astro` files) have two parts:
1. **Frontmatter** (between `---` fences) - Server-side JavaScript for imports and data
2. **Template** - HTML-like markup with `<style>` and `<script>` tags

Styles in `<style>` tags are scoped to the component by default.

## Documentation

Full documentation: https://docs.astro.build

Consult these guides before working on related tasks:

- [Routing and pages](https://docs.astro.build/en/guides/routing/)
- [Astro components](https://docs.astro.build/en/basics/astro-components/)
- [Framework components (React, Vue, Svelte)](https://docs.astro.build/en/guides/framework-components/)
- [Content collections](https://docs.astro.build/en/guides/content-collections/)
- [Styling and Tailwind](https://docs.astro.build/en/guides/styling/)
- [Internationalization](https://docs.astro.build/en/guides/internationalization/)
