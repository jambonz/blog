import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  // Each post is a folder under src/content/blog/<slug>/index.md so its images
  // can be co-located and bundled/optimized by Astro. The folder name becomes
  // the slug (route: /blog/<slug>/). Flat <slug>.md files also work.
  // Ignore anything whose file or folder name starts with `_` (scratch/work).
  loader: glob({ pattern: ['**/*.md', '!**/_*', '!**/_*/**'], base: './src/content/blog' }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      date: z.coerce.date(),
      updatedDate: z.coerce.date().optional(),
      description: z.string().optional(),
      author: z.string().default('jambonz'),
      tags: z.array(z.string()).default([]),
      // Co-located cover image (./cover.png) optimized by Astro, or a remote URL.
      coverImage: image().optional(),
      // Original Hashnode URL — emitted as <link rel="canonical"> to preserve SEO.
      canonicalUrl: z.string().url().optional(),
      draft: z.boolean().default(false),
    }),
});

export const collections = { blog };
