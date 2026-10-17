// Story mode: the host backstory from the Facilitator Guide, played on the projector
// as captions over changing scenery, with music and sound effects.
// Keys: Space play/pause · → next line · ← previous line · R restart · B backdrop
// (F full screen is in projector.js).

// The game's scenes come from its data (story_scenes): each sets the look, plays an
// optional cue, then shows its lines one at a time.
//   setting: "outside" (the game's story scenery) or "inside" (the cell)
//   tint:    red wash over the scene      moon: the moon brightens in the cell window
//   effect:  one of the cues below, played when the scene starts
const SCENES = JSON.parse(document.getElementById("story-scenes").textContent);

// Flatten into one list of lines, each knowing its scene.
const STEPS = SCENES.flatMap((scene, sceneIndex) =>
  scene.lines.map((text, lineIndex) => ({ scene, sceneIndex, text, first: lineIndex === 0 })),
);

// Long enough to read from the back of a room: a base pause plus time per word.
const readingTime = (text) => 2600 + text.split(/\s+/).length * 330;

const title = document.getElementById("title");
const caption = document.getElementById("caption");
const finale = document.getElementById("finale");
const progress = document.getElementById("progress");
const label = (action, text) =>
  (document.querySelector(`[data-action="${action}"]`).firstChild.textContent = `${text} `);

let step = -1; // -1 = title card
let sceneShown = 0; // which scene's look is on screen
let playing = false;
let timer = null;

// ---- Scene cues ----

const cues = {
  crowd() {
    Sound.play("crowd");
  },
  beating() {
    [400, 1300, 2200].forEach((ms) =>
      setTimeout(() => {
        if (!playing) return;
        Sound.play("strike");
        flash();
      }, ms),
    );
  },
  slam() {
    Sound.play("slam");
    flash();
  },
  finale() {
    Sound.play("swell");
  },
};

function flash() {
  room.classList.remove("flash");
  void room.offsetWidth; // restart the animation
  room.classList.add("flash");
}

function setScene(scene, playCue) {
  body.classList.toggle("outside", scene.setting === "outside");
  body.classList.toggle("tint-red", Boolean(scene.tint));
  body.classList.toggle("moonrise", Boolean(scene.moon));
  if (playCue && scene.effect) cues[scene.effect]();
}

// ---- Playback ----

function show(index, { playCue = true } = {}) {
  clearTimeout(timer);
  step = Math.max(0, Math.min(STEPS.length - 1, index));
  const current = STEPS[step];
  title.hidden = true;

  // Entering a scene (in order or by jumping): apply its look. Its sound cue
  // only plays when arriving at its first line, so cues never play out of order.
  if (current.sceneIndex !== sceneShown || current.first) {
    setScene(current.scene, playCue && current.first);
    sceneShown = current.sceneIndex;
  }

  caption.classList.add("hidden");
  setTimeout(() => {
    caption.textContent = current.text;
    caption.classList.remove("hidden");
  }, 450);

  const last = step === STEPS.length - 1;
  finale.hidden = !last;
  progress.style.width = `${((step + 1) / STEPS.length) * 100}%`;

  if (last) {
    pause();
    label("toggle", "Replay");
    Sound.stopScore();
  } else if (playing) {
    timer = setTimeout(() => show(step + 1), readingTime(current.text));
  }
}

function play() {
  Sound.wake(); // inside the click or key press, so audio is allowed
  if (step === STEPS.length - 1) step = -1; // replay from the start
  playing = true;
  label("toggle", "Pause");
  body.classList.add("playing");
  Sound.startScore();
  show(step < 0 ? 0 : step);
}

function pause() {
  playing = false;
  clearTimeout(timer);
  label("toggle", "Play");
  body.classList.remove("playing");
  Sound.stopScore();
}

const toggle = () => (playing ? pause() : play());

function restart() {
  pause();
  step = -1;
  caption.classList.add("hidden");
  finale.hidden = true;
  title.hidden = false;
  progress.style.width = "0";
  setScene(SCENES[0], false);
  sceneShown = 0;
}

// Manual stepping shows lines without replaying sound cues out of order.
const actions = {
  toggle,
  next: () => show(step + 1, { playCue: true }),
  prev: () => show(step - 1, { playCue: false }),
  restart,
};

document.querySelectorAll("[data-action]").forEach((el) => {
  const action = actions[el.dataset.action];
  if (!action) return; // full screen is handled in projector.js
  el.addEventListener("click", (event) => {
    event.stopPropagation(); // don't also count as a click on the page
    Sound.wake();
    action();
    el.blur();
  });
});

// Clicking anywhere on the title card starts the story.
room.addEventListener("click", () => {
  if (step < 0) play();
});

document.addEventListener("keydown", (event) => {
  if (isShortcut(event)) return;
  const key = event.key.toLowerCase();
  if (key === " ") toggle();
  else if (key === "arrowright") actions.next();
  else if (key === "arrowleft") actions.prev();
  else if (key === "r") restart();
  else if (key === "b") location.href = document.getElementById("backdrop-link").href;
  else return;
  event.preventDefault();
});

room.addEventListener("animationend", (event) => {
  if (event.animationName === "flash") room.classList.remove("flash");
});
