// sky.js — surface view from the planet. Renders the sky dome with two suns at
// their computed positions, the sky color blended from each above-horizon sun's
// light, and the ground. As the planet spins the suns rise and set at different
// times, giving the signature double sunrise / double sunset.

import { rgbStr, daylightLevel } from "./insolation.js";

export function drawSky(ctx, canvas, skyPos) {
  const W = canvas.width;
  const H = canvas.height;
  const horizonY = H * 0.68;

  // --- Sky color: blend the contributions of suns above the horizon ---
  // Each sun adds light proportional to flux * height. Low suns redden (their
  // blue is scattered away), producing sunset hues.
  let r = 0;
  let g = 0;
  let b = 0;
  let lvl = 0;
  for (const s of skyPos) {
    if (s.altitudeSin <= 0) continue;
    const h = s.altitudeSin; // 0 at horizon .. 1 at zenith
    const w = s.flux * h;
    // redden when low: scale green/blue down as the sun approaches the horizon
    const redden = 0.35 + 0.65 * h;
    r += w * s.color.r;
    g += w * s.color.g * redden;
    b += w * s.color.b * redden * redden;
    lvl += w;
  }

  // Normalize to a displayable sky brightness. tonemap keeps very bright
  // double-day skies from clipping to flat white too quickly.
  const day = daylightLevel(skyPos);
  const bright = tonemap(day);
  let sky;
  if (lvl > 0) {
    const nr = r / lvl;
    const ng = g / lvl;
    const nb = b / lvl;
    sky = {
      r: Math.round(nr * bright + 6 * (1 - bright)),
      g: Math.round(ng * bright + 8 * (1 - bright)),
      b: Math.round(nb * bright + 20 * (1 - bright)),
    };
  } else {
    sky = { r: 6, g: 8, b: 20 }; // night
  }

  // Vertical gradient: lighter near the horizon, darker overhead.
  const grad = ctx.createLinearGradient(0, 0, 0, horizonY);
  grad.addColorStop(0, rgbStr(darken(sky, 0.55)));
  grad.addColorStop(0.7, rgbStr(darken(sky, 0.85)));
  grad.addColorStop(1, rgbStr(brighten(sky, 1.15)));
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, W, horizonY);

  // Stars show through when the sky is dark.
  if (bright < 0.25) drawNightStars(ctx, W, horizonY, 0.25 - bright);

  // --- Suns ---
  // Draw the farther sun first so the nearer one overlaps it.
  const sorted = [...skyPos].sort((a, c) => c.distance - a.distance);
  for (const s of sorted) {
    if (s.altitudeSin <= -0.08) continue; // fully set
    const x = (s.azimuth * 0.5 + 0.5) * W;
    const y = horizonY - s.altitudeSin * (horizonY - 30);
    // apparent size: bigger when closer (relative to a reference distance)
    const radius = Math.max(6, 26 / Math.max(0.4, s.distance));
    const col = s.color;
    // glow
    const glow = ctx.createRadialGradient(x, y, 0, x, y, radius * 5);
    glow.addColorStop(0, rgbStr(col, 0.55));
    glow.addColorStop(0.3, rgbStr(col, 0.2));
    glow.addColorStop(1, rgbStr(col, 0));
    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(x, y, radius * 5, 0, Math.PI * 2);
    ctx.fill();
    // disk
    ctx.fillStyle = rgbStr(col, 1);
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();
  }

  // --- Ground ---
  const groundLight = tonemap(day) * 0.6 + 0.05;
  const gtop = {
    r: Math.round(60 * groundLight + 8),
    g: Math.round(45 * groundLight + 8),
    b: Math.round(40 * groundLight + 10),
  };
  const ggrad = ctx.createLinearGradient(0, horizonY, 0, H);
  ggrad.addColorStop(0, rgbStr(gtop));
  ggrad.addColorStop(1, rgbStr(darken(gtop, 0.4)));
  ctx.fillStyle = ggrad;
  ctx.fillRect(0, horizonY, W, H - horizonY);
  ctx.strokeStyle = "rgba(0,0,0,0.4)";
  ctx.beginPath();
  ctx.moveTo(0, horizonY);
  ctx.lineTo(W, horizonY);
  ctx.stroke();

  // little observer figure for scale/orientation
  ctx.fillStyle = "rgba(10,10,14,0.9)";
  ctx.beginPath();
  ctx.arc(W / 2, horizonY + (H - horizonY) * 0.45, 4, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillRect(W / 2 - 2, horizonY + (H - horizonY) * 0.45, 4, 14);
}

// Compress flux to 0..1 brightness; ~1 solar flux maps to a bright daytime sky.
function tonemap(x) {
  return x / (x + 0.6);
}

function darken(c, f) {
  return { r: c.r * f, g: c.g * f, b: c.b * f };
}
function brighten(c, f) {
  return {
    r: Math.min(255, c.r * f),
    g: Math.min(255, c.g * f),
    b: Math.min(255, c.b * f),
  };
}

function drawNightStars(ctx, W, horizonY, intensity) {
  let seed = 99173;
  const rand = () => {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff;
    return seed / 0x7fffffff;
  };
  ctx.save();
  for (let i = 0; i < 90; i++) {
    const x = rand() * W;
    const y = rand() * horizonY;
    const a = (0.3 + rand() * 0.7) * Math.min(1, intensity * 4);
    ctx.fillStyle = `rgba(255,255,255,${a})`;
    ctx.fillRect(x, y, 1, 1);
  }
  ctx.restore();
}
