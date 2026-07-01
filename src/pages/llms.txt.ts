import { getPosts } from '../utils/posts';

// Served at /blog/llms.txt — the emerging llms.txt convention: a clean,
// link-first markdown index of the blog's content for LLMs to ingest.
export async function GET(context) {
  const posts = await getPosts();
  const body = [
    '# jambonz blog',
    '',
    '> Engineering notes and product updates from the jambonz team. jambonz is an open-source CPaaS / voice gateway for building voice applications and AI voice agents on top of SIP, WebRTC, and the major speech and LLM vendors.',
    '',
    '## Posts',
    '',
    ...posts.map((post) => {
      const url = new URL(`/blog/${post.id}`, context.site).href;
      const desc = post.data.description ? `: ${post.data.description}` : '';
      return `- [${post.data.title}](${url})${desc}`;
    }),
    '',
  ].join('\n');

  return new Response(body, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
}
