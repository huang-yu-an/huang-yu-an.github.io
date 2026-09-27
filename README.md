# Yu-An Huang · Personal Academic Website

A clean, bilingual (中文 / English) academic homepage for **Yu-An Huang**
(黄裕安), tenured professor at the School of Computer Science,
Northwestern Polytechnical University (NWPU).

- Live (after deployment): **https://yu-anhuang.github.io**
- Source: this repository
- Stack: pure static **HTML + CSS + vanilla JavaScript** — no build step,
  no Ruby, no Node. The publications page reads `publications.bib`
  in the browser and renders it on the fly.

---

## Repository layout

```
yu-anhuang.github.io/
├── index.html                  ← language picker (中 / EN)
├── publications.bib            ← full BibTeX (122 entries)
├── assets/
│   ├── css/style.css
│   ├── js/bibtex.js            ← BibTeX parser & list renderer
│   └── img/
│       ├── avatar.svg          ← placeholder portrait
│       └── favicon.svg
├── zh/                         ← Chinese pages
│   ├── index.html              ← home
│   ├── publications.html
│   ├── research.html
│   ├── cv.html
│   ├── teaching.html
│   ├── news.html
│   └── contact.html
├── en/                         ← English pages (same structure)
└── _generate_pages.py          ← page-generation script (edit then re-run)
```

---

## Local preview

No build needed. Open a terminal in this folder and run:

```bash
python3 -m http.server 4000
```

Then visit <http://127.0.0.1:4000/>.

> **Note**: opening `index.html` directly via `file://` will NOT work for the
> publications page, because the browser blocks `fetch()` of `.bib` files over
> the `file://` protocol. Always use the local HTTP server.

---

## Updating content

### 1 · Add or edit a publication
Open `publications.bib` and add / update a standard BibTeX entry, e.g.:

```bibtex
@article{huang2026example,
  title={An example paper on single-cell analysis},
  author={Huang, Yu-An and Other, Author and Coauthor, Name},
  journal={Nature Methods},
  year={2026},
  volume={23},
  number={4},
  pages={456--470},
  doi={10.1038/example.2026.0001}
}
```

The publications page automatically picks it up — no rebuild required.

**Tips**

- Add `pdf = {https://.../paper.pdf}` to expose a PDF button.
- Add `code = {https://github.com/...}` to expose a Code button.
- The author `Huang, Yu-An` is auto-bolded (search for `ownerName` in
  `assets/js/bibtex.js` to change).

### 2 · Update news, research, CV, teaching, contact
Each page lives under `/zh/` and `/en/`. The cleanest workflow is to:

1. Edit `_scripts/generate_pages.py` (all content is data-driven there).
2. Run `python3 _scripts/generate_pages.py` to regenerate every page.

If you'd rather hand-edit, just edit the corresponding `.html` directly — the
generator is only used to keep both languages in sync.

### 3 · Replace the placeholder photo
Drop a real portrait at `assets/img/photo.jpg` and edit the `<img class="hero-portrait" …>`
tag in both `zh/index.html` and `en/index.html` to point at it (replace
`avatar.svg` with `photo.jpg`).

---

## Deploying to GitHub Pages

### One-time setup
1. On GitHub, create a new repository named **`yu-anhuang.github.io`**
   (must be exactly this name, public, no README / .gitignore).
2. Add the remote locally and push:
   ```bash
   git remote add origin git@github.com:yu-anhuang/yu-anhuang.github.io.git
   git add -A
   git commit -m "Initial personal academic website"
   git push -u origin main
   ```
3. On GitHub, go to **Settings → Pages → Build and deployment**:
   - Source: **Deploy from a branch**
   - Branch: **main** / **(root)**
4. Wait ~1 minute. Your site will be live at
   **https://yu-anhuang.github.io**.

### Subsequent updates
```bash
# Edit content, then:
git add -A
git commit -m "Add 2026 AAAI paper"
git push
```

GitHub Pages rebuilds automatically — refresh your browser in ~30s.

### Optional · use a custom domain
1. Buy a domain (e.g. `yu-anhuang.com`).
2. In your DNS provider, add a CNAME record pointing to `yu-anhuang.github.io`.
3. In this repo, create a file `CNAME` (no extension) containing:
   ```
   yu-anhuang.com
   ```
4. Push. In Settings → Pages, GitHub will issue a free Let's Encrypt cert.

---

## Customization cheatsheet

| Want to…                           | Edit…                                    |
| ---------------------------------- | ---------------------------------------- |
| Change site colors                 | `assets/css/style.css` (`--c-accent`)    |
| Change nav links / titles          | `_generate_pages.py` (`NAV_ZH`/`NAV_EN`) |
| Change the homepage hero text      | `_generate_pages.py` (`hero_html`)       |
| Change labels on publications page | `_generate_pages.py` (`publications_body`) |
| Add a new page                     | add to `NAV_*` and a new `*_body()` fn   |
| Tweak the BibTeX parser            | `assets/js/bibtex.js`                    |

---

## License

Content © Yu-An Huang. Code released under MIT — feel free to fork and adapt.
