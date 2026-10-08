# Atelier 8 — site

Site du studio de motion design Atelier 8 (Paris — Hong Kong), publié sur https://atelier8.io via GitHub Pages.

- `docs/` : le site publié (GitHub Pages → branche `main`, dossier `/docs`). `CNAME` = atelier8.io.
- `src/` : sources (fragments `k1`…`k5.html`, `mark.json`, `lenis.min.js`). `python3 src/build.py` régénère `docs/index.html`.
- Médias : `docs/media/films/{slug}.mp4|.jpg|-md.mp4` (vidéo galerie 800 px sans son), hero `docs/media/hero-scrub*.mp4`.

Mise en ligne : chaque commit poussé sur `main` est publié automatiquement par GitHub Pages (1 à 2 min).
