// Projector backdrop: room countdown, narration, ambience, earthquake cue (for games
// that have one) and the player QR code.
// Keys: I story · Space start/pause · E earthquake · Q QR code · T timer on/off
//       S sound on/off · D debrief · R reset (F full screen is in projector.js).
// URL options: ?minutes=45 for a different game length, ?timer=off to hide the clock,
// ?start=1 to start the timer on arrival (the story's "Start the game" button).

// Each game keeps its own room timer.
const STORAGE_KEY = `narrow-gate-timer:${body.dataset.game}`;
const params = new URLSearchParams(location.search);
const minutes = Number(params.get("minutes")) || Number(body.dataset.minutes) || 40;
const DURATION = minutes * 60 * 1000;
const LOW_AT = 5 * 60 * 1000;

// Atmosphere lines from the game's data (backdrop_lines); free of answers.
const LINES = JSON.parse(document.getElementById("backdrop-lines").textContent);

const clock = document.getElementById("clock");
const status = document.getElementById("status");
const line = document.getElementById("line");
const TIME_UP = line.dataset.timeUp;
const joinPanel = document.getElementById("join");
const debriefLink = document.getElementById("debrief-link");
const storyLink = document.getElementById("story-link");
const button = (action) => document.querySelector(`[data-action="${action}"]`);
const label = (action, text) => (button(action).firstChild.textContent = `${text} `);

// ---- Timer (kept in localStorage so a refresh doesn't lose it) ----

const fresh = () => ({ duration: DURATION, remaining: DURATION, startedAt: null });

function load() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (saved && typeof saved.remaining === "number") {
      // A different ?minutes value starts over, unless a game is running.
      if (saved.duration !== DURATION && !saved.startedAt) return fresh();
      return saved;
    }
  } catch {}
  return fresh();
}

function save() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(timer));
  } catch {}
}

let timer = load();

const running = () => timer.startedAt !== null;
const remaining = () =>
  running() ? Math.max(0, timer.remaining - (Date.now() - timer.startedAt)) : timer.remaining;

function format(ms) {
  const total = Math.ceil(ms / 1000);
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, "0")}`;
}

function render() {
  const left = remaining();
  const done = left <= 0;
  if (done && running()) {
    timer = { ...timer, remaining: 0, startedAt: null };
    save();
    Sound.stopAmbience();
    if (showClock) Sound.play("bell");
  }
  clock.textContent = format(left);
  body.classList.toggle("low", left > 0 && left <= LOW_AT);
  body.classList.toggle("done", done);
  body.classList.toggle("paused", !running() && !done && left < timer.duration);

  if (done) status.textContent = "Time's up";
  else if (running()) status.textContent = "";
  else if (left < timer.duration) status.textContent = "Paused";
  else status.textContent = "";

  label("toggle", running() ? "Pause" : left < timer.duration ? "Resume" : "Start");
}

// Start/pause also starts/stops the ambience, so the room goes quiet when paused.
function toggle() {
  if (running()) {
    timer = { ...timer, remaining: remaining(), startedAt: null };
    Sound.stopAmbience();
  } else if (remaining() > 0) {
    timer = { ...timer, startedAt: Date.now() };
    Sound.wake();
    Sound.startAmbience();
    keepAwake();
    setQr(false); // players have joined by now
  }
  save();
  render();
}

function reset() {
  if (!window.confirm(`Reset the timer to ${format(DURATION)}?`)) return;
  timer = fresh();
  save();
  Sound.stopAmbience();
  setQr(true);
  render();
}

// ---- Clock on/off (the countdown keeps running underneath) ----

let showClock = params.get("timer") !== "off";

function applyClock() {
  body.classList.toggle("no-timer", !showClock);
  label("clock", showClock ? "Timer on" : "Timer off");
}

function toggleClock() {
  showClock = !showClock;
  // Keep the choice in the address so a refresh remembers it.
  if (showClock) params.delete("timer");
  else params.set("timer", "off");
  const query = params.toString();
  history.replaceState(null, "", query ? `?${query}` : location.pathname);
  applyClock();
}

// ---- Player QR code: shown before the game, hidden once it starts ----

function setQr(shown) {
  body.classList.toggle("qr-hidden", !shown);
}
const toggleQr = () => setQr(body.classList.contains("qr-hidden"));
joinPanel.addEventListener("click", () => setQr(false));

// ---- Earthquake cue ----

function quake() {
  room.classList.remove("quake");
  void room.offsetWidth; // restart the animation if triggered twice
  room.classList.add("quake");
  Sound.play("quake");
}
room.addEventListener("animationend", (event) => {
  if (event.animationName === "quake") room.classList.remove("quake");
});

// ---- Sound ----

function toggleSound() {
  Sound.setEnabled(!Sound.enabled);
  if (Sound.enabled && running()) Sound.startAmbience();
  label("sound", Sound.enabled ? "Sound on" : "Sound off");
}

// Browsers need a click or key press before playing audio. If the page was
// refreshed mid-game, the ambience resumes on the first one.
for (const type of ["pointerdown", "keydown"]) {
  document.addEventListener(
    type,
    () => {
      Sound.wake();
      if (running()) Sound.startAmbience();
    },
    { capture: true },
  );
}

// ---- Keeping the projector awake ----

let wakeLock = null;
async function keepAwake() {
  try {
    wakeLock = await navigator.wakeLock?.request("screen");
  } catch {}
}
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible" && running()) keepAwake();
});

// ---- Narration lines ----

let lineIndex = 0;
function showLine(text) {
  line.classList.add("fading");
  setTimeout(() => {
    line.textContent = text;
    line.classList.remove("fading");
  }, 1200);
}
line.textContent = LINES[0] || "";
setInterval(() => {
  if (showClock && remaining() <= 0) {
    if (line.textContent !== TIME_UP) showLine(TIME_UP);
    return;
  }
  if (!LINES.length) return;
  lineIndex = (lineIndex + 1) % LINES.length;
  showLine(LINES[lineIndex]);
}, 40000);

// ---- Controls ----

const actions = { toggle, quake, reset, qr: toggleQr, clock: toggleClock, sound: toggleSound };
document.querySelectorAll("[data-action]").forEach((el) => {
  const action = actions[el.dataset.action];
  if (!action) return; // full screen is handled in projector.js
  el.addEventListener("click", () => {
    action();
    el.blur(); // so Space doesn't also "click" the focused button
  });
});

document.addEventListener("keydown", (event) => {
  if (isShortcut(event)) return;
  const key = event.key.toLowerCase();
  if (key === " ") toggle();
  else if (key === "e" && button("quake")) quake();
  else if (key === "q") toggleQr();
  else if (key === "t") toggleClock();
  else if (key === "s") toggleSound();
  else if (key === "d") location.href = debriefLink.href;
  else if (key === "i") location.href = storyLink.href;
  else if (key === "r") reset();
  else return;
  event.preventDefault();
});

setQr(!running());
applyClock();

// Arriving from the story's "Start the game": start the timer, then tidy the address.
if (params.get("start") === "1") {
  params.delete("start");
  const query = params.toString();
  history.replaceState(null, "", query ? `?${query}` : location.pathname);
  if (!running() && remaining() > 0) toggle();
}
label("sound", Sound.enabled ? "Sound on" : "Sound off");
render();
setInterval(render, 250);
