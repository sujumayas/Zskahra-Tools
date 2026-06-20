// main.js — wires the physics engine, stability model and two renderers to the
// HTML controls, and runs the animation loop.

import { stepVelocityVerlet, totalEnergy } from "./physics.js";
import {
  buildSystem,
  evaluateStability,
  presetDefaults,
} from "./system.js";
import { skyPositions, totalFlux } from "./insolation.js";
import { drawTopDown } from "./topdown.js";
import { drawSky } from "./sky.js";

// ---- DOM handles ----------------------------------------------------------
const $ = (id) => document.getElementById(id);
const topCanvas = $("topdown");
const topCtx = topCanvas.getContext("2d");
const skyCanvas = $("sky");
const skyCtx = skyCanvas.getContext("2d");

const inputs = {
  M1: $("M1"),
  M2: $("M2"),
  sep: $("sep"),
  eb: $("eb"),
  pd: $("pd"),
  speed: $("speed"),
};

// ---- App state ------------------------------------------------------------
const state = {
  params: null, // {type, M1, M2, sep, e_b, planetDist}
  bodies: [],
  starA: null,
  starB: null,
  planet: null,
  trails: new Map(),
  stability: null,
  running: true,
  simTime: 0, // years
  spin: 0, // planet rotation angle (rad) for the sky view
  initialEnergy: 0,
  speed: 1,
  dtPerStep: 1e-3,
  stepsPerFrame: 4,
};

const TRAIL_MAX = { planet: 700, star: 450 };

// ---- Build / rebuild the system from the current params -------------------
function rebuild() {
  const p = state.params;
  const sys = buildSystem(p);
  state.bodies = sys.bodies;
  state.starA = sys.starA;
  state.starB = sys.starB;
  state.planet = sys.planet;
  state.trails = new Map(state.bodies.map((b) => [b, []]));
  state.stability = evaluateStability(p);
  state.simTime = 0;
  state.spin = 0;
  state.initialEnergy = totalEnergy(state.bodies);

  // Choose an integration step that resolves the fastest orbit in the system
  // (the tight Tatooine binary, or the planet, whichever is quicker) with a
  // few hundred steps per period — keeps every preset accurate and stable.
  const mtot = p.M1 + p.M2;
  const pBinary = Math.sqrt(Math.pow(p.sep, 3) / mtot);
  const centralMass = p.type === "p-type" ? mtot : p.M1;
  const pPlanet = Math.sqrt(Math.pow(p.planetDist, 3) / centralMass);
  state.dtPerStep = Math.min(pBinary, pPlanet) / 240;

  updateConfigNote();
  updateStabilityBadge();
}

// ---- Load a named preset into the controls and rebuild --------------------
function loadPreset(name) {
  const d = presetDefaults(name);
  state.params = {
    type: d.type,
    M1: d.M1,
    M2: d.M2,
    sep: d.sep,
    e_b: d.e_b,
    planetDist: d.planetDist,
  };
  inputs.M1.value = d.M1;
  inputs.M2.value = d.M2;
  inputs.sep.value = d.sep;
  inputs.eb.value = d.e_b;
  inputs.pd.value = d.planetDist;
  syncLabels();
  highlightPreset(name);
  rebuild();
}

// ---- Read controls -> params (keeps the configuration type) ---------------
function readControls() {
  state.params.M1 = parseFloat(inputs.M1.value);
  state.params.M2 = parseFloat(inputs.M2.value);
  state.params.sep = parseFloat(inputs.sep.value);
  state.params.e_b = parseFloat(inputs.eb.value);
  state.params.planetDist = parseFloat(inputs.pd.value);
  state.speed = parseFloat(inputs.speed.value);
  syncLabels();
  rebuild();
}

function syncLabels() {
  $("M1-val").textContent = `${parseFloat(inputs.M1.value).toFixed(2)} M☉`;
  $("M2-val").textContent = `${parseFloat(inputs.M2.value).toFixed(2)} M☉`;
  $("sep-val").textContent = `${parseFloat(inputs.sep.value).toFixed(2)} AU`;
  $("eb-val").textContent = parseFloat(inputs.eb.value).toFixed(2);
  $("pd-val").textContent = `${parseFloat(inputs.pd.value).toFixed(2)} AU`;
  $("speed-val").textContent = `${parseFloat(inputs.speed.value).toFixed(1)}×`;
}

