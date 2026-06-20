// topdown.js — top-down orbital view of the whole system, drawn from above the
// orbital plane and centered on the barycenter. Shows star disks (sized/colored
// by mass), the planet, fading orbit trails, the barycenter, and the
// Holman-Wiegert stability ring.

import { massToColor, rgbStr } from "./insolation.js";

// Map a body's mass to a drawn disk radius (px). Stars use a log-ish scale so a
// dim companion is still visible next to a bright primary.
function starRadiusPx(mass) {
  return 6 + 10 * Math.pow(mass, 0.45);
}

export function drawTopDown(ctx, canvas, state) {
  const { bodies, planet, starA, trails, stability, params } = state;
  const W = canvas.width;
  const H = canvas.height;

  ctx.fillStyle = "#05060d";
  ctx.fillRect(0, 0, W, H);
  drawStarfield(ctx, W, H);

  // --- Auto-scale to fit all bodies plus the stability ring ---
  let maxR = 0.5;
  for (const b of bodies) maxR = Math.max(maxR, Math.hypot(b.pos.x, b.pos.y));
  if (stability) maxR = Math.max(maxR, stability.critical);
  maxR *= 1.25; // margin
  const scale = (Math.min(W, H) / 2) / maxR; // px per AU
  const cx = W / 2;
  const cy = H / 2;
  const toPx = (p) => ({ x: cx + p.x * scale, y: cy - p.y * scale });

  // --- Stability ring (Holman-Wiegert critical radius) ---
  // P-type: planet orbits the barycenter, so the ring is centered there.
  // S-type: planet orbits the primary star, so the ring is centered on it.
  if (stability) {
    const center =
      stability.kind === "inner" && starA ? toPx(starA.pos) : { x: cx, y: cy };
    const rp = stability.critical * scale;
    ctx.beginPath();
    ctx.arc(center.x, center.y, rp, 0, Math.PI * 2);
    ctx.setLineDash([6, 6]);
    ctx.strokeStyle = stability.stable
      ? "rgba(90, 220, 140, 0.5)"
      : "rgba(240, 90, 90, 0.6)";
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = stability.stable
      ? "rgba(90, 220, 140, 0.8)"
      : "rgba(240, 120, 120, 0.9)";
    ctx.font = "11px system-ui, sans-serif";
    const label =
      stability.kind === "outer" ? "stable beyond" : "stable inside";
    ctx.fillText(`a_c ${label}`, center.x + rp + 6, center.y - 4);
  }

  // --- Orbit trails ---
  for (const b of bodies) {
    const tr = trails.get(b);
    if (!tr || tr.length < 2) continue;
    ctx.lineWidth = b.kind === "planet" ? 1.6 : 1.2;
    for (let i = 1; i < tr.length; i++) {
      const a = toPx(tr[i - 1]);
      const c = toPx(tr[i]);
      const alpha = (i / tr.length) * 0.6;
      ctx.strokeStyle =
        b.kind === "planet"
          ? `rgba(120, 200, 255, ${alpha})`
          : rgbStr(massToColor(b.mass), alpha * 0.8);
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(c.x, c.y);
      ctx.stroke();
    }
  }

  // --- Barycenter marker ---
  ctx.strokeStyle = "rgba(255,255,255,0.35)";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(cx - 5, cy);
  ctx.lineTo(cx + 5, cy);
  ctx.moveTo(cx, cy - 5);
  ctx.lineTo(cx, cy + 5);
  ctx.stroke();

  // --- Stars (with glow) ---
  for (const b of bodies) {
    if (b.kind !== "star") continue;
    const p = toPx(b.pos);
    const r = starRadiusPx(b.mass);
    const col = massToColor(b.mass);
    const grad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, r * 3.5);
    grad.addColorStop(0, rgbStr(col, 0.9));
    grad.addColorStop(0.4, rgbStr(col, 0.25));
    grad.addColorStop(1, rgbStr(col, 0));
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(p.x, p.y, r * 3.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = rgbStr(col, 1);
    ctx.beginPath();
    ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "rgba(255,255,255,0.85)";
    ctx.font = "11px system-ui, sans-serif";
    ctx.fillText(b.name, p.x + r + 4, p.y - r - 2);
  }

  // --- Planet ---
  const pp = toPx(planet.pos);
  // line from the planet to its nearest sun, to make "closer sun" legible
  let nearest = null;
  let nd = Infinity;
  for (const b of bodies) {
    if (b.kind !== "star") continue;
    const d = Math.hypot(b.pos.x - planet.pos.x, b.pos.y - planet.pos.y);
    if (d < nd) {
      nd = d;
      nearest = b;
    }
  }
  if (nearest) {
    const np = toPx(nearest.pos);
    ctx.strokeStyle = "rgba(150,200,255,0.25)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(pp.x, pp.y);
    ctx.lineTo(np.x, np.y);
    ctx.stroke();
  }
  ctx.fillStyle = "#7fc8ff";
  ctx.beginPath();
  ctx.arc(pp.x, pp.y, 4.5, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = "rgba(255,255,255,0.7)";
  ctx.lineWidth = 1;
  ctx.stroke();

  // --- Scale bar ---
  drawScaleBar(ctx, W, H, scale);
}

function drawScaleBar(ctx, W, H, scale) {
  // pick a "nice" AU length close to 1/5 of the view
  const targetPx = Math.min(W, H) / 5;
  const targetAu = targetPx / scale;
  const nice = niceNumber(targetAu);
  const px = nice * scale;
  const x = 16;
  const y = H - 20;
  ctx.strokeStyle = "rgba(255,255,255,0.7)";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(x, y);
  ctx.lineTo(x + px, y);
  ctx.stroke();
  ctx.fillStyle = "rgba(255,255,255,0.8)";
  ctx.font = "11px system-ui, sans-serif";
  ctx.fillText(`${nice} AU`, x, y - 6);
}

function niceNumber(v) {
  const exp = Math.floor(Math.log10(v));
  const base = Math.pow(10, exp);
  const f = v / base;
  let nf;
  if (f < 1.5) nf = 1;
  else if (f < 3.5) nf = 2;
  else if (f < 7.5) nf = 5;
  else nf = 10;
  return nf * base;
}

// A cheap static starfield seeded from canvas size (no RNG needed at runtime).
function drawStarfield(ctx, W, H) {
  ctx.save();
  let seed = 12345;
  const rand = () => {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff;
    return seed / 0x7fffffff;
  };
  for (let i = 0; i < 140; i++) {
    const x = rand() * W;
    const y = rand() * H;
    const a = 0.2 + rand() * 0.5;
    ctx.fillStyle = `rgba(255,255,255,${a})`;
    ctx.fillRect(x, y, 1, 1);
  }
  ctx.restore();
}
