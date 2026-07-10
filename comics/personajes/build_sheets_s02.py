# -*- coding: utf-8 -*-
"""Session 2/3 additions: NPC model sheets + Siteth vista + pack-beast plate.

All NEW designs (no prior turnarounds) — generated from text + clear-line anchor
+ skin scale, and they REQUIRE Pedro's approval before any page is generated.

Decisions from Pedro 2026-07-09:
- Pelviorskar (canon doc name) is lettered PELVSKAR — docs always add one suffix
  too many; real usage is root + ONE suffix.
- Rimtav: a SHORT aldeano (~1.85 m), no special racial traits.
- Ulbior's cargo: ambiguous wrapped bundles, never identified.

[INFERRED, pending approval]: ages/faces of all four NPCs; Ulbior's stiff RIGHT
leg; the pack beast's whole design; Siteth's architecture (no canon image).

Usage:
    set -a && . ./.env && set +a && .venv/bin/python personajes/build_sheets_s02.py [names...] [--force]
Names: ulbior arnsar pelvskar rimtav bestia siteth (default: all)
"""

import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from build_sheets_clearline import (ANCHOR, SCALE, SHEET, SCALE_NOTE, STYLE_NOTE,
                                    TEXT_RULE, gen, load_env)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

NPCS = {
    "ulbior": {
        "step": 2, "label": "ULBIOR",
        "desc": (
            "ULBIOR of Karven, 'the Errant' — a legendary lone caravanner. An "
            "aldeano man in his late fifties: TALL (1.95 m), THIN, wiry and "
            "elongated, slightly stooped from the road, deeply sun-weathered. His "
            "RIGHT leg is stiff and lame: he stands with all his weight on the "
            "left leg, the right foot trailing — identical in all three views. "
            "Short grizzled grey-brown hair, short rough beard stubble, and the "
            "calm half-smile of a man who is never surprised, lips slightly "
            "pursed as if whistling. Layered road-worn travel garments: faded "
            "wrapped cloth, a blanket-roll across one shoulder, wide belt hung "
            "with MANY small pouches and knotted charms, strap sandals with extra "
            "wrapping, a plain wooden walking staff. NO parchment, NO writing, NO "
            "weapons, NO hood."
        ),
    },
    "arnsar": {
        "step": 1, "label": "ARNSAR",
        "desc": (
            "ARNSAR of Siteth — the -sar who registers the market's entries and "
            "exits. An aldeano man around fifty: TALL (2.00 m), THIN, elongated, "
            "pale, sedentary. Receding dark-grey hair combed back, heavy-lidded "
            "patient eyes, the dry wry face of a man who hears bad questions all "
            "day. Muted layered work robes in archive tones, strap sandals, and "
            "his office on him: strands of velkrai knotted cords with bone and "
            "bronze beads looped at his belt and over one shoulder, a small "
            "bead-counting ring on one finger. NO books, NO scrolls, NO writing, "
            "NO weapons."
        ),
    },
    "pelvskar": {
        "step": 2, "label": "PELVSKAR",
        "desc": (
            "PELVSKAR of Siteth — a retired caravanner who now coordinates the "
            "market's defense; he knows every route. An OLD aldeano man in his "
            "late sixties, ENORMOUS in the aldeano way: at the very top of the "
            "range (2.15 m), TOWERING, but LIGHT-FRAMED like all villagers — "
            "THIN-BONED, rangy, long-limbed, lean and rawboned, knuckly "
            "long-fingered hands, a lined sun-beaten face, short grizzled white "
            "hair and heavy white brows. He imposes by sheer height and "
            "presence, NEVER by mass: NOT bulky, NOT broad, NOT muscular, NO "
            "thick neck. "
            "Old route-worn gear worn like a second skin: a heavy woven "
            "blanket-cloak over one shoulder, a wide scarred leather belt with "
            "route-charms and knotted cords of past journeys, strap sandals, a "
            "plain clay drinking cup hanging from the belt. NO weapons, NO "
            "writing, NO industrial metal."
        ),
    },
    "rimtav": {
        "step": 1, "label": "RIMTAV",
        "desc": (
            "RIMTAV of Siteth — the market judge, incorruptible, arbiter of every "
            "commercial dispute. An aldeano man in his fifties, SHORT for a "
            "villager (1.85 m) though still long-limbed, spare and upright — "
            "direct, practical, contained energy. Close-cropped grey hair, "
            "clean-shaven angular face, level unimpressed eyes. Severely neat "
            "plain robes in dark muted tones, strap sandals, and the tools of his "
            "judgments: short strands of dispute-cords with bronze beads at his "
            "belt, nothing ornamental. NO books, NO scrolls, NO writing, NO "
            "weapons."
        ),
    },
}

