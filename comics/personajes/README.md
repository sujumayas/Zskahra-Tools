# Personajes jugadores

Una carpeta por PJ con su ficha visual canónica (`INFO.md`), su recorte de la lámina
original (`plate.png`) y su turnaround generado (`turnaround.png`, requiere aprobación
de Pedro antes de usarse en páginas — CLAUDE.md, ficha obligatoria).

| PJ | Raza (real) | Villa actual | Oficio (aprendiz de) | Tono (escala) |
|---|---|---|---|---|
| [Zal](zal/INFO.md) | Vhareth — melliza del Caos, IC 7 | Logven | sanadora (-ion) | **6** (canon) |
| [Vala](vala/INFO.md) | Vhareth — mellizo del Orden, IC 4 | Logven | vidente (-oth) | 4  |
| [Kelx](kelx/INFO.md) | aldeano | Litor | ingeniero de artefactos / pilones (-held) | 2  |
| [Axthen](axthen/INFO.md) | aldeano | Logven | archivista (-sar, velkrai) | 2  |
| [Dur](dur/INFO.md) | aldeano | Theriv | cazador (-dren/-mork) | 2 + bronceado  |

Todos ~16–18 años, todos **sin sufijo** todavía (decidido por Pedro 2026-07-08).
Los mellizos pasan por aldeanos huérfanos; su historia real es solo del GM
(`world_info/mellizos_v3.md`) y **jamás se explica en el cómic** (regla suprema 2).

## Decisiones pendientes de Pedro

1. ~~Tonos, alturas y pesos~~ — todos fijados por Pedro 2026-07-08 (tonos: Zal 6, Vala 4,
   Kelx 2, Axthen 2, Dur 2+bronceado). **Decisión de morfología de los mellizos (híbrido):**
   Zal 1.64 m / 78 kg y Vala 1.77 m / 101 kg — más bajos que los aldeanos y muy densos;
   supera a mellizos_v3 §4.1 y al doc de pigmentación en lo que toca a "altos y ligeros".
2. ~~El libro de Vala~~ — resuelto con la aprobación de los turnarounds: Vala lleva
   cordones de vidente, sin libro (canon: solo los Vethkar leen/escriben).
3. ~~Aprobar turnarounds~~ — **los 5 aprobados por Pedro (2026-07-08)**. Son la
   referencia obligatoria de cada página.
4. Discrepancia detectada: CLAUDE.md dice aldeanos H 1.90–2.15 / M 1.80–2.00, pero
   `world_info/zskahra_razas.md` dice H 1.80–1.98 / M 1.72–1.90. Las fichas usan valores
   dentro de la intersección de ambos rangos — decidir cuál manda.

## Regenerar turnarounds

```bash
set -a && . ./.env && set +a && .venv/bin/python personajes/build_turnarounds.py zal vala --force
```
