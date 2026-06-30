import rss from '@astrojs/rss';
import { getPosts } from '../utils/posts';

// Served at /blog/rss.xml (base is applied to endpoints too). Links are made
// absolute against `context.site` (https://jambonz.org).
export async function GET(context) {
  const posts = await getPosts();
  return rss({
    title: 'jambonz blog',
    description: 'Engineering notes and product updates from the jambonz team.',
    site: context.site,
    items: posts.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.date,
      link: `/blog/${post.id}/`,
    })),
  });
}