BESTIA_PROMPT = (
    "This is an ANIMAL REFERENCE PLATE: the SAME single animal drawn TWICE on a "
    "plain pale background with no scenery — LEFT: full side view, RIGHT: "
    "three-quarter front view. A DOMESTIC PACK BEAST of an alien low-gravity "
    "moon: a placid heavy-bodied draft bovine with unusually LONG legs for its "
    "bulk (lunar proportions), a broad low-slung head with short BLUNT horns, "
    "drooping ears, a shaggy dust-colored coat over grey-tan hide, a short "
    "tufted tail. Calm, patient, harmless — absolutely NO mutations, NO scales, "
    "NO spikes, NO glowing parts. It wears a simple rope harness and a wooden "
    "pack frame loaded with ambiguous wrapped cloth bundles (side view only; "
    "the front view shows the bare harness). It never stands upright, never "
    "holds anything. "
    'The ONLY text on the plate is "PACK BEAST" hand-lettered small, centered at '
    "the bottom. NO other words, glyphs, numbers or watermarks. "
)

SITETH_PROMPT = (
    "A wordless ESTABLISHING VISTA plate of SITETH, the grain village — the "
    "LARGEST village of an alien low-gravity moon (~720 souls), spread over "
    "fertile central plains. Seen from a low rise outside the walls: wide "
    "wheat-and-barley fields, then the village — low sprawling architecture of "
    "pale stone and rough timber: a GRANARY QUARTER of fat round stone granaries "
    "with conical thatch roofs raised on stone footings, a MARKET QUARTER dense "
    "with woven-cloth awnings, carts, tiny crowds and pack animals, and modest "
    "outskirts of seasonal workers' huts. Everything turns around the CENTRAL "
    "PYLON: one tall slender crystalline spire of pale Order-crystal on a stone "
    "base, rising above every roof at the village's hub. In the sky: TWO small "
    "suns at medium separation and THLASK — an enormous dead planet fixed high "
    "in the sky: a MASSIVE SOLID rocky sphere veined with deep dark cracks, "
    "full and opaque edge to edge, NOT hollow. Soft distributed daylight. NO "
    "industrial metal, NO electricity, NO modern glass, NO firearms, NO written "
    "text or signs anywhere. ABSOLUTELY NO text, NO letters, NO signature, NO "
    "watermark on the plate."
)


def build_npc(name, force=False):
    cfg = NPCS[name]
    out = HERE / name / "sheet-clearline.png"
    if out.exists() and not force:
        print(f"skip {name} (exists)")
        return
    prompt = (STYLE_NOTE + SHEET + cfg["desc"] + " "
              + SCALE_NOTE.format(step=cfg["step"])
              + TEXT_RULE.format(name=cfg["label"]))
    t0 = time.time()
    gen(prompt, [ANCHOR, SCALE], out)
    print(f"done {name} in {time.time() - t0:.0f}s -> {out}")


def build_bestia(force=False):
    out = ROOT / "world_info" / "reference_images" / "beasts" / "animal-de-carga.png"
    if out.exists() and not force:
        print("skip bestia (exists)")
        return
    t0 = time.time()
    gen(STYLE_NOTE + BESTIA_PROMPT, [ANCHOR], out, size="1536x1024")
    print(f"done bestia in {time.time() - t0:.0f}s -> {out}")


def build_siteth(force=False):
    out = ROOT / "ciudades" / "siteth.png"
    if out.exists() and not force:
        print("skip siteth (exists)")
        return
    t0 = time.time()
    gen(STYLE_NOTE + SITETH_PROMPT, [ANCHOR], out, size="1536x1024")
    print(f"done siteth in {time.time() - t0:.0f}s -> {out}")


def main():
    load_env()
    args = [a for a in sys.argv[1:] if a != "--force"]
    force = "--force" in sys.argv[1:]
    names = args or (list(NPCS) + ["bestia", "siteth"])
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {}
        for n in names:
            if n == "bestia":
                futures[pool.submit(build_bestia, force)] = n
            elif n == "siteth":
                futures[pool.submit(build_siteth, force)] = n
            else:
                futures[pool.submit(build_npc, n, force)] = n
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
