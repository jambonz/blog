import { getCollection } from 'astro:content';

// Hide drafts only on the live production deploy. Everywhere else — local dev
// and Vercel *preview* deployments (VERCEL_ENV='preview') — drafts are shown so
// an author can review unpublished work before flipping `draft: false`.
const showDrafts = process.env.VERCEL_ENV !== 'production';

/** Published posts (drafts included off-production), newest first. */
export async function getPosts() {
  const posts = await getCollection('blog', ({ data }) => showDrafts || !data.draft);
  return posts.sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());
}
