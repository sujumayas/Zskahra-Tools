// system.js — build initial conditions for a two-sun system and evaluate
// orbital stability using the Holman & Wiegert (1999) criteria.
//
// Two star+planet configurations are supported (the engine is the same; only
// the initial conditions differ):
//
//   S-type (circumstellar): the planet orbits the primary "home" sun closely
//     while a second sun sits far away. The closer/farther relationship is
//     PERMANENT. Stable only when a_planet < a_crit_inner (a fraction of the
//     binary separation).
//
//   P-type (circumbinary / "Tatooine"): the two suns orbit each other tightly
//     and the planet orbits BOTH from well outside. Whichever sun is on the
//     near side is "closer" at that instant. Stable only when
//     a_planet > a_crit_outer.

import { G, Vec, makeBody, computeAccelerations, barycenter } from "./physics.js";

// Speed for a circular orbit of a test body at radius r around mass M.
export function circularSpeed(M, r) {
  return Math.sqrt((G * M) / r);
}

// Vis-viva speed: orbital speed at separation r for a two-body orbit of
// semi-major axis a around total mass M.
export function visVivaSpeed(M, r, a) {
  return Math.sqrt(G * M * (2 / r - 1 / a));
}

// Star colors mirror the temperature mapping in insolation.js (massToColor),
// kept here so presets read nicely. Lower mass => cooler/redder.
const PRESETS = {
  "s-type": {
    type: "s-type",
    label: "S-type (home + distant sun)",
    M1: 1.0, // primary "home" sun (the close one)
    M2: 0.5, // distant companion sun
    sep: 18, // binary semi-major axis (AU) — large, so the companion is far
    e_b: 0.2, // binary eccentricity
    planetDist: 1.4, // planet's orbit radius around the primary (AU)
  },
  "p-type": {
    type: "p-type",
    label: "P-type (Tatooine)",
    M1: 1.0,
    M2: 0.8,
    sep: 0.3, // tight binary
    e_b: 0.1,
    planetDist: 1.6, // planet orbits both suns from outside
  },
  "kepler16b": {
    type: "p-type",
    label: "Kepler-16b-like",
    M1: 0.6897,
    M2: 0.2026,
    sep: 0.2243,
    e_b: 0.1594,
    planetDist: 0.7048,
  },
};

export function presetNames() {
  return Object.keys(PRESETS);
}

export function presetDefaults(name) {
  return { ...PRESETS[name] };
}

// ---- Holman & Wiegert (1999) stability limits ----------------------------
// Both fits are polynomials in the binary eccentricity e and the mass ratio mu,
// returning the critical planet semi-major axis as a multiple of the binary
// separation a_b.

// P-type (circumbinary) OUTER limit: planet stable when a_p > a_crit.
// mu = m2 / (m1 + m2). Valid for mu in [0.1, 0.9], e in [0, 0.7].
export function criticalRadiusOuter(mu, e, ab) {
  const ac =
    1.6 +
    5.1 * e +
    -2.22 * e * e +
    4.12 * mu +
    -4.27 * e * mu +
    -5.09 * mu * mu +
    4.61 * e * e * mu * mu;
  return ac * ab;
}

// S-type (circumstellar) INNER limit: planet (around the primary) stable when
// a_p < a_crit. Here mu = m_companion / (m1 + m2).
export function criticalRadiusInner(mu, e, ab) {
  const ac =
    0.464 +
    -0.38 * mu +
    -0.631 * e +
    0.586 * mu * e +
    0.15 * e * e +
    -0.198 * mu * e * e;
  return ac * ab;
}

// Evaluate stability for the current parameters. Returns the critical radius,
// the planet's orbital radius, a boolean, and a human-readable note.
export function evaluateStability(p) {
  const mtot = p.M1 + p.M2;
  if (p.type === "p-type") {
    const mu = p.M2 / mtot;
    const ac = criticalRadiusOuter(mu, p.e_b, p.sep);
    return {
      stable: p.planetDist > ac,
      critical: ac,
      planetRadius: p.planetDist,
      kind: "outer",
      note: `Circumbinary: planet must orbit beyond a_c = ${ac.toFixed(2)} AU`,
    };
  }
  // s-type: companion is M2, planet orbits the primary M1
  const mu = p.M2 / mtot;
  const ac = criticalRadiusInner(mu, p.e_b, p.sep);
  return {
    stable: p.planetDist < ac,
    critical: ac,
    planetRadius: p.planetDist,
    kind: "inner",
    note: `Circumstellar: planet must orbit inside a_c = ${ac.toFixed(2)} AU`,
  };
}

// ---- Initial conditions --------------------------------------------------
// Build the three bodies (two stars + planet) for the given parameters, set in
// the barycentric frame so the whole system has ~zero net momentum and stays
// centered on screen.

export function buildSystem(p) {
  const mtot = p.M1 + p.M2;

  // --- Binary stars ---
  // Start the pair at apoapsis along the x-axis. r_apo is the separation when
  // the stars are farthest apart; vis-viva gives the (slower) speed there.
  const rApo = p.sep * (1 + p.e_b);
  // distances of each star from the barycenter at this instant
  const r1 = rApo * (p.M2 / mtot); // primary sits closer to the barycenter
  const r2 = rApo * (p.M1 / mtot);
  // relative speed of the two stars at apoapsis, split by mass to the barycenter
  const vRel = visVivaSpeed(mtot, rApo, p.sep);
  const v1 = vRel * (p.M2 / mtot);
  const v2 = vRel * (p.M1 / mtot);

  const starA = makeBody({
    mass: p.M1,
    pos: { x: -r1, y: 0 },
    vel: { x: 0, y: -v1 },
    kind: "star",
    name: "Sun A",
  });
  const starB = makeBody({
    mass: p.M2,
    pos: { x: r2, y: 0 },
    vel: { x: 0, y: v2 },
    kind: "star",
    name: "Sun B",
  });

  // --- Planet ---
  let planet;
  if (p.type === "p-type") {
    // Circumbinary: place the planet outside the binary, orbiting the system's
    // total mass about the barycenter (origin).
    const r = p.planetDist;
    const vc = circularSpeed(mtot, r);
    planet = makeBody({
      mass: 3e-6, // ~Earth mass in solar masses; tiny, near-test-particle
      pos: { x: r, y: 0 },
      vel: { x: 0, y: vc },
      kind: "planet",
      name: "Planet",
    });
  } else {
    // Circumstellar (S-type): the planet orbits the primary "home" sun. Its
    // velocity is the star's velocity plus a circular velocity about the star.
    const r = p.planetDist;
    const vc = circularSpeed(p.M1, r);
    planet = makeBody({
      mass: 3e-6,
      pos: { x: starA.pos.x + r, y: starA.pos.y },
      vel: { x: starA.vel.x, y: starA.vel.y + vc },
      kind: "planet",
      name: "Planet",
    });
  }

  const bodies = [starA, starB, planet];

  // Remove any residual net momentum so the barycenter stays put on screen.
  const bc = barycenter(bodies);
  let px = 0;
  let py = 0;
  for (const b of bodies) {
    px += b.mass * b.vel.x;
    py += b.mass * b.vel.y;
  }
  for (const b of bodies) {
    b.vel.x -= px / bc.mass;
    b.vel.y -= py / bc.mass;
  }
  // Recenter positions on the barycenter.
  for (const b of bodies) {
    b.pos.x -= bc.x;
    b.pos.y -= bc.y;
  }

  computeAccelerations(bodies);
  return { bodies, starA, starB, planet };
}
