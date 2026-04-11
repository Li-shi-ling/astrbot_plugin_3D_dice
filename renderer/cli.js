#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i += 2) {
    args[argv[i].replace(/^--/, "")] = argv[i + 1];
  }
  return args;
}

function createRng(seed) {
  let value = (seed >>> 0) || 1;
  return function rng() {
    value = (value * 1664525 + 1013904223) >>> 0;
    return value / 0x100000000;
  };
}

function vec(x = 0, y = 0, z = 0) {
  return { x, y, z };
}

function add(a, b) {
  return vec(a.x + b.x, a.y + b.y, a.z + b.z);
}

function sub(a, b) {
  return vec(a.x - b.x, a.y - b.y, a.z - b.z);
}

function scale(v, s) {
  return vec(v.x * s, v.y * s, v.z * s);
}

function dot(a, b) {
  return a.x * b.x + a.y * b.y + a.z * b.z;
}

function cross(a, b) {
  return vec(
    a.y * b.z - a.z * b.y,
    a.z * b.x - a.x * b.z,
    a.x * b.y - a.y * b.x,
  );
}

function length(v) {
  return Math.sqrt(dot(v, v));
}

function normalize(v) {
  const len = length(v) || 1;
  return scale(v, 1 / len);
}

function quat(x = 0, y = 0, z = 0, w = 1) {
  return { x, y, z, w };
}

function quatMul(a, b) {
  return quat(
    a.w * b.x + a.x * b.w + a.y * b.z - a.z * b.y,
    a.w * b.y - a.x * b.z + a.y * b.w + a.z * b.x,
    a.w * b.z + a.x * b.y - a.y * b.x + a.z * b.w,
    a.w * b.w - a.x * b.x - a.y * b.y - a.z * b.z,
  );
}

function quatNormalize(q) {
  const len = Math.sqrt(q.x * q.x + q.y * q.y + q.z * q.z + q.w * q.w) || 1;
  return quat(q.x / len, q.y / len, q.z / len, q.w / len);
}

function quatFromAxisAngle(axis, angle) {
  const half = angle / 2;
  const sin = Math.sin(half);
  const n = normalize(axis);
  return quat(n.x * sin, n.y * sin, n.z * sin, Math.cos(half));
}

function rotateVector(q, v) {
  const qv = quat(v.x, v.y, v.z, 0);
  const qc = quat(-q.x, -q.y, -q.z, q.w);
  const result = quatMul(quatMul(q, qv), qc);
  return vec(result.x, result.y, result.z);
}

function average(points) {
  const total = points.reduce((acc, point) => add(acc, point), vec(0, 0, 0));
  return scale(total, 1 / Math.max(1, points.length));
}

function faceNormal(vertices, face) {
  const a = vertices[face[0]];
  const b = vertices[face[1]];
  const c = vertices[face[2]];
  return normalize(cross(sub(b, a), sub(c, a)));
}

function makeCube() {
  const v = [
    vec(-1, -1, -1), vec(1, -1, -1), vec(1, 1, -1), vec(-1, 1, -1),
    vec(-1, -1, 1), vec(1, -1, 1), vec(1, 1, 1), vec(-1, 1, 1),
  ];
  const faces = [
    { vertices: [4, 5, 6, 7], value: 1 },
    { vertices: [0, 1, 2, 3], value: 6 },
    { vertices: [0, 4, 7, 3], value: 4 },
    { vertices: [1, 5, 6, 2], value: 3 },
    { vertices: [3, 2, 6, 7], value: 2 },
    { vertices: [0, 1, 5, 4], value: 5 },
  ];
  return { vertices: v, faces };
}

function makeTetrahedron() {
  const v = [vec(1, 1, 1), vec(-1, -1, 1), vec(-1, 1, -1), vec(1, -1, -1)];
  const faces = [
    { vertices: [0, 1, 2], value: 1 },
    { vertices: [0, 3, 1], value: 2 },
    { vertices: [0, 2, 3], value: 3 },
    { vertices: [1, 3, 2], value: 4 },
  ];
  return { vertices: v, faces };
}