function highlightPreset(name) {
  document.querySelectorAll(".preset").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.preset === name);
  });
}

function updateConfigNote() {
  const p = state.params;
  const kind =
    p.type === "p-type"
      ? "Circumbinary (P-type): the planet orbits both suns from outside; whichever sun is on the near side is the closer one right now."
      : "Circumstellar (S-type): the planet orbits the close 'home' sun (A); sun B is the permanent distant companion.";
  $("config-note").textContent = `${kind} ${state.stability.note}.`;
}

function updateStabilityBadge() {
  const el = $("stability");
  const s = state.stability;
  el.textContent = s.stable
    ? `STABLE · a_c = ${s.critical.toFixed(2)} AU`
    : `UNSTABLE · a_c = ${s.critical.toFixed(2)} AU`;
  el.className = `stability ${s.stable ? "stable" : "unstable"}`;
}

// ---- Animation loop -------------------------------------------------------
function frame() {
  if (state.running) {
    const steps = Math.max(1, Math.round(state.stepsPerFrame * state.speed));
    for (let i = 0; i < steps; i++) {
      stepVelocityVerlet(state.bodies, state.dtPerStep);
      state.simTime += state.dtPerStep;
    }
    // Advance the planet's spin so suns visibly rise and set. This is decoupled
    // from orbital time (a planet rotates many times per orbit).
    state.spin += 0.03 * state.speed;

    pushTrails();
  }

  drawTopDown(topCtx, topCanvas, state);
  const skyPos = skyPositions(state.planet, [state.starA, state.starB], state.spin);
  drawSky(skyCtx, skyCanvas, skyPos);
  updateReadouts(skyPos);

  requestAnimationFrame(frame);
}

function pushTrails() {
  for (const b of state.bodies) {
    const tr = state.trails.get(b);
    tr.push({ x: b.pos.x, y: b.pos.y });
    const cap = b.kind === "planet" ? TRAIL_MAX.planet : TRAIL_MAX.star;
    if (tr.length > cap) tr.shift();
  }
}

function updateReadouts(skyPos) {
  const dA = skyPos[0].distance;
  const dB = skyPos[1].distance;
  $("ro-dA").textContent = `${dA.toFixed(3)} AU`;
  $("ro-dB").textContent = `${dB.toFixed(3)} AU`;
  const f = totalFlux(state.planet, [state.starA, state.starB]);
  $("ro-flux").textContent = `${f.toFixed(2)} S⊕`; // relative to 1 sun @ 1 AU
  $("ro-time").textContent = `${state.simTime.toFixed(2)} yr`;
  const drift =
    state.initialEnergy !== 0
      ? (totalEnergy(state.bodies) - state.initialEnergy) / Math.abs(state.initialEnergy)
      : 0;
  $("ro-energy").textContent = `${(drift * 100).toExponential(2)} %`;
}

// ---- Event wiring ---------------------------------------------------------
document.querySelectorAll(".preset").forEach((btn) => {
  btn.addEventListener("click", () => loadPreset(btn.dataset.preset));
});

["M1", "M2", "sep", "eb", "pd"].forEach((k) => {
  inputs[k].addEventListener("input", readControls);
});
inputs.speed.addEventListener("input", () => {
  state.speed = parseFloat(inputs.speed.value);
  syncLabels();
});

$("playpause").addEventListener("click", () => {
  state.running = !state.running;
  $("playpause").textContent = state.running ? "Pause" : "Play";
});
$("reset").addEventListener("click", () => rebuild());

// ---- Boot -----------------------------------------------------------------
// Optional ?preset=s-type|p-type|kepler16b deep-link; defaults to S-type.
const wanted = new URLSearchParams(location.search).get("preset");
const valid = ["s-type", "p-type", "kepler16b"];
loadPreset(valid.includes(wanted) ? wanted : "s-type");
requestAnimationFrame(frame);
