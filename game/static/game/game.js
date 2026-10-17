// Player pages.
//
// Forms marked data-swap (Begin and the code locks) are sent in the background
// and the next page is swapped in without a reload. That keeps the player's tap
// "active", which phones require before they allow the unlock sounds to play.
// Without JavaScript the forms still work as ordinary page loads.

let countdown = null;

function init() {
  // Countdown timer: the deadline (unix seconds) comes from the server.
  clearInterval(countdown);
  const timer = document.querySelector(".timer");
  if (timer) {
    const deadline = Number(timer.dataset.deadline) * 1000;
    const tick = () => {
      const left = Math.max(0, Math.round((deadline - Date.now()) / 1000));
      const m = Math.floor(left / 60);
      const s = String(left % 60).padStart(2, "0");
      timer.textContent = left > 0 ? `${m}:${s}` : "Time's up";
      timer.classList.toggle("low", left < 5 * 60);
      if (left === 0) document.querySelector(".time-up")?.removeAttribute("hidden");
    };
    tick();
    countdown = setInterval(tick, 1000);
  }

  // Unlock scene and its sounds: tap anywhere to skip; remove it once it has faded out.
  const entrance = document.querySelector(".entrance");
  if (entrance) {
    Sound.playScene(entrance.dataset.scene);
    entrance.addEventListener("click", () => {
      entrance.remove();
      Sound.stopScene();
    });
    entrance.addEventListener("animationend", (event) => {
      if (event.animationName === "entrance-out") entrance.remove();
    });
  }

  if (document.querySelector(".lock .error")) Sound.play("wrong");

  document.querySelectorAll("form[data-swap]").forEach((form) => {
    form.addEventListener("submit", submitInPlace);
  });

  // Ask before submitting forms that wipe progress.
  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
  });

  // Stage 3: tap a strip to turn it over.
  document.querySelectorAll(".strip").forEach((strip) => {
    strip.addEventListener("click", () => {
      Sound.wake();
      Sound.play("flip");
      strip.classList.toggle("flipped");
    });
  });

  // NIV / NKJV switch: one choice for the whole game, remembered on this device.
  const bible = document.documentElement.dataset.bible || "niv";
  document.querySelectorAll("[data-bible-pick]").forEach((pick) => {
    pick.setAttribute("aria-checked", String(pick.dataset.biblePick === bible));
    pick.addEventListener("click", () => {
      document.documentElement.dataset.bible = pick.dataset.biblePick;
      try {
        localStorage.setItem("narrow-gate-bible", pick.dataset.biblePick);
      } catch {}
      document.querySelectorAll("[data-bible-pick]").forEach((other) => {
        other.setAttribute("aria-checked", String(other === pick));
      });
    });
  });

  // Sound on/off button in the header.
  const toggle = document.querySelector(".sound-toggle");
  if (toggle) {
    const sync = () => toggle.setAttribute("aria-pressed", String(Sound.enabled));
    sync();
    toggle.addEventListener("click", () => {
      Sound.wake();
      Sound.setEnabled(!Sound.enabled);
      sync();
    });
  }
}

async function submitInPlace(event) {
  event.preventDefault();
  const form = event.currentTarget;
  Sound.wake(); // inside the tap, so the browser allows audio
  const button = form.querySelector('[type="submit"]');
  if (button) button.disabled = true;
  try {
    const response = await fetch(form.action, {
      method: "POST",
      body: new FormData(form),
      credentials: "same-origin",
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    swapPage(await response.text(), response.url);
  } catch {
    form.submit(); // fall back to a normal page load
  }
}

function swapPage(html, url) {
  const next = new DOMParser().parseFromString(html, "text/html");
  document.title = next.title;
  document.body.replaceWith(next.body);
  if (url !== location.href) {
    history.pushState(null, "", url);
    window.scrollTo(0, 0);
  }
  init();
}

// Back/forward after a swap: load the page fresh from the server.
window.addEventListener("popstate", () => location.reload());

init();
