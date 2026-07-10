# -*- coding: utf-8 -*-
"""Session 4 additions: Irheld + Alvior NPC sheets and the krethar-leader plate.

All NEW designs — generated from text + clear-line anchor (+ skin scale for the
NPCs, + canon Krethar plate for the leader), and they REQUIRE Pedro's approval
before any page is generated.

Decisions from Pedro 2026-07-09 (see sesion-04 SCRIPT.md):
- The commander is lettered IRHELD (root Ir + -held; the friend's comic wrote
  "Ir-Held" — hyphenated names don't exist in canon).
- "Mirabella" = MIRAVELAR and "Ulvior" = ULBIOR — both only mentioned, no sheet.
- The veteran does not exist; no sheet.

[INFERRED, pending approval]: Irheld's skin scale 3 and age; Alvior's skin
scale 2 and age; the leader's exact crystal-spike silhouette.

Usage:
    set -a && . ./.env && set +a && .venv/bin/python personajes/build_sheets_s04.py [names...] [--force]
Names: irheld alvior leader (default: all)
"""

import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from build_sheets_clearline import (ANCHOR, SCALE, SHEET, SCALE_NOTE, STYLE_NOTE,
                                    TEXT_RULE, gen, load_env)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
KRETHAR = ROOT / "world_info" / "reference_images" / "beasts" / "Krethar.png"

NPCS = {
    "irheld": {
        "step": 3, "label": "IRHELD",
        "desc": (
            "IRHELD — commander of a trade caravan; his -held suffix means he "
            "answers for the caravan's protective pylon. An aldeano man in his "
            "mid-forties: TALL (1.98 m), THIN, elongated, light-boned, upright "
            "and composed — the still center of any crowd. Dark hair worn in a "
            "single neat BRAID down his back, a lean weathered face, calm level "
            "eyes, clean-shaven. Lighter travel robes than the people around "
            "him: pale layered wrapped cloth, road-worn but kept, a wide belt "
            "with bronze fittings and small crystal-tending tools (picks, soft "
            "brushes, wrapped shims), knotted route-charms, strap sandals. NO "
            "weapons, NO books, NO scrolls, NO writing, NO hood."
        ),
    },
    "alvior": {
        "step": 2, "label": "ALVIOR",
        "desc": (
            "ALVIOR — the elected representative of a trade caravan's families "
            "and cargo (root Alv + the traveler suffix -ior). An OLD aldeano "
            "man in his late sixties: TALL (2.02 m), THIN, elongated and "
            "light-boned, a little bowed at the shoulders but grave and "
            "deliberate. LONG WHITE hair swept back and a FULL WHITE BEARD — "
            "the loudest trait, identical in all three views. Deep-lined face, "
            "shrewd heavy-browed eyes. Layered muted travel robes with a heavy "
            "woven half-cloak over one shoulder, a wide belt hung with knotted "
            "cords of past journeys and small bronze charms, strap sandals, a "
            "plain wooden walking staff. NO weapons, NO books, NO scrolls, NO "
            "writing."
        ),
    },
}

LEADER_PROMPT = (
    "This is an ANIMAL REFERENCE PLATE: the SAME single creature drawn TWICE on "
    "a plain pale background with no scenery — LEFT: full side view, RIGHT: "
    "three-quarter front view. THE KRETHAR LEADER, an alpha Chaos predator: "
    "take the BASE ANATOMY exactly from the attached krethar beast plate (a "
    "lean, ferocious quadruped reptile with a spined ridge) but REDRAW it in "
    "the clear-line style of the first image, and make it the ALPHA of its "
    "kind: visibly TWICE the bulk of a common krethar, heavier neck and "
    "shoulders, and instead of the commons' low pale crystal clusters its back "
    "and tail BRISTLE with TALL DARK CRYSTAL SPIKES, like a hedge of obsidian "
    "shards, with thin VIOLET LIGHTNING crackling between the spike tips, and "
    "a faint violet glow pulsing behind its ribs. It is an animal on four "
    "legs: never upright, never holding anything, NO wings. One coherent "
    "hand-drawn medium, NOT a photograph. "
    'The ONLY text on the plate is "KRETHAR LEADER" hand-lettered small, '
    "centered at the bottom. NO other words, glyphs, numbers or watermarks. "
)


def build_npc(name, force=False):
    cfg = NPCS[name]
    out = HERE / name / "sheet-clearline.png"
    if out.exists() and not force:
        print(f"skip {name} (exists)")
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    prompt = (STYLE_NOTE + SHEET + cfg["desc"] + " "
              + SCALE_NOTE.format(step=cfg["step"])
              + TEXT_RULE.format(name=cfg["label"]))
    t0 = time.time()
    gen(prompt, [ANCHOR, SCALE], out)
    print(f"done {name} in {time.time() - t0:.0f}s -> {out}")


def build_leader(force=False):
    out = (ROOT / "world_info" / "reference_images" / "beasts"
           / "Krethar-leader-clearline.png")
    if out.exists() and not force:
        print("skip leader (exists)")
        return
    t0 = time.time()
    gen(STYLE_NOTE + LEADER_PROMPT, [ANCHOR, KRETHAR], out, size="1536x1024")
    print(f"done leader in {time.time() - t0:.0f}s -> {out}")


def main():
    load_env()
    args = [a for a in sys.argv[1:] if a != "--force"]
    force = "--force" in sys.argv[1:]
    names = args or (list(NPCS) + ["leader"])
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {}
        for n in names:
            if n == "leader":
                futures[pool.submit(build_leader, force)] = n
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
