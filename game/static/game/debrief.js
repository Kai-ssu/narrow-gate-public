// Debrief slides: one discussion question per screen.
// Keys: → / Space / Page Down next · ← / Page Up previous (works with presentation clickers)
//       B back to the backdrop.

const slides = [...document.querySelectorAll(".slide")];
const counter = document.getElementById("counter");
let current = 0;

function show(index) {
  current = Math.max(0, Math.min(slides.length - 1, index));
  slides.forEach((slide, i) => (slide.hidden = i !== current));
  counter.textContent = current === 0 ? "" : `${current} / ${slides.length - 1}`;
  history.replaceState(null, "", `#${current}`);
}

const actions = { next: () => show(current + 1), prev: () => show(current - 1) };

document.querySelectorAll("[data-action]").forEach((button) => {
  const action = actions[button.dataset.action];
  if (!action) return;
  button.addEventListener("click", () => {
    action();
    button.blur();
  });
});

document.addEventListener("keydown", (event) => {
  if (isShortcut(event)) return;
  if (["ArrowRight", "PageDown", " "].includes(event.key)) actions.next();
  else if (["ArrowLeft", "PageUp"].includes(event.key)) actions.prev();
  else if (event.key.toLowerCase() === "b") location.href = document.getElementById("backdrop-link").href;
  else return;
  event.preventDefault();
});

// Reopen on the same slide after a refresh.
show(Number(location.hash.slice(1)) || 0);
