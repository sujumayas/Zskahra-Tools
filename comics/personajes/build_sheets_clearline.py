# -*- coding: utf-8 -*-
"""Clear-line pipeline: wordless style anchor + in-style character model sheets.

Style DECIDED by Pedro 2026-07-08: clear-line (ligne claire) science-fantasy
(winning test: sesion-01-un-velkrai-irregular/style_tests/style5-clearline-scifantasy.png).

Step 1 — style anchor (text-only, wordless, no characters):
    world_info/reference_images/style/style-anchor-clearline.png
Step 2 — per-character model sheets (3-view turnaround) in the new style,
    design locked to the APPROVED parchment turnarounds:
    personajes/<name>/sheet-clearline.png
    Refs per call: anchor FIRST, then approved turnaround.png (design), then
    the numbered skin-tone scale LAST.
    VIMSAR has no prior design — she is generated from text + anchor + scale.

Test-page corrections baked in (Pedro): Vala DENSE never fat; the three
aldeanos tall/thin/elongated; only Kelx sandy-blond.

Usage:
    set -a && . ./.env && set +a && .venv/bin/python personajes/build_sheets_clearline.py [names...] [--force]
"""

import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCALE = ROOT / "world_info" / "reference_images" / "skin-color-scale.png"
ANCHOR = ROOT / "world_info" / "reference_images" / "style" / "style-anchor-clearline.png"
WORKERS = 3

# ------------------------------------------------------------------ engine


def load_env():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k, v)


def _multipart(fields, files):
    boundary = uuid.uuid4().hex
    body = []
    for name, value in fields:
        body.append(f"--{boundary}\r\n".encode())
        body.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        body.append(f"{value}\r\n".encode())
    for name, path in files:
        mime = mimetypes.guess_type(str(path))[0] or "image/png"
        body.append(f"--{boundary}\r\n".encode())
        body.append(
            f'Content-Disposition: form-data; name="{name}"; filename="{path.name}"\r\n'
            f"Content-Type: {mime}\r\n\r\n".encode()
        )
        body.append(path.read_bytes())
        body.append(b"\r\n")
    body.append(f"--{boundary}--\r\n".encode())
    return f"multipart/form-data; boundary={boundary}", b"".join(body)


def _post(url, headers, data):
    last = ""
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=600) as resp:
                payload = json.load(resp)
            b64 = payload["data"][0].get("b64_json")
            if b64:
                return base64.b64decode(b64)
            last = json.dumps(payload)[:500]
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read().decode()[:500]}"
            if e.code in (429, 500, 503):
                time.sleep(15 * (attempt + 1))
                continue
        except Exception as e:  # noqa: BLE001
            last = str(e)
        time.sleep(5)
    raise RuntimeError(last)


def gen(prompt, refs, out, size="1536x1024"):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not set")
    if refs:
        fields = [("model", "gpt-image-2"), ("prompt", prompt),
                  ("size", size), ("quality", "high"), ("n", "1")]
        ctype, body = _multipart(fields, [("image[]", p) for p in refs])
        img = _post("https://api.openai.com/v1/images/edits",
                    {"Content-Type": ctype, "Authorization": f"Bearer {key}"}, body)
    else:
        body = json.dumps({"model": "gpt-image-2", "prompt": prompt,
                           "size": size, "quality": "high", "n": 1}).encode()
        img = _post("https://api.openai.com/v1/images/generations",
                    {"Content-Type": "application/json",
                     "Authorization": f"Bearer {key}"}, body)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(img)


# ------------------------------------------------------------------ prompts

CLEARLINE = (
    "fine even CLEAR-LINE (ligne claire) science-fantasy style: uniform elegant ink "
    "contours of constant weight, airy flat colors in pale dusty pastels, subtle "
    "single-tone shadows, Moebius-flavored calm — one coherent hand-drawn medium, "
    "NOT a photograph, NOT painterly, NO gradients, NO digital gloss"
)

ANCHOR_PROMPT = (
    f"A wordless landscape plate rendered in {CLEARLINE}. "
    "An alien moon's open scrubland: a pale winding dirt road through dusty "
    "olive-and-ochre brush and strange succulent plants, distant eroded rock spires. "
    "In the sky: TWO small suns close to each other, and THLASK — one enormous dead "
    "planet fixed high in the sky: a MASSIVE, completely SOLID rocky sphere, its "
    "surface veined with deep dark cracks and canyon-like fault lines, like a "
    "shattered stone ball that still holds together. The sphere is FULL and OPAQUE "
    "edge to edge — NOT hollow, NOT an eggshell, NO missing chunks, NO sky visible "
    "through it. Soft distributed daylight. "
    "ABSOLUTELY NO text, NO letters, NO signature, NO watermark, NO people, NO "
    "animals, NO buildings. Pure landscape reference plate."
)

STYLE_NOTE = (
    "Render EXACTLY in the style of the FIRST attached reference image: {cl}. Use "
    "the first image ONLY for rendering style — never copy its composition or "
    "subjects. ".format(cl=CLEARLINE)
)

DESIGN_NOTE = (
    "The SECOND attached image is this character's APPROVED DESIGN turnaround "
    "(drawn in an older etched style): keep the SAME face, hair, body proportions, "
    "clothing and gear EXACTLY, but redraw everything in the clear-line style of "
    "the first image. "
)

SHEET = (
    "This is a CHARACTER MODEL SHEET (turnaround): the SAME single character drawn "
    "THREE times side by side at identical scale on a plain pale background with no "
    "scenery — LEFT: front view, CENTER: three-quarter view, RIGHT: back view. Full "
    "body head to feet, natural standing pose, identical clothing and gear in all "
    "three views. "
)

