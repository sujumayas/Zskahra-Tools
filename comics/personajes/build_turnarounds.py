# -*- coding: utf-8 -*-
"""Turnaround model sheets for the five PCs (Zal, Vala, Kelx, Axthen, Dur).

One 3:2 sheet per character: full body, THREE views (front / three-quarter /
back), etched sepia ink-on-parchment style locked to each character's plate
crop in personajes/<name>/plate.png. Skin tone pinned to the numbered scale
in world_info/reference_images/skin-color-scale.png.

Engine: OpenAI gpt-image-2 images/edits (proven pattern from rosas/build.py).

Usage:
    set -a && . ./.env && set +a && .venv/bin/python personajes/build_turnarounds.py [names...] [--force]

Output: personajes/<name>/turnaround.png (skipped if present; --force to redo)
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


def gen(prompt, refs, out):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not set")
    fields = [("model", "gpt-image-2"), ("prompt", prompt),
              ("size", "1536x1024"), ("quality", "high"), ("n", "1")]
    ctype, body = _multipart(fields, [("image[]", p) for p in refs])
    img = _post("https://api.openai.com/v1/images/edits",
                {"Content-Type": ctype, "Authorization": f"Bearer {key}"}, body)
    out.write_bytes(img)


# ------------------------------------------------------------------ prompts

STYLE = (
    "Render EXACTLY in the style of the FIRST attached reference plate: fine etched "
    "sepia INK linework on warm aged parchment, dense crosshatching and stippling, "
    "medieval-naturalist illustrated plate. Hand-drawn etching only — NOT a photograph, "
    "NOT digital painting. Use the reference plate ONLY for its rendering style and for "
    "this character's face, hair, clothing and gear design — NEVER copy its composition, "
    "background scenery, card frame, titles or glyphs. "
)

SHEET = (
    "This is a CHARACTER MODEL SHEET (turnaround): the SAME single character drawn "
    "THREE times side by side at identical scale on a plain aged-parchment background "
    "with no scenery — LEFT: front view, CENTER: three-quarter view, RIGHT: back view. "
    "Full body head to feet, natural standing pose, all clothing and gear identical in "
    "the three views. "
)

SCALE_NOTE = (
    "The LAST attached image is a NUMBERED SKIN-TONE SCALE drawn in the same parchment "
    "style: match this character's skin tone EXACTLY to step {step} of that scale, "
    "identical in all three views. Do NOT draw the scale itself on the sheet. "
)

TEXT_RULE = (
    'The ONLY text on the sheet is the name "{name}" hand-lettered small, centered '
    "under the figures. NO other words, NO titles, NO flavor text, NO glyphs, NO "
    "numbers, NO watermarks, NO written language anywhere else. "
)

CHARS = {
    "zal": {
        "step": 6,
        "label": "ZAL",
        "extra_refs": ["accion-sanadora.png"],
        "desc": (
            "ZAL, a young woman of about 17, apprentice healer. The second attached "
            "image shows her in action — same woman. Skin tone markedly darker than "
            "any pale villager (step 6). COMPACT and DENSE: 1.64 m, short and "
            "powerfully built, heavy solid muscle, broad through the shoulders and "
            "hips — NOT tall, NOT slender, NOT willowy. Abundant dark curly hair in "
            "a thick braid with a sprig of herbs tucked into it, loose strands. Pale "
            "layered wrapped cloth garments with frayed hems, strap sandals, belt hung "
            "with herb pouches, dried herb bundles and a small mortar. A SMALL DARK "
            "STONE AMULET on a cord at her neck, clearly visible in front and "
            "three-quarter views. NO skin markings, NO tattoos, NO weapons."
        ),
    },
    "vala": {
        "step": 4,
        "label": "VALA",
        "extra_refs": [],
        "desc": (
            "VALA, a young man of about 17, apprentice seer. Skin noticeably darker "
            "than a deeply tanned pale villager (step 4) — yet clearly LIGHTER than "
            "his twin sister at step 6. COMPACT and DENSE: 1.77 m, broad-shouldered "
            "and heavyset (101 kg), thick solid muscle mass, a heavy grounded frame — "
            "NOT tall, NOT slender, NOT long-limbed. A quiet contained presence. Short "
            "dark curly hair. Calm contemplative expression. Pale layered robes with "
            "bronze-and-bone chain ornaments, strap sandals, seer's cords of knotted "
            "charms and small bone tokens hanging at his belt. A SMALL DARK STONE "
            "AMULET on a cord at his neck, clearly visible in front and three-quarter "
            "views. NO skin markings, NO book, NO scroll, NO weapons."
        ),
    },
    "kelx": {
        "step": 2,
        "label": "KELX",
        "extra_refs": [],
        "desc": (
            "KELX, a young man of about 17, apprentice artifact engineer and pylon "
            "technician from a stone-carving village. Villager skin at step 2 — the "
            "faint deeper cast of an apprentice who already handles artifacts daily. "
            "Tall (1.93 m), slender long-limbed low-gravity build, strong forearms of "
            "a stoneworker's apprentice. Sandy-blond wavy hair tied up. Short layered "
            "work garments of woven cloth and hide with frayed hems, strap sandals, "
            "leather wrist wraps, a tool harness and belt heavy with bronze fittings: "
            "awls, hooks, cords, crystal spares, small tuning tools. Focused quiet "
            "expression. NO industrial or modern metal, NO weapons."
        ),
    },
    "axthen": {
        "step": 2,
        "label": "AXTHEN",
        "extra_refs": [],
        "desc": (
            "AXTHEN, a young man of about 17, apprentice record-keeper of an archive "
            "village. Villager skin at step 2, sheltered indoor life. Very tall "
            "(1.95 m), slender willowy long-limbed low-gravity build, fine precise "
            "hands. Long dark curly hair gathered half-up with loose strands. Layered "
            "flowing pale robes with wide sleeves, strap sandals, simple bone-bead "
            "necklace. His signature tool: VELKRAI — strands of knotted memory-cords "
            "with bone and bronze beads hanging from his belt and wound around one "
            "wrist. NO books, NO scrolls, NO writing, NO weapons."
        ),
    },
    "dur": {
        "step": 2,
        "label": "DUR",
        "extra_refs": [],
        "desc": (
            "DUR, a young man of about 17, apprentice hunter from a jungle frontier "
            "village. Villager skin at step 2 with a visible sun-tan of outdoor work — "
            "weathered but still clearly of the pale lineage. Tall (1.92 m), lean wiry "
            "athletic low-gravity build. Dark unruly curly hair, half tied back. Alert "
            "observant expression. Ragged hide-and-woven-cloth kilt, crossed chest "
            "strap over bare torso, strap sandals, leather wrist wraps, a hunting "
            "pouch and small bone charm at his belt. He carries a SHORT SPEAR in one "
            "hand and TWO JAVELINS slung across his back — same weapons in all three "
            "views. NO metal armor, NO other weapons."
        ),
    },
}


def build(name, force=False):
    cfg = CHARS[name]
    out = HERE / name / "turnaround.png"
    if out.exists() and not force:
        print(f"skip {name} (exists)")
        return
    refs = [HERE / name / "plate.png"]
    refs += [HERE / name / r for r in cfg["extra_refs"]]
    refs.append(SCALE)
    prompt = (
        STYLE + SHEET + cfg["desc"] + " "
        + SCALE_NOTE.format(step=cfg["step"])
        + TEXT_RULE.format(name=cfg["label"])
    )
    t0 = time.time()
    gen(prompt, refs, out)
    print(f"done {name} in {time.time() - t0:.0f}s -> {out}")


def main():
    load_env()
    args = [a for a in sys.argv[1:] if a != "--force"]
    force = "--force" in sys.argv[1:]
    names = args or list(CHARS)
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(build, n, force): n for n in names}
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