function makeOctahedron() {
  const v = [vec(1, 0, 0), vec(-1, 0, 0), vec(0, 1, 0), vec(0, -1, 0), vec(0, 0, 1), vec(0, 0, -1)];
  const faces = [
    { vertices: [2, 0, 4], value: 1 },
    { vertices: [2, 4, 1], value: 2 },
    { vertices: [2, 1, 5], value: 3 },
    { vertices: [2, 5, 0], value: 4 },
    { vertices: [3, 4, 0], value: 5 },
    { vertices: [3, 1, 4], value: 6 },
    { vertices: [3, 5, 1], value: 7 },
    { vertices: [3, 0, 5], value: 8 },
  ];
  return { vertices: v, faces };
}

function makeD10(labels) {
  const vertices = [vec(0, 1.4, 0), vec(0, -1.4, 0)];
  for (let i = 0; i < 5; i += 1) {
    const a = (Math.PI * 2 * i) / 5;
    const b = a + Math.PI / 5;
    vertices.push(vec(Math.cos(a), 0.35, Math.sin(a)));
    vertices.push(vec(0.72 * Math.cos(b), -0.35, 0.72 * Math.sin(b)));
  }
  const faces = [];
  for (let i = 0; i < 5; i += 1) {
    const a0 = 2 + i * 2;
    const b0 = 3 + i * 2;
    const a1 = 2 + ((i + 1) % 5) * 2;
    const b1 = 3 + ((i + 1) % 5) * 2;
    faces.push({ vertices: [0, a0, b0, a1], value: labels[i * 2] });
    faces.push({ vertices: [1, a1, b0, b1], value: labels[i * 2 + 1] });
  }
  return { vertices, faces };
}