SCALE_NOTE = (
    "The LAST attached image is a NUMBERED SKIN-TONE SCALE: match this character's "
    "skin tone EXACTLY to step {step} of that scale, identical in all three views, "
    "rendered as a flat clear-line color. Do NOT draw the scale itself. "
)

TEXT_RULE = (
    'The ONLY text on the sheet is the name "{name}" hand-lettered small, centered '
    "under the figures. NO other words, glyphs, numbers or watermarks. "
)

CHARS = {
    "zal": {
        "step": 6, "label": "ZAL",
        "desc": (
            "ZAL, young woman of about 17. Compact (1.64 m) and powerfully DENSE — "
            "heavy solid muscle, broad shoulders and hips, NOT fat. Markedly darker "
            "than any pale villager. Thick dark braid with a sprig of herbs, loose "
            "curls. Pale layered wrapped garments, frayed hems, strap sandals, herb "
            "pouches and a small mortar at her belt, small dark stone amulet on a "
            "cord at her neck. NO skin markings, NO weapons."
        ),
    },
    "vala": {
        "step": 4, "label": "VALA",
        "desc": (
            "VALA, young man of about 17. Compact (1.77 m) and powerfully DENSE — "
            "barrel chest, thick neck, wide shoulders, heavy solid muscle and bone, "
            "absolutely NOT fat, NO belly. Noticeably darker than a tanned villager "
            "yet lighter than his twin sister. Short dark curls, calm face. Pale "
            "layered robes with bronze-and-bone chain ornaments, seer's cords of "
            "knotted charms at his belt, small dark stone amulet on a cord at his "
            "neck. NO skin markings, NO book, NO weapons."
        ),
    },
    "kelx": {
        "step": 2, "label": "KELX",
        "desc": (
            "KELX, young man of about 17, VERY TALL (1.93 m), THIN and ELONGATED — "
            "long light limbs, slender low-gravity build, strong forearms. "
            "SANDY-BLOND wavy hair tied up. Short layered work garments of woven "
            "cloth and hide, strap sandals, leather wrist wraps, tool harness and "
            "belt with bronze fittings, awls, hooks, cords and crystal spares. NO "
            "industrial metal, NO weapons."
        ),
    },
    "axthen": {
        "step": 2, "label": "AXTHEN",
        "desc": (
            "AXTHEN, young man of about 17, VERY TALL (1.95 m), THIN, willowy and "
            "ELONGATED — the lightest silhouette of the cast. LONG DARK CURLY hair "
            "gathered half-up, NOT blond. Layered flowing pale robes with wide "
            "sleeves, strap sandals, bone-bead necklace, velkrai knotted memory-"
            "cords with bone and bronze beads at his belt and wound on one wrist. "
            "NO books, NO writing, NO weapons."
        ),
    },
    "dur": {
        "step": 2, "label": "DUR",
        "desc": (
            "DUR, young man of about 17, VERY TALL (1.92 m), THIN, wiry and "
            "ELONGATED — lean athletic low-gravity build. DARK unruly curly hair "
            "half tied back, NOT blond, visible sun-tan of frontier work. Ragged "
            "hide-and-woven-cloth kilt, crossed chest strap over bare torso, strap "
            "sandals, leather wrist wraps, hunting pouch and small bone charm. "
            "Carries a SHORT SPEAR in one hand and TWO JAVELINS slung across his "
            "back, identical in all three views. NO metal armor."
        ),
    },
    "vimsar": {
        "step": 1, "label": "VIMSAR",
        "no_design": True,
        "desc": (
            "VIMSAR, an OLD woman, chief archivist of a stone archive village — "
            "design is NEW, in style. An aldeana: TALL (1.80 m), THIN, elongated "
            "light build, now aged — straight-backed, austere, deeply lined face, "
            "sharp patient eyes, white hair pulled severely back. Palest villager "
            "skin. Long layered robes in muted archive tones, strap sandals, and "
            "her office everywhere: many strands of velkrai knotted cords with bone "
            "and bronze beads hanging from her belt and looped across her chest "
            "like a sash. NO books, NO scrolls, NO writing, NO weapons."
        ),
    },
}


def build_anchor(force=False):
    if ANCHOR.exists() and not force:
        print("skip anchor (exists)")
        return
    t0 = time.time()
    gen(ANCHOR_PROMPT, [], ANCHOR, size="1536x1024")
    print(f"done anchor in {time.time() - t0:.0f}s -> {ANCHOR}")


def build_sheet(name, force=False):
    cfg = CHARS[name]
    out = HERE / name / "sheet-clearline.png"
    if out.exists() and not force:
        print(f"skip {name} (exists)")
        return
    refs = [ANCHOR]
    prompt = STYLE_NOTE
    if not cfg.get("no_design"):
        refs.append(HERE / name / "turnaround.png")
        prompt += DESIGN_NOTE
    refs.append(SCALE)
    prompt += (SHEET + cfg["desc"] + " " + SCALE_NOTE.format(step=cfg["step"])
               + TEXT_RULE.format(name=cfg["label"]))
    t0 = time.time()
    gen(prompt, refs, out)
    print(f"done {name} in {time.time() - t0:.0f}s -> {out}")


def main():
    load_env()
    args = [a for a in sys.argv[1:] if a != "--force"]
    force = "--force" in sys.argv[1:]
    build_anchor(force=False)
    names = args or list(CHARS)
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(build_sheet, n, force): n for n in names}
        failed = []
        for fut, n in futures.items():
            try:
                fut.result()
            except Exception as e:  # noqa: BLE001
                failed.append((n, str(e)[:300]))
        for n, err in failed:
            print(f"FAILED {n}: {err}")
        if failed:
            sys.exit(1)


if __name__ == "__main__":
    main()
