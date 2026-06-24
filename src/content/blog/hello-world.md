---
title: "Hello World"
date: 2024-01-15
description: "A first post to test typography and code highlighting."
---

This is a sample post to test the blog styling. The goal is clean, readable typography with first-class code blocks.

## Code Examples

Here's some TypeScript:

```typescript
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    description: z.string().optional(),
  }),
});

export const collections = { blog };
```

And some shell commands:

```bash
npm install
npm run dev
```

Inline code looks like `this` and should be subtle but readable.

## Why This Matters

When you write technical content, code is the substance. Everything else—typography, whitespace, navigation—should support it without distraction. A reader scanning for a function signature or a config snippet should find it immediately.

The measure (line length) should sit around 65–75 characters for comfortable reading. Too wide and the eye loses its place; too narrow and the text feels cramped.
