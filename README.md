# AquaFlow Energy — investor website

Static site, no build step. Open `index.html` or serve the folder:

```bash
python3 -m http.server 8765
```

- `index.html` — main page; `faq.html` — questions and risks
- `styles.css`, `main.js` — shared styles and page behaviour
- `img/` — photography (Pexels); `img/dwg/` — AFE Rev B technical drawings as tintable SVG, plus `gen-*.svg` sheets made by `_tools/make_schematics.py`
- `team/` — portraits; `docs/` — PDFs linked from the footer
- `_notes/figures-october-2026.md` — the unit-economics figures the site carried before the November 2026 business plan

The investor enquiry form posts through FormSubmit to the address in `FORM_TO` at the top of `main.js`. The first submission triggers a one-time activation email to that address.