function makeIcosahedron() {
  const phi = (1 + Math.sqrt(5)) / 2;
  const v = [
    vec(-1, phi, 0), vec(1, phi, 0), vec(-1, -phi, 0), vec(1, -phi, 0),
    vec(0, -1, phi), vec(0, 1, phi), vec(0, -1, -phi), vec(0, 1, -phi),
    vec(phi, 0, -1), vec(phi, 0, 1), vec(-phi, 0, -1), vec(-phi, 0, 1),
  ];
  const faces = [
    [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
    [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
    [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
    [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1],
  ].map((vertices, index) => ({ vertices, value: index + 1 }));
  return { vertices: v, faces };
}

function makeDodecahedron() {
  const ico = makeIcosahedron();
  const centers = ico.faces.map((face) => normalize(average(face.vertices.map((index) => ico.vertices[index]))));
  const adjacency = ico.vertices.map(() => []);
  ico.faces.forEach((face, faceIndex) => {
    face.vertices.forEach((vertexIndex) => adjacency[vertexIndex].push(faceIndex));
  });

  const faces = adjacency.map((faceIndices, index) => {
    const axis = normalize(ico.vertices[index]);
    const basisA = normalize(Math.abs(axis.x) < 0.9 ? cross(axis, vec(1, 0, 0)) : cross(axis, vec(0, 1, 0)));
    const basisB = normalize(cross(axis, basisA));
    const sorted = [...faceIndices].sort((a, b) => {
      const va = centers[a];
      const vb = centers[b];
      return Math.atan2(dot(va, basisB), dot(va, basisA)) - Math.atan2(dot(vb, basisB), dot(vb, basisA));
    });
    return { vertices: sorted, value: index + 1 };
  });
  return { vertices: centers, faces };
}

function geometryForSides(sides) {
  if (sides === 4) return makeTetrahedron();
  if (sides === 6) return makeCube();
  if (sides === 8) return makeOctahedron();
  if (sides === 10) return makeD10([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
  if (sides === 12) return makeDodecahedron();
  if (sides === 20) return makeIcosahedron();
  if (sides === 100) return makeD10([0, 10, 20, 30, 40, 50, 60, 70, 80, 90]);
  throw new Error(`Unsupported sides ${sides}`);
}

function themeForName(name, width, height) {
  const themes = {
    classic: {
      background_top: "#1f2937",
      background_bottom: "#0f172a",
      floor_color: "#111827",
      die_color: "#f8fafc",
      edge_color: "#0f172a",
      label_color: "#111827",
    },
    ember: {
      background_top: "#4c1d15",
      background_bottom: "#1c1917",
      floor_color: "#292524",
      die_color: "#fed7aa",
      edge_color: "#7c2d12",
      label_color: "#431407",
    },
    emerald: {
      background_top: "#064e3b",
      background_bottom: "#022c22",
      floor_color: "#052e2b",
      die_color: "#d1fae5",
      edge_color: "#065f46",
      label_color: "#022c22",
    },
    midnight: {
      background_top: "#111827",
      background_bottom: "#030712",
      floor_color: "#0f172a",
      die_color: "#cbd5e1",
      edge_color: "#334155",
      label_color: "#020617",
    },
  };
  const selected = themes[name] || themes.classic;
  return { ...selected, width, height };
}

function buildDiceList(request, rng) {
  const dice = [];
  let index = 0;
  request.dice.forEach((spec) => {
    for (let count = 0; count < spec.count; count += 1) {
      const geometry = geometryForSides(spec.sides);
      const radius = Math.max(...geometry.vertices.map((vertex) => length(vertex)));
      dice.push({
        sides: spec.sides,
        label: `d${spec.sides}#${count + 1}`,
        geometry,
        radius,
        position: vec(-1.8 + index * 1.15, 3.0 + rng() * 1.4, (rng() - 0.5) * 1.2),
        velocity: vec((rng() - 0.5) * 2.8, -0.6 - rng() * 0.4, (rng() - 0.5) * 1.6),
        rotation: quatNormalize(quat(rng(), rng(), rng(), rng())),
        angularVelocity: vec((rng() - 0.5) * 6, (rng() - 0.5) * 6, (rng() - 0.5) * 6),
      });
      index += 1;
    }
  });
  return dice;
}

function integrate(die, dt) {
  die.velocity.y -= 9.2 * dt;
  die.position = add(die.position, scale(die.velocity, dt));
  const speed = length(die.angularVelocity);
  if (speed > 0.0001) {
    const delta = quatFromAxisAngle(die.angularVelocity, speed * dt);
    die.rotation = quatNormalize(quatMul(delta, die.rotation));
  }
  die.velocity = scale(die.velocity, 0.992);
  die.angularVelocity = scale(die.angularVelocity, 0.985);

  const floor = -1.7;
  if (die.position.y - die.radius < floor) {
    die.position.y = floor + die.radius;
    die.velocity.y = Math.abs(die.velocity.y) * 0.52;
    die.velocity.x *= 0.88;
    die.velocity.z *= 0.88;
    die.angularVelocity.x *= 0.92;
    die.angularVelocity.z *= 0.92;
  }

  const limitX = 3.2;
  const limitZ = 2.0;
  if (Math.abs(die.position.x) + die.radius > limitX) {
    die.position.x = Math.sign(die.position.x) * (limitX - die.radius);
    die.velocity.x *= -0.56;
  }
  if (Math.abs(die.position.z) + die.radius > limitZ) {
    die.position.z = Math.sign(die.position.z) * (limitZ - die.radius);
    die.velocity.z *= -0.56;
  }
}

function resolveCollisions(dice) {
  for (let i = 0; i < dice.length; i += 1) {
    for (let j = i + 1; j < dice.length; j += 1) {
      const a = dice[i];
      const b = dice[j];
      const delta = sub(b.position, a.position);
      const distance = length(delta) || 0.0001;
      const minDistance = (a.radius + b.radius) * 0.78;
      if (distance >= minDistance) continue;
      const normal = scale(delta, 1 / distance);
      const correction = (minDistance - distance) / 2;
      a.position = add(a.position, scale(normal, -correction));
      b.position = add(b.position, scale(normal, correction));
      const relative = sub(b.velocity, a.velocity);
      const impulse = dot(relative, normal);
      if (impulse < 0) {
        const response = scale(normal, impulse * 0.68);
        a.velocity = add(a.velocity, response);
        b.velocity = sub(b.velocity, response);
      }
    }
  }
}

function worldVertices(die) {
  return die.geometry.vertices.map((vertex) => add(rotateVector(die.rotation, vertex), die.position));
}

function project(point, width, height) {
  const camera = vec(0, 2.6, 8.5);
  const relative = sub(point, camera);
  const depth = Math.max(0.2, -relative.z + 12);
  const focal = Math.min(width, height) * 0.78;
  return {
    x: width / 2 + (relative.x * focal) / depth,
    y: height * 0.62 - (relative.y * focal) / depth,
    depth,
  };
}

function shadeColor(hex, amount) {
  const clean = hex.replace("#", "");
  const base = parseInt(clean, 16);
  const clamp = (value) => Math.max(0, Math.min(255, value));
  const r = clamp(((base >> 16) & 0xff) * amount);
  const g = clamp(((base >> 8) & 0xff) * amount);
  const b = clamp((base & 0xff) * amount);
  return `#${[r, g, b].map((value) => Math.round(value).toString(16).padStart(2, "0")).join("")}`;
}

function topValue(die) {
  let bestValue = die.geometry.faces[0].value;
  let bestScore = -Infinity;
  for (const face of die.geometry.faces) {
    const localNormal = faceNormal(die.geometry.vertices, face.vertices);
    const worldNormal = rotateVector(die.rotation, localNormal);
    const score = dot(worldNormal, vec(0, 1, 0));
    if (score > bestScore) {
      bestScore = score;
      bestValue = face.value;
    }
  }
  return bestValue;
}

function buildFrames(request, dice, theme) {
  const frames = [];
  const dt = 1 / Math.max(12, request.fps);
  for (let frameIndex = 0; frameIndex < request.frames; frameIndex += 1) {
    dice.forEach((die) => integrate(die, dt));
    resolveCollisions(dice);
    frames.push(renderFrame(dice, theme, request.width, request.height));
  }
  return frames;
}

function renderFrame(dice, theme, width, height) {
  const polygons = [];
  const labels = [];
  const lightDirection = normalize(vec(-0.8, 1.1, 1.0));

  dice.forEach((die) => {
    const points3d = worldVertices(die);
    die.geometry.faces.forEach((face) => {
      const worldFace = face.vertices.map((index) => points3d[index]);
      const center = average(worldFace);
      const normal = faceNormal(points3d, face.vertices);
      if (dot(normal, vec(0, 0.2, 1)) >= 0) {
        return;
      }
      const projected = worldFace.map((point) => project(point, width, height));
      const brightness = 0.6 + Math.max(0, dot(normal, lightDirection)) * 0.45;
      polygons.push({
        depth: center.z,
        points: projected.map((point) => [Math.round(point.x), Math.round(point.y)]),
        fill: shadeColor(theme.die_color, brightness),
        outline: theme.edge_color,
        alpha: 255,
      });
      const screenCenter = project(center, width, height);
      labels.push({
        depth: center.z,
        x: Math.round(screenCenter.x),
        y: Math.round(screenCenter.y),
        text: String(face.value),
        color: theme.label_color,
      });
    });
  });

  polygons.sort((a, b) => a.depth - b.depth);
  labels.sort((a, b) => a.depth - b.depth);
  return { polygons, labels };
}

function main() {
  const args = parseArgs(process.argv);
  const inputPath = path.resolve(args.input);
  const outputPath = path.resolve(args.output);
  const request = JSON.parse(fs.readFileSync(inputPath, "utf8"));
  const rng = createRng(request.seed || 1);
  const dice = buildDiceList(request, rng);
  const theme = themeForName(request.theme, request.width, request.height);
  const frames = buildFrames(request, dice, theme);
  const values = dice.map((die) => topValue(die));
  const result = {
    theme,
    frames,
    values,
    dice_labels: dice.map((die) => die.label),
  };
  fs.writeFileSync(outputPath, JSON.stringify(result));
}

main();
