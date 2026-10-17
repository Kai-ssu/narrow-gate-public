// Sound effects synthesized with the Web Audio API, so there are no audio files
// to host or license. Browsers only allow sound after a tap, click or key press
// on the page, so call Sound.wake() from inside one before playing anything.

const Sound = (() => {
  const STORAGE_KEY = "narrow-gate-sound";
  const VOLUME = 0.6;

  let ctx = null;
  let master = null;
  let noise = null;
  let scene = null;
  let ambience = null;
  let score = null;
  let enabled = true;
  try {
    enabled = localStorage.getItem(STORAGE_KEY) !== "off";
  } catch {}

  function wake() {
    if (!ctx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      ctx = new AudioContext();
      master = ctx.createGain();
      master.gain.value = enabled ? VOLUME : 0;
      master.connect(ctx.destination);
      // Two seconds of white noise, shared by every noisy effect.
      noise = ctx.createBuffer(1, ctx.sampleRate * 2, ctx.sampleRate);
      const data = noise.getChannelData(0);
      for (let i = 0; i < data.length; i++) data[i] = Math.random() * 2 - 1;
    }
    if (ctx.state === "suspended") ctx.resume();
  }

  function setEnabled(on) {
    enabled = on;
    try {
      localStorage.setItem(STORAGE_KEY, on ? "on" : "off");
    } catch {}
    if (master) master.gain.setTargetAtTime(on ? VOLUME : 0, ctx.currentTime, 0.05);
  }

  // ---- Building blocks ----

  // Attack / hold / release volume envelope; returns the time it ends.
  function envelope(gain, t, peak, attack, hold, release) {
    gain.setValueAtTime(0.0001, t);
    gain.exponentialRampToValueAtTime(peak, t + attack);
    gain.setValueAtTime(peak, t + attack + hold);
    gain.exponentialRampToValueAtTime(0.0001, t + attack + hold + release);
    return t + attack + hold + release;
  }

  function tone(out, t, freq, { type = "sine", peak = 0.3, attack = 0.01, hold = 0, release = 0.3, to } = {}) {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, t);
    if (to) osc.frequency.exponentialRampToValueAtTime(to, t + attack + hold + release);
    osc.connect(gain).connect(out);
    const end = envelope(gain.gain, t, peak, attack, hold, release);
    osc.start(t);
    osc.stop(end + 0.05);
  }

  function hiss(out, t, { filter = "bandpass", freq = 1000, to, q = 1, peak = 0.3, attack = 0.005, hold = 0, release = 0.2 } = {}) {
    const src = ctx.createBufferSource();
    src.buffer = noise;
    src.loop = true;
    const shape = ctx.createBiquadFilter();
    shape.type = filter;
    shape.frequency.setValueAtTime(freq, t);
    shape.Q.value = q;
    if (to) shape.frequency.exponentialRampToValueAtTime(to, t + attack + hold + release);
    const gain = ctx.createGain();
    src.connect(shape).connect(gain).connect(out);
    const end = envelope(gain.gain, t, peak, attack, hold, release);
    src.start(t, Math.random() * 1.5);
    src.stop(end + 0.05);
  }

  // ---- Effects ----

  const effects = {
    // Key turning twice, then the shackle springing open.
    padlock(out, t) {
      hiss(out, t, { freq: 2600, q: 8, peak: 0.25, release: 0.04 });
      hiss(out, t + 0.12, { freq: 1900, q: 8, peak: 0.25, release: 0.05 });
      tone(out, t + 0.25, 140, { type: "triangle", peak: 0.35, release: 0.25, to: 90 });
      hiss(out, t + 0.25, { filter: "lowpass", freq: 600, peak: 0.3, release: 0.12 });
      tone(out, t + 0.3, 1320, { peak: 0.12, release: 0.6 });
      tone(out, t + 0.3, 1980, { peak: 0.06, release: 0.4 });
    },

    // A heavy cell door slamming shut, echoing off stone.
    slam(out, t) {
      tone(out, t, 70, { peak: 0.7, release: 0.9, to: 40 });
      hiss(out, t, { filter: "lowpass", freq: 900, to: 150, peak: 0.6, release: 0.5 });
      hiss(out, t + 0.05, { filter: "lowpass", freq: 300, peak: 0.15, attack: 0.05, release: 1.6 });
    },

    // The opening line of the Old Hundredth, a hymn tune from 1551.
    hymn(out, t) {
      const notes = [[392, 1], [392, 1], [370, 1], [330, 1], [294, 1], [392, 1], [440, 1], [494, 2]];
      let at = t;
      for (const [freq, beats] of notes) {
        const length = 0.42 * beats;
        tone(out, at, freq, { type: "triangle", peak: 0.13, attack: 0.08, hold: length - 0.1, release: 0.35 });
        tone(out, at, freq / 2, { peak: 0.07, attack: 0.08, hold: length - 0.1, release: 0.35 });
        at += length;
      }
    },

    // Deep rumble with stones rattling.
    quake(out, t) {
      const length = 1.8;
      hiss(out, t, { filter: "lowpass", freq: 2000, to: 200, peak: 0.5, release: 0.3 });
      hiss(out, t, { filter: "lowpass", freq: 140, q: 0.7, peak: 0.9, attack: 0.15, hold: length - 0.6, release: 0.6 });
      tone(out, t, 38, { peak: 0.6, attack: 0.15, hold: length - 0.6, release: 0.6, to: 30 });
      for (let i = 0; i < 14; i++) {
        hiss(out, t + Math.random() * length * 0.8, {
          freq: 2000 + Math.random() * 3000,
          q: 4,
          peak: 0.08 + Math.random() * 0.08,
          release: 0.03,
        });
      }
    },

    // A torch flaring to life and crackling.
    torch(out, t) {
      hiss(out, t, { freq: 300, to: 2000, q: 1.2, peak: 0.35, attack: 0.3, release: 0.5 });
      for (let i = 0; i < 10; i++) {
        hiss(out, t + 0.2 + Math.random() * 1.2, { freq: 3000, q: 2, peak: 0.15, release: 0.02 });
      }
    },

    // Prison doors creaking open onto a bright major chord.
    doors(out, t) {
      const creak = ctx.createOscillator();
      const wobble = ctx.createOscillator();
      const wobbleDepth = ctx.createGain();
      const shape = ctx.createBiquadFilter();
      const gain = ctx.createGain();
      creak.type = "sawtooth";
      creak.frequency.setValueAtTime(80, t);
      creak.frequency.exponentialRampToValueAtTime(130, t + 1.1);
      wobble.frequency.value = 9;
      wobbleDepth.gain.value = 6;
      wobble.connect(wobbleDepth).connect(creak.frequency);
      shape.type = "bandpass";
      shape.frequency.value = 900;
      shape.Q.value = 3;
      creak.connect(shape).connect(gain).connect(out);
      const end = envelope(gain.gain, t, 0.12, 0.1, 0.8, 0.3);
      creak.start(t);
      wobble.start(t);
      creak.stop(end);
      wobble.stop(end);
      for (const freq of [262, 330, 392, 523]) {
        tone(out, t + 1.2, freq, { peak: 0.08, attack: 0.6, hold: 0.8, release: 1.6 });
      }
    },

    // Dull thud for a wrong code.
    wrong(out, t) {
      tone(out, t, 120, { type: "triangle", peak: 0.4, release: 0.25, to: 80 });
      tone(out, t + 0.18, 100, { type: "triangle", peak: 0.35, release: 0.35, to: 70 });
      hiss(out, t, { filter: "lowpass", freq: 400, peak: 0.2, release: 0.1 });
    },

    // Paper strip being turned over.
    flip(out, t) {
      hiss(out, t, { filter: "highpass", freq: 3000, q: 0.7, peak: 0.18, release: 0.06 });
      hiss(out, t + 0.04, { freq: 1500, peak: 0.1, release: 0.05 });
    },

    // Three slow tolls of a bell when time runs out.
    bell(out, t) {
      for (let toll = 0; toll < 3; toll++) {
        const at = t + toll * 2.2;
        for (const [freq, peak] of [[220, 0.5], [440, 0.3], [554, 0.15], [660, 0.12], [880, 0.08]]) {
          tone(out, at, freq, { peak: peak * 0.6, attack: 0.005, release: 4 });
        }
      }
    },

    // An angry crowd building up (story: the marketplace).
    crowd(out, t) {
      for (let i = 0; i < 7; i++) {
        hiss(out, t + Math.random() * 0.8, {
          freq: 300 + Math.random() * 600,
          q: 5,
          peak: 0.07,
          attack: 0.8,
          hold: 2.2 + Math.random(),
          release: 1.5,
        });
      }
      hiss(out, t, { filter: "lowpass", freq: 400, peak: 0.15, attack: 1, hold: 2.5, release: 1.5 });
    },

    // One blow of a rod (story: the beating).
    strike(out, t) {
      hiss(out, t, { filter: "highpass", freq: 1500, peak: 0.5, release: 0.08 });
      tone(out, t, 90, { peak: 0.5, release: 0.25, to: 50 });
    },

    // A scroll unrolling: a run of paper rustles (The Secret of Susa).
    unroll(out, t) {
      for (let i = 0; i < 6; i++) {
        hiss(out, t + i * 0.13, { filter: "highpass", freq: 2500 + i * 200, q: 0.7, peak: 0.12, release: 0.08 });
      }
      hiss(out, t + 0.8, { filter: "lowpass", freq: 500, peak: 0.2, release: 0.1 });
    },

    // Soft high chimes, like stars coming out (The Secret of Susa: the sleepless night).
    chime(out, t) {
      [1568, 1319, 1175, 1568, 1760].forEach((freq, i) => {
        tone(out, t + i * 0.28, freq, { peak: 0.06, release: 1.6 });
        tone(out, t + i * 0.28, freq * 2, { peak: 0.015, release: 0.8 });
      });
    },

    // A wax seal pressed onto a decree, then a bright chord (The Secret of Susa).
    stamp(out, t) {
      tone(out, t, 110, { type: "triangle", peak: 0.5, release: 0.3, to: 60 });
      hiss(out, t, { filter: "lowpass", freq: 700, peak: 0.35, release: 0.15 });
      for (const freq of [294, 370, 440, 587]) {
        tone(out, t + 0.35, freq, { type: "triangle", peak: 0.05, attack: 0.3, hold: 0.6, release: 1.4 });
      }
    },

    // Fingers scratching words into plaster, one burst per word (The Writing on the Wall).
    scrawl(out, t) {
      for (let word = 0; word < 4; word++) {
        for (let i = 0; i < 5; i++) {
          hiss(out, t + word * 0.5 + i * 0.07, { freq: 1800 + Math.random() * 1200, q: 3, peak: 0.08, release: 0.05 });
        }
      }
      tone(out, t + 2.1, 73, { type: "triangle", peak: 0.25, attack: 0.4, hold: 0.6, release: 1.2 });
    },

    // A slow, rising chord (story: the closing line).
    swell(out, t) {
      for (const freq of [147, 220, 294, 349]) {
        tone(out, t, freq, { type: "triangle", peak: 0.06, attack: 2.5, hold: 0.8, release: 2.5 });
      }
    },
  };

  // Which effects go with each unlock scene, and when (seconds after it starts).
  // Timings match the animations in style.css.
  const scenes = {
    dark: [["slam", 0.15]],
    songs: [["padlock", 0.45], ["hymn", 1.5]],
    quake: [["padlock", 0.45], ["quake", 1.5]],
    torch: [["padlock", 0.45], ["torch", 1.5]],
    doors: [["padlock", 0.45], ["doors", 1.7]],
    scroll: [["padlock", 0.45], ["unroll", 1.6]],
    night: [["padlock", 0.45], ["chime", 1.6]],
    seal: [["padlock", 0.45], ["stamp", 2.0]],
    writing: [["padlock", 0.45], ["scrawl", 1.7]],
  };

  const ready = () => ctx !== null && enabled;

  function play(name) {
    if (!ready()) return;
    effects[name](master, ctx.currentTime + 0.02);
  }

  function playScene(name) {
    if (!ready() || !scenes[name]) return;
    stopScene();
    scene = ctx.createGain();
    scene.connect(master);
    const start = ctx.currentTime + 0.02;
    for (const [effect, at] of scenes[name]) effects[effect](scene, start + at);
  }

  // Fade out the current scene's sounds (when a player skips the animation).
  function stopScene() {
    if (!scene) return;
    const old = scene;
    old.gain.setTargetAtTime(0, ctx.currentTime, 0.08);
    setTimeout(() => old.disconnect(), 1000);
    scene = null;
  }

  // A looping background bed that fades in, runs until stopped, then fades out.
  // build(out, later) connects its sounds to `out`, can schedule repeating extras
  // with later(fn, ms), and returns the sources to stop at the end.
  function startBed(build) {
    const out = ctx.createGain();
    out.gain.value = 0;
    out.gain.setTargetAtTime(1, ctx.currentTime, 1.5);
    out.connect(master);
    const timers = new Set();
    const later = (fn, ms) => {
      const id = setTimeout(() => {
        timers.delete(id);
        fn();
      }, ms);
      timers.add(id);
    };
    const sources = build(out, later);
    return {
      stop() {
        timers.forEach(clearTimeout);
        out.gain.setTargetAtTime(0, ctx.currentTime, 0.4);
        setTimeout(() => {
          sources.forEach((source) => source.stop());
          out.disconnect();
        }, 2500);
      },
    };
  }

  // Backdrop ambience: a low, steady drone with torch crackle, plus the room's own
  // touch: water drips in the prison cell, or a few plucked strings in the palace.
  // (Kept nearly flat: a slow swell sounds like ocean waves.)
  function startAmbience() {
    if (!ready() || ambience) return;
    ambience = startBed((out, later) => {
      const drone = ctx.createBufferSource();
      drone.buffer = noise;
      drone.loop = true;
      const low = ctx.createBiquadFilter();
      low.type = "lowpass";
      low.frequency.value = 110;
      const droneGain = ctx.createGain();
      droneGain.gain.value = 0.12;
      drone.connect(low).connect(droneGain).connect(out);
      drone.start();

      const crackle = () => {
        hiss(out, ctx.currentTime, { freq: 2500 + Math.random() * 2500, q: 3, peak: 0.03 + Math.random() * 0.05, release: 0.02 });
        later(crackle, 40 + Math.random() * 260);
      };
      const drip = () => {
        const freq = 900 + Math.random() * 600;
        tone(out, ctx.currentTime, freq, { peak: 0.06, release: 0.09, to: freq * 1.8 });
        later(drip, 3000 + Math.random() * 7000);
      };
      // A short phrase on a lyre in D with a raised third (D Eb F# G A Bb C D),
      // a scale that gives an old Near Eastern sound.
      const SCALE = [294, 311, 370, 392, 440, 466, 523, 587];
      const pluck = () => {
        let step = Math.floor(Math.random() * 5);
        const notes = 2 + Math.floor(Math.random() * 3);
        for (let i = 0; i < notes; i++) {
          const freq = SCALE[step];
          const at = ctx.currentTime + i * (0.35 + Math.random() * 0.25);
          tone(out, at, freq, { type: "triangle", peak: 0.045, attack: 0.005, release: 1.4 });
          tone(out, at, freq * 2, { peak: 0.012, attack: 0.005, release: 0.6 });
          step = Math.max(0, Math.min(SCALE.length - 1, step + (Math.random() < 0.5 ? -1 : 1)));
        }
        later(pluck, 5000 + Math.random() * 7000);
      };
      crackle();
      if (document.body.dataset.room === "palace") later(pluck, 2500);
      else later(drip, 2000);
      return [drone];
    });
  }

  function stopAmbience() {
    ambience?.stop();
    ambience = null;
  }

  // Music bed for the story: a dark D minor drone with a slow heartbeat.
  function startScore() {
    if (!ready() || score) return;
    score = startBed((out, later) => {
      const low = ctx.createBiquadFilter();
      low.type = "lowpass";
      low.frequency.value = 650;
      low.connect(out);
      const voices = [73.4, 110, 146.8, 174.6].map((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = i === 0 ? "sawtooth" : "triangle";
        osc.frequency.value = freq;
        osc.detune.value = (Math.random() - 0.5) * 8;
        gain.gain.value = i === 0 ? 0.035 : 0.05;
        osc.connect(gain).connect(low);
        osc.start();
        return osc;
      });
      const heartbeat = () => {
        const t = ctx.currentTime;
        tone(out, t, 55, { peak: 0.18, release: 0.3, to: 40 });
        tone(out, t + 0.28, 50, { peak: 0.12, release: 0.3, to: 38 });
        later(heartbeat, 2400);
      };
      later(heartbeat, 1500);
      return voices;
    });
  }

  function stopScore() {
    score?.stop();
    score = null;
  }

  return {
    wake,
    play,
    playScene,
    stopScene,
    startAmbience,
    stopAmbience,
    startScore,
    stopScore,
    setEnabled,
    get enabled() {
      return enabled;
    },
  };
})();
