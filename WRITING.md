# Writing posts for the jambonz blog

You don't need to install anything or use a code editor — everything below is
done in your web browser on GitHub. The blog lives at
**https://github.com/jambonz/blog**.

## One-time setup

You'll receive (from Dave):

1. An invitation to the **GitHub** repository above — click the link in the
   email and *Accept*. Create a free GitHub account if you don't have one.
2. Access to **Vercel**, which is what shows you a preview of your post before
   it goes live. Accept that invite too.

That's it — no software to install.

## How a post is organized

Each post is a **folder** inside `src/content/blog/`. The folder name becomes
the web address. For example a folder named

```
src/content/blog/my-great-post/
```

becomes `jambonz.org/blog/my-great-post/`. Inside the folder:

- `index.md` — the article itself (text + headings, written in Markdown)
- any images the post uses, sitting right next to `index.md`

Use lowercase words separated by hyphens for the folder name — no spaces.

## Write a new post

1. Go to **https://github.com/jambonz/blog** and open the folders
   `src` → `content` → `blog`.
2. Click **Add file ▸ Create new file** (top right).
3. In the filename box, type your folder and file name together, like:

   ```
   my-great-post/index.md
   ```

   Typing the `/` automatically creates the folder.
4. Paste this template into the big text box and fill it in:

   ```markdown
   ---
   title: "Your headline here"
   date: 2026-06-28
   description: "One or two sentences summarizing the post (used by Google and on the blog listing)."
   author: "Your Name"
   tags: ["tag-one", "tag-two"]
   draft: true
   ---

   Write your article here.

   ## A section heading

   A paragraph. You can make text **bold**, add a [link](https://jambonz.org),
   and write bullet lists:

   - first point
   - second point
   ```

   The part between the `---` lines is the post's settings; everything below is
   the article. Keep **`draft: true`** while you're still working — that keeps
   the post off the public site but still lets you preview it (see below).
5. Scroll down to **Commit new file**. Choose **"Create a new branch for this
   commit and start a pull request"**, then click **Propose new file**, and on
   the next screen **Create pull request**.

A "pull request" (PR) is just GitHub's word for "a set of proposed changes."
Think of it as the draft workspace for this post.

## Add images to a post

1. Open your post's folder on GitHub (e.g. `src/content/blog/my-great-post/`)
   **on your branch** (the one created in the step above).
2. Click **Add file ▸ Upload files** and drag your image in (e.g.
   `diagram.png`). Commit it to the **same branch**.
3. In `index.md`, show the image where you want it like this:

   ```markdown
   ![A short description of the image](./diagram.png)
   ```

   The `./` means "in this same folder." Always include the short description
   (it helps accessibility and SEO).

## Preview your post before it goes live

A minute or two after you create or update the pull request, a comment from
**Vercel** appears on it with a **"Visit Preview"** link. Click it to see your
post exactly as it will look, at a temporary web address. (Log in to Vercel the
first time if asked.)

Want to change something? Edit `index.md` again on your branch and commit — the
preview updates automatically after a minute.

## Publish (make it live)

When you're happy:

1. Edit `index.md` one more time and change `draft: true` to **`draft: false`**.
   Commit to the same branch.
2. On the pull request, click **Merge pull request**, then **Confirm merge**.

Your post goes live on the blog within a minute or two. Done!

## A few rules of thumb

- Only ever add or edit things inside `src/content/blog/`. Leave the other
  folders alone.
- `date` uses the format `YYYY-MM-DD` (year-month-day).
- If you want to set a post aside, just leave `draft: true` — it stays hidden
  from the public site until you set it to `false`.
- Markdown cheat sheet: <https://www.markdownguide.org/cheat-sheet/>

If anything looks wrong or you're unsure, leave the post as `draft: true` and
ask Dave to take a look before publishing.
