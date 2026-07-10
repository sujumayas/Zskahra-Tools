#!/usr/bin/env python3
"""Genera personajes/index.html (galería) y personajes/<nombre>.html (ficha) a
partir de las carpetas de personajes. Volver a correr cada vez que se agregue
un personaje nuevo o se apruebe una lámina.

Solo se publica información "player-safe": lo que un personaje del mundo vería
a simple vista (villa, oficio, apariencia). Los INFO.md internos tienen datos
de GM (raza real de los mellizos, alineación IC, etc.) que NUNCA deben
copiarse a este sitio — ver personajes/README.md, "regla suprema 2".

Uso: python3 build_site.py
"""
from pathlib import Path

ROOT = Path(__file__).parent

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
main{padding:20px 16px 40px;max-width:1000px;margin:0 auto}
.section-title{font-family:'Cinzel',serif;font-size:12px;letter-spacing:2px;color:var(--gold-dim);text-transform:uppercase;margin:24px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--border)}
.section-title:first-child{margin-top:0}
.char-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
@media (max-width:820px){.char-grid{grid-template-columns:repeat(3,1fr)}}
@media (max-width:600px){.char-grid{grid-template-columns:repeat(2,1fr)}}
.char-card{display:block;text-decoration:none;color:inherit;border:1px solid var(--border);border-radius:6px;overflow:hidden;background:var(--surface2);transition:border-color .15s,transform .1s}
.char-card:hover{border-color:var(--gold-dim);transform:translateY(-2px)}
.char-card img{display:block;width:100%;aspect-ratio:3/2;object-fit:cover;object-position:top;background:var(--bg)}
.char-card .char-label{padding:10px 10px 12px}
.char-card .char-name{font-family:'Cinzel',serif;font-size:13px;letter-spacing:1px;color:var(--gold);text-transform:uppercase}
.char-card .char-sub{font-size:12px;color:var(--cream-dim);margin-top:2px;font-style:italic}
"""

DETAIL_CSS = """
main{padding:16px;max-width:760px;margin:0 auto}
.detail-hero{width:100%;border-radius:4px;border:1px solid var(--border);margin-bottom:16px}
.detail-meta{display:flex;flex-wrap:wrap;gap:8px 20px;margin-bottom:14px}
.detail-meta div{font-size:13px}
.detail-meta span{display:block;font-family:'Cinzel',serif;font-size:10px;letter-spacing:1px;color:var(--gold-dim);text-transform:uppercase;margin-bottom:2px}
.detail-blurb{font-size:16px;color:var(--cream);margin-bottom:20px;font-style:italic}
.detail-extra{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:6px}
.detail-extra figure{margin:0}
.detail-extra img{width:100%;border-radius:4px;border:1px solid var(--border);display:block}
.detail-extra figcaption{font-size:11px;color:var(--cream-dim);text-align:center;margin-top:4px;font-family:'Cinzel',serif;letter-spacing:1px;text-transform:uppercase}
"""

# Datos "player-safe" curados a mano a partir de INFO.md, sin ningún dato de
# GM (raza real de los mellizos, IC, alineación, secretos de origen, etc.).
PJS = {
    "zal": {
        "name": "Zal",
        "villa": "Logven",
        "oficio": "Aprendiz de sanadora (-ion)",
        "blurb": "Trenza gruesa con una ramita de hierbas siempre sujeta, cinturón con "
                 "bolsas de hierbas y un pequeño mortero. Lleva un amuleto de piedra "
                 "oscura al cuello que nunca se quita.",
    },
    "vala": {
        "name": "Vala",
        "villa": "Logven",
        "oficio": "Aprendiz de vidente (-oth)",
        "blurb": "Mellizo de Zal. Porte calmo y contemplativo, cordones de fichas y "
                 "amuletos de sueño al cinto. Lleva un amuleto de piedra oscura idéntico "
                 "al de su hermana, siempre visible.",
    },
    "kelx": {
        "name": "Kelx",
        "villa": "Litor",
        "oficio": "Aprendiz de técnico de pilones (-held)",
        "blurb": "Pelo rubio arena recogido en alto. Arnés y cinturón de herramientas "
                 "de bronce: punzones, ganchos y repuestos para el afinado de pilones.",
    },
    "axthen": {
        "name": "Axthen",
        "villa": "Logven",
        "oficio": "Aprendiz de archivista (-sar)",
        "blurb": "Pelo oscuro largo y rizado, recogido a media altura. Lleva siempre "
                 "velkrai — cuerdas anudadas con cuentas de hueso y bronce — su "
                 "herramienta de oficio como archivista.",
    },
    "dur": {
        "name": "Dur",
        "villa": "Theriv",
        "oficio": "Aprendiz de cazador (-dren/-mork)",
        "blurb": "Bronceado por la vida de frontera, pelo oscuro revuelto. Lanza corta "
                 "en mano y un par de jabalinas a la espalda.",
    },
}

NPCS = {
    "vimsar": {
        "name": "Vimsar",
        "villa": "Logven",
        "oficio": "Archivista jefe (NPC)",
        "blurb": "Anciana dedicada de por vida al archivo de Logven. Poca paciencia con "
                 "preguntas ociosas, enorme con las sinceras. Velkrai al cinto y "
                 "cruzados al pecho como una banda.",
    },
}

# Personajes de los que solo tenemos la lámina de modelo, sin ficha escrita.
OTHERS_NO_INFO = ["alvior", "arnsar", "irheld", "pelvskar", "rimtav", "ulbior"]


def hero_image(folder: Path) -> str:
    for name in ("sheet-clearline.png",):
        if (folder / name).exists():
            return name
    raise SystemExit(f"{folder} no tiene sheet-clearline.png")


def extra_images(folder: Path, hero: str):
    candidates = ["turnaround.png", "plate.png", "accion-sanadora.png"]
    return [c for c in candidates if c != hero and (folder / c).exists()]


def build_card(slug: str, data: dict) -> str:
    return f"""      <a class="char-card" href="{slug}.html">
        <img src="{slug}/sheet-clearline.png" alt="{data['name']}" loading="lazy">
        <div class="char-label">
          <div class="char-name">{data['name']}</div>
          <div class="char-sub">{data['villa']} &middot; {data['oficio']}</div>
        </div>
      </a>"""


def build_card_plain(slug: str) -> str:
    name = slug.capitalize()
    return f"""      <a class="char-card" href="{slug}.html">
        <img src="{slug}/sheet-clearline.png" alt="{name}" loading="lazy">
        <div class="char-label">
          <div class="char-name">{name}</div>
          <div class="char-sub">Personaje del cómic</div>
        </div>
      </a>"""


def build_gallery():
    pj_cards = "\n".join(build_card(slug, data) for slug, data in PJS.items())
    npc_cards = "\n".join(build_card(slug, data) for slug, data in NPCS.items())
    other_cards = "\n".join(build_card_plain(slug) for slug in OTHERS_NO_INFO)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Zskahra — Personajes</title>
{FONTS}
<style>{BASE_CSS}{GALLERY_CSS}</style>
</head>
<body>
<a href="../index.html" class="back-link">&larr; Cómics</a>
<header>
  <h1>Zskahra</h1>
  <p>Personajes del cómic</p>
</header>
<main>
  <p class="section-title">Personajes jugadores</p>
  <div class="char-grid">
{pj_cards}
  </div>

  <p class="section-title">Otros personajes</p>
  <div class="char-grid">
{npc_cards}
{other_cards}
  </div>
</main>
</body>
</html>
"""
    (ROOT / "index.html").write_text(html)


