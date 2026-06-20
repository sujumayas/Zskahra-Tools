// insolation.js — how much light each sun delivers to the planet, what color
// each sun is, and where each sun sits in the planet's sky as it spins.
//
// This is the layer that makes a two-sun world feel distinct: two suns of
// different size and color, rising and setting at different times, producing
// double sunsets and a shifting sky color.

import { Vec } from "./physics.js";

// Main-sequence mass-luminosity relation: L ~ M^3.5 (in solar units). A small
// companion is dramatically dimmer than a sun-like primary.
export function luminosity(mass) {
  return Math.pow(mass, 3.5);
}

// Flux (relative solar-flux-at-1-AU units) reaching the planet from a sun of
// the given luminosity at distance d (AU). The 1/(4*pi) constant is folded
// away, so a 1 L_sun star at 1 AU yields F = 1.
export function flux(lum, d) {
  return lum / (d * d);
}

// Approximate mass -> photospheric color. More massive main-sequence stars are
// hotter (bluer/whiter); low-mass stars are cooler (orange/red). Returns
// {r, g, b} in 0..255.
export function massToColor(mass) {
  // Control points roughly following the main sequence.
  const stops = [
    { m: 0.1, c: [255, 110, 70] }, // M dwarf — deep orange/red
    { m: 0.3, c: [255, 150, 90] }, // late K — orange
    { m: 0.6, c: [255, 205, 150] }, // K/G — warm yellow
    { m: 1.0, c: [255, 244, 234] }, // G (sun-like) — near white
    { m: 1.5, c: [220, 230, 255] }, // F/A — white-blue
    { m: 3.0, c: [180, 200, 255] }, // hot — blue
  ];
  if (mass <= stops[0].m) return rgb(stops[0].c);
  if (mass >= stops[stops.length - 1].m) return rgb(stops[stops.length - 1].c);
  for (let i = 0; i < stops.length - 1; i++) {
    const a = stops[i];
    const b = stops[i + 1];
    if (mass >= a.m && mass <= b.m) {
      const t = (mass - a.m) / (b.m - a.m);
      return rgb([
        a.c[0] + (b.c[0] - a.c[0]) * t,
        a.c[1] + (b.c[1] - a.c[1]) * t,
        a.c[2] + (b.c[2] - a.c[2]) * t,
      ]);
    }
  }
  return rgb(stops[stops.length - 1].c);
}

function rgb(c) {
  return { r: Math.round(c[0]), g: Math.round(c[1]), b: Math.round(c[2]) };
}

export function rgbStr(c, a = 1) {
  return `rgba(${c.r}, ${c.g}, ${c.b}, ${a})`;
}

// ---- Sky geometry --------------------------------------------------------
// The observer stands on the planet's equator; the spin axis is perpendicular
// to the orbital plane. As the planet spins (angle `spin`), the local zenith
// direction rotates. For a sun in world-direction d (unit vector from planet
// to sun):
//
//   altitude = asin(d . zenith)   -> +pi/2 overhead, 0 at horizon, <0 below
//   azimuth  = d . east           -> -1 (left) .. +1 (right) along the horizon
//
// This is a faithful little spherical-astronomy model, just reduced to the
// equatorial plane.
export function skyPositions(planet, suns, spin) {
  const zenith = { x: Math.cos(spin), y: Math.sin(spin) };
  const east = { x: -Math.sin(spin), y: Math.cos(spin) };
  return suns.map((s) => {
    const toSun = Vec.sub(s.pos, planet.pos);
    const d = Vec.len(toSun);
    const dir = Vec.scale(toSun, 1 / (d || 1));
    const h = Vec.dot(dir, zenith); // sin(altitude), -1..1
    const a = Vec.dot(dir, east); // horizontal placement, -1..1
    const lum = luminosity(s.mass);
    return {
      body: s,
      distance: d,
      altitudeSin: h, // >0 => above horizon
      azimuth: a,
      flux: flux(lum, d),
      color: massToColor(s.mass),
    };
  });
}

// Total illumination on the planet right now (sum of each sun's flux, ignoring
// sky position) — drives the "brightness" readouts.
export function totalFlux(planet, suns) {
  let f = 0;
  for (const s of suns) {
    const d = Vec.len(Vec.sub(s.pos, planet.pos));
    f += flux(luminosity(s.mass), d);
  }
  return f;
}

// Daylight contribution: only suns above the horizon light the sky, weighted by
// how high they are (a sun near the horizon lights the sky weakly and redder).
// Returns a 0..~ value used to set sky brightness.
export function daylightLevel(skyPos) {
  let lvl = 0;
  for (const s of skyPos) {
    if (s.altitudeSin > 0) lvl += s.flux * s.altitudeSin;
  }
  return lvl;
}
