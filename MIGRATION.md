# Porting posts from Hashnode

Each post is a folder so its images live next to its markdown:

```
src/content/blog/<slug>/
  index.md        # the post
  cover.jpg       # optional cover image
  diagram.png     # any in-body images
```

The folder name is the slug and becomes the URL: `/blog/<slug>/`.
**Keep the slug identical to the Hashnode slug** so the old→new redirect
(DEPLOY.md, Step 4) is a clean 1:1 map and inbound links survive.

## Per-post steps

1. **Create the folder** `src/content/blog/<hashnode-slug>/`.

2. **Grab the markdown.** On Hashnode, each post has a "..." → *Edit* view you
   can copy markdown from, or use the member export. Save it as `index.md`.

3. **Write the frontmatter** (schema in `src/content.config.ts`):

   ```yaml
   ---
   title: "How to stream text from LLMs using jambonz"   # required
   date: 2024-11-12                                       # required (publishedAt)
   updatedDate: 2025-01-04                                # optional
   description: "One-line summary / Hashnode subtitle."   # optional, used in <meta>
   author: "Dave Horton"                                  # optional, defaults to "jambonz"
   tags: ["llm", "streaming", "voice-ai"]                 # optional
   coverImage: "./cover.jpg"                              # optional, co-located
   draft: false                                           # omit or false to publish
   ---
   ```

   Do **not** set `canonicalUrl` for migrated posts — leaving it unset makes the
   new jambonz.org/blog URL canonical, which is what you want when retiring
   Hashnode. Only set it if a post stays primarily hosted somewhere else.

4. **Download the images.** Hashnode bodies reference absolute
   `https://cdn.hashnode.com/...` URLs. Download each into the post folder and
   switch the markdown reference to a relative path:

   ```markdown
   <!-- before -->
   ![diagram](https://cdn.hashnode.com/res/hashnode/image/upload/v123/abc.png)
   <!-- after -->
   ![diagram](./diagram.png)
   ```

   Relative images (and the `coverImage`) are optimized by Astro and get the
   `/blog` base prefix automatically at build time. Absolute remote URLs are
   left untouched (and unoptimized), so prefer downloading.

   Quick pull of every image in a file:

   ```bash
   cd src/content/blog/<slug>/
   grep -oE 'https://cdn\.hashnode\.com/[^) ]+' index.md \
     | while read u; do curl -sO "$u"; done
   ```
   Then rename the downloaded files to something meaningful and fix the refs.

5. **Preview** with `npm run dev` → http://localhost:4321/blog/ and check the
   post renders, images load, and code blocks highlight.

## Notes

- `date` is date-only and rendered in **UTC**, so it shows exactly as authored
  regardless of the builder's timezone.
- Posts with `draft: true` are hidden from the live production site but still
  render in local and Vercel preview builds, so authors can review them.
- Files and folders whose name starts with `_` are ignored by the loader
  (handy for scratch / work in progress).
