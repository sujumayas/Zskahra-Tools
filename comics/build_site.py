#!/usr/bin/env python3
"""Genera comics/index.html (galería) y comics/NN.html (lector) a partir de
comics_pages/NN/{cover.png, p01.png, ...}. Volver a correr cada vez que se
agregue un episodio nuevo a comics_pages/.

Uso: python3 build_site.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
PAGES_DIR = ROOT / "comics_pages"

FONTS = '<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;800&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">'

BASE_CSS = """
:root{--bg:#110e08;--surface:#1e1608;--surface2:#2a1e0a;--border:#4a3418;--border-light:#6a4d28;--gold:#c8a045;--gold-dim:#8a6a2a;--cream:#e8d5a0;--cream-dim:#a08850}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--cream);font-family:'Crimson Text',Georgia,serif;font-size:17px;line-height:1.5;min-height:100vh}
.back-link{display:block;background:var(--surface);border-bottom:1px solid var(--border);padding:8px 16px;font-family:'Cinzel',serif;font-size:11px;letter-spacing:2px;color:var(--gold-dim);text-decoration:none;text-transform:uppercase;transition:color .15s}
.back-link:hover{color:var(--gold)}
header{background:var(--surface);border-bottom:2px solid var(--gold);padding:20px 16px 14px;text-align:center;position:sticky;top:0;z-index:100}
header h1{font-family:'Cinzel',serif;font-size:22px;font-weight:800;color:var(--gold);letter-spacing:3px;text-transform:uppercase}
header p{font-size:13px;color:var(--cream-dim);margin-top:3px;font-style:italic}
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border-light);border-radius:3px}
"""

GALLERY_CSS = """
main{padding:20px 16px 40px;max-width:900px;margin:0 auto}
.comic-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
@media (max-width:820px){.comic-grid{grid-template-columns:repeat(3,1fr)}}
@media (max-width:600px){.comic-grid{grid-template-columns:repeat(2,1fr)}}
.comic-card{display:block;text-decoration:none;color:inherit;border:1px solid var(--border);border-radius:6px;overflow:hidden;background:var(--surface2);transition:border-color .15s,transform .1s}
.comic-card:hover{border-color:var(--gold-dim);transform:translateY(-2px)}
.comic-card img{display:block;width:100%;aspect-ratio:2/3;object-fit:cover;background:var(--bg)}
.comic-card .comic-label{padding:10px 10px 12px;text-align:center}
.comic-card .comic-title{font-family:'Cinzel',serif;font-size:13px;letter-spacing:1px;color:var(--gold);text-transform:uppercase}
.comic-card .comic-count{font-size:12px;color:var(--cream-dim);margin-top:2px;font-style:italic}
"""

READER_CSS = """
header .page-count{font-size:11px;color:var(--gold-dim);letter-spacing:1px;margin-top:4px}
main{padding:16px;max-width:720px;margin:0 auto;display:flex;flex-direction:column;gap:10px}
main img{display:block;width:100%;height:auto;border-radius:3px;border:1px solid var(--border)}
.reader-nav{display:flex;justify-content:space-between;gap:10px;margin-top:14px;padding-top:14px;border-top:1px solid var(--border)}
.reader-nav a,.reader-nav span{flex:1;text-align:center;padding:10px 12px;border:1px solid var(--border);border-radius:4px;font-family:'Cinzel',serif;font-size:11px;letter-spacing:1px;text-transform:uppercase;text-decoration:none;color:var(--cream-dim);transition:all .15s}
.reader-nav a:hover{border-color:var(--gold-dim);color:var(--gold)}
.reader-nav span{opacity:.35}
.reader-nav a.gallery-link{color:var(--gold)}
"""


def title_for(num: str) -> str:
    return f"Sesión {num}"


def discover_episodes():
    episodes = []
    for d in sorted(PAGES_DIR.iterdir()):
        if not d.is_dir():
            continue
        cover = d / "cover.png"
        if not cover.exists():
            continue
        pages = sorted(
            (p for p in d.iterdir() if re.match(r"p\d+\.png$", p.name)),
            key=lambda p: p.name,
        )
        episodes.append({"num": d.name, "cover": cover, "pages": pages})
    return episodes


def build_gallery(episodes):
    cards = []
    for ep in episodes:
        num = ep["num"]
        cards.append(f"""      <a class="comic-card" href="{num}.html">
        <img src="comics_pages/{num}/cover.png" alt="Portada {title_for(num)}" loading="lazy">
        <div class="comic-label">
          <div class="comic-title">{title_for(num)}</div>
          <div class="comic-count">{len(ep['pages'])} páginas</div>
        </div>
      </a>""")
    cards_html = "\n".join(cards)
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Zskahra — Cómics</title>
{FONTS}
<style>{BASE_CSS}{GALLERY_CSS}</style>
</head>
<body>
<a href="../index.html" class="back-link">&larr; Volver</a>
<header>
  <h1>Zskahra</h1>
  <p>Cómics de la campaña</p>
</header>
<main>
  <div class="comic-grid">
{cards_html}
  </div>
</main>
</body>
</html>
"""
    (ROOT / "index.html").write_text(html)


def build_reader(episodes, i):
    ep = episodes[i]
    num = ep["num"]
    prev_ep = episodes[i - 1] if i > 0 else None
    next_ep = episodes[i + 1] if i < len(episodes) - 1 else None

    images = [f'comics_pages/{num}/cover.png']
    images += [f'comics_pages/{num}/{p.name}' for p in ep["pages"]]
    imgs_html = "\n".join(
        f'  <img src="{src}" alt="{title_for(num)} — página {n}" loading="lazy" decoding="async">'
        for n, src in enumerate(images)
    )

    prev_link = (
        f'<a href="{prev_ep["num"]}.html">&larr; {title_for(prev_ep["num"])}</a>'
        if prev_ep else '<span>&larr; Sesión anterior</span>'
    )
    next_link = (
        f'<a href="{next_ep["num"]}.html">{title_for(next_ep["num"])} &rarr;</a>'
        if next_ep else '<span>Sesión siguiente &rarr;</span>'
    )

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Zskahra — {title_for(num)}</title>
{FONTS}
<style>{BASE_CSS}{READER_CSS}</style>
</head>
<body>
<a href="index.html" class="back-link">&larr; Cómics</a>
<header>
  <h1>{title_for(num)}</h1>
  <p class="page-count">{len(images)} páginas</p>
</header>
<main>
{imgs_html}
  <nav class="reader-nav">
    {prev_link}
    <a class="gallery-link" href="index.html">Índice</a>
    {next_link}
  </nav>
</main>
</body>
</html>
"""
    (ROOT / f"{num}.html").write_text(html)


def main():
    episodes = discover_episodes()
    if not episodes:
        raise SystemExit("No se encontraron episodios en comics_pages/")
    build_gallery(episodes)
    for i in range(len(episodes)):
        build_reader(episodes, i)
    print(f"Generados: index.html + {', '.join(e['num'] + '.html' for e in episodes)}")


if __name__ == "__main__":
    main()
