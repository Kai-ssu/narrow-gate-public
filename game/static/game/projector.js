// Shared by the projector pages (backdrop and debrief):
// dust in the moonlight, full screen, and a control bar that hides when idle.

const body = document.body;
const room = document.getElementById("room");

function toggleFullscreen() {
  if (document.fullscreenElement) document.exitFullscreen();
  else document.documentElement.requestFullscreen?.().catch(() => {});
}

// True for key presses the page should ignore (held keys, browser shortcuts).
const isShortcut = (event) => event.repeat || event.metaKey || event.ctrlKey || event.altKey;

document.addEventListener("keydown", (event) => {
  if (isShortcut(event) || event.key.toLowerCase() !== "f") return;
  toggleFullscreen();
  event.preventDefault();
});
document.querySelectorAll('[data-action="fullscreen"]').forEach((button) => {
  button.addEventListener("click", () => {
    toggleFullscreen();
    button.blur();
  });
});

// Dust motes drifting through the window light.
const dust = document.getElementById("dust");
for (let i = 0; i < 24; i++) {
  const mote = document.createElement("span");
  mote.className = "mote";
  mote.style.cssText = [
    `left:${35 + Math.random() * 30}%`,
    `top:${15 + Math.random() * 55}%`,
    `--size:${1 + Math.random() * 3}px`,
    `--dx:${(Math.random() - 0.5) * 80}px`,
    `--dur:${12 + Math.random() * 14}s`,
    `--delay:${-Math.random() * 20}s`,
  ].join(";");
  dust.appendChild(mote);
}

// Show the control bar on mouse movement or a tap; hide it (and the cursor) when idle.
let idleTimer;
function wake() {
  body.classList.remove("idle");
  clearTimeout(idleTimer);
  idleTimer = setTimeout(() => body.classList.add("idle"), 3000);
}
for (const type of ["pointermove", "pointerdown"]) document.addEventListener(type, wake);
wake();
