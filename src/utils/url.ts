// Build links that respect Astro's configured `base` (/blog). Astro prefixes
// `base` to assets it processes, but NOT to href/src strings you write by hand,
// so internal links must go through here. No trailing slash (trailingSlash: 'never').
//
//   url()            -> "/blog"
//   url('about')     -> "/blog/about"
//   url('/about/')   -> "/blog/about"
const BASE = import.meta.env.BASE_URL.replace(/\/$/, ''); // "/blog"

export function url(path = ''): string {
  const clean = path.replace(/^\/|\/$/g, ''); // strip leading/trailing slashes
  return clean ? `${BASE}/${clean}` : BASE;
}
