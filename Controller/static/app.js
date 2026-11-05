"use strict";

const $ = (id) => document.getElementById(id);
const canvas = $("clock");
const ctx = canvas.getContext("2d");
const SMOOTHING_SECONDS = 0.05;

let cfg = null;
let socket = null;
let retryMs = 500;
let target = null; // latest angles from the server (degrees), 2 per clock: hour, minute
let shown = null; // smoothed angles actually drawn
let dirty = true;

function setOptions(select, options, value) {
  select.replaceChildren(...options.map((o) => new Option(o, o)));
  select.value = value;
  select.disabled = false;
}

function applyConfig(c) {
  cfg = c;
  const dpr = window.devicePixelRatio || 1;
  canvas.width = c.width * dpr;
  canvas.height = c.height * dpr;
  canvas.style.width = c.width + "px";
  canvas.style.aspectRatio = `${c.width} / ${c.height}`;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  dirty = true;
}

function handleMessage(msg) {
  switch (msg.type) {
    case "state":
      applyConfig(msg.config);
      setOptions($("algorithm"), msg.algorithms, msg.algorithm);
      setOptions($("overnight"), msg.overnightModes, msg.overnightMode);
      $("interface").textContent = msg.interface;
      $("commit").textContent = msg.commit;
      $("log").textContent = msg.log;
      target = shown = null; // snap to the first frame after (re)connect
      break;
    case "algorithm": $("algorithm").value = msg.value; break;
    case "overnightMode": $("overnight").value = msg.value; break;
    case "log": $("log").textContent = msg.value; break;
  }
}

function handleFrame(angles) {
  target = angles;
  if (!shown) shown = Float32Array.from(angles);
  dirty = true;
}

function setStatus(text, ok) {
  const el = $("status");
  el.textContent = text;
  el.className = ok ? "ok" : "";
}

function connect() {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  const ws = new WebSocket(`${proto}://${location.host}/ws`);
  ws.binaryType = "arraybuffer";
  socket = ws;

  ws.onopen = () => { retryMs = 500; setStatus("connected", true); };
  ws.onmessage = (e) => {
    if (typeof e.data === "string") handleMessage(JSON.parse(e.data));
    else handleFrame(new Float32Array(e.data));
  };
  ws.onclose = () => {
    setStatus("disconnected, retrying", false);
    $("algorithm").disabled = $("overnight").disabled = true;
    setTimeout(connect, retryMs);
    retryMs = Math.min(retryMs * 2, 5000);
  };
}

function send(msg) {
  if (socket && socket.readyState === WebSocket.OPEN) socket.send(JSON.stringify(msg));
}

$("algorithm").addEventListener("change", (e) => send({ type: "algorithm", value: e.target.value }));
$("overnight").addEventListener("change", (e) => send({ type: "overnightMode", value: e.target.value }));

async function uploadCalibration(e) {
  const file = e.target.files[0];
  if (!file) return;
  const body = new FormData();
  body.append("file", file);
  try {
    const res = await fetch("/calibration", { method: "POST", body });
    if (!res.ok) $("log").textContent = `upload failed: ${(await res.json()).detail}`;
  } catch (err) {
    $("log").textContent = `upload failed: ${err}`;
  }
  e.target.value = "";
}

for (const input of document.querySelectorAll(".calibration-input")) {
  input.addEventListener("change", uploadCalibration);
}

// Shortest signed difference between two angles in degrees.
const angleDiff = (a, b) => ((b - a + 540) % 360) - 180;

function smooth(dt) {
  if (!target || !shown) return;
  const k = 1 - Math.exp(-dt / SMOOTHING_SECONDS);
  for (let i = 0; i < target.length; i++) {
    const d = angleDiff(shown[i], target[i]);
    if (Math.abs(d) < 0.05) {
      if (shown[i] !== target[i]) { shown[i] = target[i]; dirty = true; }
    } else {
      shown[i] += d * k;
      dirty = true;
    }
  }
}

function drawHand(cx, cy, deg, color) {
  const a = (deg * Math.PI) / 180;
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(Math.PI / 2 - a); // angle 0 points down, increasing counter-clockwise (matches the Bokeh version)
  ctx.fillStyle = color;
  ctx.fillRect(0, -cfg.handWidth / 2, cfg.handLength, cfg.handWidth);
  ctx.restore();
}

function draw() {
  ctx.fillStyle = cfg.backgroundColor;
  ctx.fillRect(0, 0, cfg.width, cfg.height);

  const n = cfg.rows * cfg.cols;
  const centers = [];
  for (let i = 0; i < n; i++) {
    centers.push([
      cfg.padX + ((i % cfg.cols) + 0.5) * cfg.spacing,
      cfg.padY + (Math.floor(i / cfg.cols) + 0.5) * cfg.spacing,
    ]);
  }

  ctx.lineWidth = 1;
  ctx.fillStyle = cfg.recessFillColor;
  ctx.strokeStyle = cfg.recessLineColor;
  for (const [cx, cy] of centers) {
    ctx.beginPath();
    ctx.arc(cx, cy, cfg.clockRadius, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();
  }

  if (shown) {
    centers.forEach(([cx, cy], i) => drawHand(cx, cy, shown[2 * i], cfg.backHandColor));
    centers.forEach(([cx, cy], i) => drawHand(cx, cy, shown[2 * i + 1], cfg.frontHandColor));
  }

  ctx.fillStyle = cfg.frontHandColor;
  for (const [cx, cy] of centers) {
    ctx.beginPath();
    ctx.arc(cx, cy, cfg.handWidth / 2, 0, 2 * Math.PI);
    ctx.fill();
  }
}

let lastTime = performance.now();
function frame(now) {
  const dt = Math.min((now - lastTime) / 1000, 0.25);
  lastTime = now;
  if (cfg) {
    smooth(dt);
    if (dirty) { dirty = false; draw(); }
  }
  requestAnimationFrame(frame);
}

connect();
requestAnimationFrame(frame);