def build_detail(slug: str, data: dict | None):
    folder = ROOT / slug
    hero = hero_image(folder)
    extras = extra_images(folder, hero)
    name = data["name"] if data else slug.capitalize()

    meta_html = ""
    blurb_html = ""
    if data:
        meta_html = f"""  <div class="detail-meta">
    <div><span>Villa</span>{data['villa']}</div>
    <div><span>Oficio</span>{data['oficio']}</div>
  </div>"""
        blurb_html = f'  <p class="detail-blurb">{data["blurb"]}</p>'

    extras_html = ""
    if extras:
        figs = "\n".join(
            f'    <figure><img src="{slug}/{e}" alt="{name} — {e.split(".")[0]}" loading="lazy"><figcaption>{e.split(".")[0].replace("-", " ")}</figcaption></figure>'
            for e in extras
        )
        extras_html = f'  <div class="detail-extra">\n{figs}\n  </div>'

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Zskahra — {name}</title>
{FONTS}
<style>{BASE_CSS}{DETAIL_CSS}</style>
</head>
<body>
<a href="index.html" class="back-link">&larr; Personajes</a>
<header>
  <h1>{name}</h1>
</header>
<main>
  <img class="detail-hero" src="{slug}/{hero}" alt="{name}">
{meta_html}
{blurb_html}
{extras_html}
</main>
</body>
</html>
"""
    (ROOT / f"{slug}.html").write_text(html)


def main():
    build_gallery()
    for slug, data in PJS.items():
        build_detail(slug, data)
    for slug, data in NPCS.items():
        build_detail(slug, data)
    for slug in OTHERS_NO_INFO:
        build_detail(slug, None)
    print("Generados: index.html + fichas de personajes")


if __name__ == "__main__":
    main()
