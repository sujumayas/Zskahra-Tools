// physics.js — gravitational N-body core for the two-sun simulation.
//
// Units: AU (distance), solar masses (mass), years (time).
// With G = 4*pi^2, a 1 M_sun body on a 1 AU circular orbit has a period of
// exactly 1 year — convenient, human-readable orbital mechanics.

export const G = 4 * Math.PI * Math.PI;

// A small softening length (AU) folded into the force law. It removes the
// 1/r^2 singularity during very close approaches so the integrator can't blow
// up — physically negligible at orbital scales.
const SOFTENING = 1e-3;

// ---- 2D vector helpers (plain {x, y} objects) ----------------------------

export const Vec = {
  add: (a, b) => ({ x: a.x + b.x, y: a.y + b.y }),
  sub: (a, b) => ({ x: a.x - b.x, y: a.y - b.y }),
  scale: (a, s) => ({ x: a.x * s, y: a.y * s }),
  dot: (a, b) => a.x * b.x + a.y * b.y,
  len: (a) => Math.hypot(a.x, a.y),
  norm: (a) => {
    const l = Math.hypot(a.x, a.y) || 1;
    return { x: a.x / l, y: a.y / l };
  },
};

// ---- Body ----------------------------------------------------------------
// A point mass with position, velocity and (cached) acceleration. `kind` is a
// label used only for rendering/insolation ("star" | "planet").

export function makeBody({ mass, pos, vel, kind, name, color }) {
  return {
    mass,
    pos: { ...pos },
    vel: { ...vel },
    acc: { x: 0, y: 0 },
    kind: kind || "body",
    name: name || "",
    color: color || "#ffffff",
  };
}

// ---- Forces --------------------------------------------------------------
// Compute the gravitational acceleration on every body from every other body
// and store it on `body.acc`.

export function computeAccelerations(bodies) {
  for (const b of bodies) {
    b.acc.x = 0;
    b.acc.y = 0;
  }
  for (let i = 0; i < bodies.length; i++) {
    for (let j = i + 1; j < bodies.length; j++) {
      const bi = bodies[i];
      const bj = bodies[j];
      const dx = bj.pos.x - bi.pos.x;
      const dy = bj.pos.y - bi.pos.y;
      const r2 = dx * dx + dy * dy + SOFTENING * SOFTENING;
      const invR = 1 / Math.sqrt(r2);
      const invR3 = invR * invR * invR;
      // a_i toward j: G * m_j * dr / r^3   (and the equal/opposite on j)
      const fi = G * bj.mass * invR3;
      const fj = G * bi.mass * invR3;
      bi.acc.x += fi * dx;
      bi.acc.y += fi * dy;
      bj.acc.x -= fj * dx;
      bj.acc.y -= fj * dy;
    }
  }
}

// ---- Integrator ----------------------------------------------------------
// Velocity-Verlet (a.k.a. leapfrog in kick-drift-kick form). Symplectic and
// second-order: it conserves orbital energy over long runs instead of letting
// the planet spiral in or out the way naive Euler/RK would.

export function stepVelocityVerlet(bodies, dt) {
  // half-kick: v += 0.5 * a * dt   (using accelerations from the previous step)
  for (const b of bodies) {
    b.vel.x += 0.5 * b.acc.x * dt;
    b.vel.y += 0.5 * b.acc.y * dt;
  }
  // drift: x += v * dt
  for (const b of bodies) {
    b.pos.x += b.vel.x * dt;
    b.pos.y += b.vel.y * dt;
  }
  // recompute accelerations at the new positions
  computeAccelerations(bodies);
  // half-kick: v += 0.5 * a * dt   (with the new accelerations)
  for (const b of bodies) {
    b.vel.x += 0.5 * b.acc.x * dt;
    b.vel.y += 0.5 * b.acc.y * dt;
  }
}

// ---- Diagnostics ---------------------------------------------------------
// Total mechanical energy (kinetic + gravitational potential). For a correct
// symplectic integrator this stays nearly constant; the UI reports its drift
// as a live correctness check.

export function totalEnergy(bodies) {
  let ke = 0;
  for (const b of bodies) {
    const v2 = b.vel.x * b.vel.x + b.vel.y * b.vel.y;
    ke += 0.5 * b.mass * v2;
  }
  let pe = 0;
  for (let i = 0; i < bodies.length; i++) {
    for (let j = i + 1; j < bodies.length; j++) {
      const dx = bodies[j].pos.x - bodies[i].pos.x;
      const dy = bodies[j].pos.y - bodies[i].pos.y;
      const r = Math.hypot(dx, dy) || SOFTENING;
      pe += (-G * bodies[i].mass * bodies[j].mass) / r;
    }
  }
  return ke + pe;
}

// Center of mass (barycenter) of a set of bodies.
export function barycenter(bodies) {
  let m = 0;
  let x = 0;
  let y = 0;
  for (const b of bodies) {
    m += b.mass;
    x += b.mass * b.pos.x;
    y += b.mass * b.pos.y;
  }
  return { x: x / m, y: y / m, mass: m };
}
