
(() => {
  const TOTAL = 75;
  const SCENES = [
    { start: 0,  end: 6,  title: "Le cahier" },
    { start: 6,  end: 14, title: "Le désordre" },
    { start: 14, end: 20, title: "Le constat" },
    { start: 20, end: 26, title: "Le clic" },
    { start: 26, end: 38, title: "Le rangement" },
    { start: 38, end: 44, title: "La donnée" },
    { start: 44, end: 50, title: "L'ancrage" },
    { start: 50, end: 75, title: "Le produit" }
  ];

  const stage = document.getElementById("stage");
  const scenes = [...document.querySelectorAll(".scene")];
  const playBtn = document.getElementById("playBtn");
  const playIcon = document.getElementById("playIcon");
  const replayBtn = document.getElementById("replayBtn");
  const progress = document.getElementById("progress");
  const progressWrap = document.getElementById("progressWrap");
  const timeEl = document.getElementById("time");
  const sceneName = document.getElementById("sceneName");
  const chapters = document.getElementById("chapters");
  const vo = document.getElementById("voAudio");
  const voBtn = document.getElementById("voBtn");
  let pendingAudioTime = 0;

  let elapsed = 0;
  let playing = false;
  let raf = null;
  let lastTs = null;
  let activeIndex = -1;
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const clamp = (v, min, max) => Math.max(min, Math.min(max, v));
  const mmss = (v) => {
    const t = Math.max(0, Math.min(TOTAL, v));
    return `${String(Math.floor(t / 60)).padStart(2, "0")}:${String(Math.floor(t % 60)).padStart(2, "0")}`;
  };

  function setAudioTime(value, force = false) {
    const target = clamp(value, 0, TOTAL);
    pendingAudioTime = target;
    if (!vo || vo.readyState < 1) return;
    if (force || Math.abs(vo.currentTime - target) > 0.15) {
      try { vo.currentTime = target; } catch (_) {}
    }
  }

  function playAudio() {
    if (!vo) return;
    setAudioTime(elapsed, true);
    const promise = vo.play();
    if (promise && typeof promise.catch === "function") promise.catch(() => {});
  }

  function pauseAudio() {
    if (vo) vo.pause();
  }

  function updateVoButton() {
    if (!voBtn || !vo) return;
    const on = !vo.muted;
    voBtn.textContent = on ? "VO · ON" : "VO · OFF";
    voBtn.setAttribute("aria-pressed", String(on));
    voBtn.setAttribute("aria-label", on ? "Couper la voix off" : "Réactiver la voix off");
    voBtn.classList.toggle("is-off", !on);
  }

  if (vo) {
    vo.volume = 1;
    vo.addEventListener("loadedmetadata", () => {
      try {
        vo.currentTime = clamp(pendingAudioTime, 0, Math.min(TOTAL, vo.duration || TOTAL));
      } catch (_) {}
    });
    vo.addEventListener("error", () => {
      if (voBtn) {
        voBtn.disabled = true;
        voBtn.textContent = "VO indisponible";
      }
    });
  }
  if (voBtn) {
    voBtn.addEventListener("click", () => {
      if (!vo) return;
      vo.muted = !vo.muted;
      updateVoButton();
      if (!vo.muted && playing) {
        setAudioTime(elapsed, true);
        const promise = vo.play();
        if (promise && typeof promise.catch === "function") promise.catch(() => {});
      }
    });
  }
  updateVoButton();

  const indexAt = (v) => {
    if (v >= TOTAL) return SCENES.length - 1;
    for (let i = 0; i < SCENES.length; i++) {
      if (v >= SCENES[i].start && v < SCENES[i].end) return i;
    }
    return 0;
  };

  function setPlayIcon() {
    if (playing) {
      playIcon.innerHTML = '<rect x="6" y="5" width="4" height="14" rx="1"></rect><rect x="14" y="5" width="4" height="14" rx="1"></rect>';
      playBtn.setAttribute("aria-label", "Mettre en pause");
    } else {
      playIcon.innerHTML = '<path d="M8 5v14l11-7z"></path>';
      playBtn.setAttribute("aria-label", "Lire l'animatic");
    }
  }

  function syncSceneAnimations(scene, localTime) {
    if (!scene || typeof scene.getAnimations !== "function") return;
    const ms = Math.max(0, localTime) * 1000;
    scene.getAnimations({ subtree: true }).forEach((animation) => {
      if (!animation.animationName) return;
      try {
        animation.currentTime = ms;
      } catch (_) {}
    });
  }

  function setScene(index, force = false) {
    if (index === activeIndex && !force) return;
    const localTime = Math.max(0, elapsed - (SCENES[index]?.start || 0));
    scenes.forEach((scene, i) => {
      const isActive = i === index;
      scene.classList.toggle("active", isActive);
      if (isActive) syncSceneAnimations(scene, localTime);
    });
    activeIndex = index;
    sceneName.textContent = SCENES[index]?.title || "";
    [...chapters.children].forEach((chapter, i) => chapter.classList.toggle("active", i === index));
  }

  function render() {
    progress.style.width = `${(elapsed / TOTAL) * 100}%`;
    timeEl.textContent = `${mmss(elapsed)} / 01:15`;
    progressWrap.setAttribute("aria-valuenow", String(Math.round(elapsed)));
    const index = indexAt(elapsed);
    setScene(index);
    sceneName.textContent = (index === 7 && elapsed >= 68)
      ? "Le produit · signature"
      : (SCENES[index]?.title || "");
  }

  function tick(ts) {
    if (!playing) return;
    if (lastTs === null) lastTs = ts;
    const dt = Math.min(0.08, (ts - lastTs) / 1000);
    lastTs = ts;
    elapsed += dt;
    if (elapsed >= TOTAL) {
      elapsed = TOTAL;
      render();
      pause();
      return;
    }
    if (vo && !vo.paused && Math.abs(vo.currentTime - elapsed) > 0.2) {
      try { vo.currentTime = elapsed; } catch (_) {}
    }
    render();
    raf = requestAnimationFrame(tick);
  }

  function play() {
    if (elapsed >= TOTAL) reset(false);
    if (playing) return;
    playing = true;
    stage.classList.remove("paused");
    lastTs = null;
    setPlayIcon();
    raf = requestAnimationFrame(tick);
    playAudio();
  }

  function pause() {
    playing = false;
    if (raf) cancelAnimationFrame(raf);
    raf = null;
    lastTs = null;
    stage.classList.add("paused");
    setPlayIcon();
    pauseAudio();
  }

  function reset(autoPlay = false) {
    pause();
    elapsed = 0;
    setAudioTime(0, true);
    activeIndex = -1;
    scenes.forEach((scene) => scene.classList.remove("active"));
    void stage.offsetWidth;
    setScene(0, true);
    render();
    if (autoPlay) play();
  }

  function seek(value) {
    const wasPlaying = playing;
    pause();
    elapsed = clamp(value, 0, TOTAL);
    setAudioTime(elapsed, true);
    activeIndex = -1;
    scenes.forEach((scene) => scene.classList.remove("active"));
    void stage.offsetWidth;
    setScene(indexAt(elapsed), true);
    render();
    if (wasPlaying && elapsed < TOTAL) play();
  }

  function buildChapters() {
    SCENES.forEach((scene, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "chapter";
      button.innerHTML = `<b>${String(index + 1).padStart(2, "0")}</b><span>${mmss(scene.start)}</span><em>${scene.title}</em>`;
      button.addEventListener("click", () => {
        seek(scene.start);
        play();
      });
      chapters.appendChild(button);
    });
  }

  playBtn.addEventListener("click", () => {
    if (playing) pause();
    else play();
  });
  replayBtn.addEventListener("click", () => reset(true));

  progressWrap.addEventListener("click", (event) => {
    const rect = progressWrap.getBoundingClientRect();
    const ratio = clamp((event.clientX - rect.left) / rect.width, 0, 1);
    seek(ratio * TOTAL);
  });
  progressWrap.addEventListener("keydown", (event) => {
    const step = event.shiftKey ? 10 : 3;
    if (event.key === "ArrowRight") { event.preventDefault(); seek(elapsed + step); }
    if (event.key === "ArrowLeft") { event.preventDefault(); seek(elapsed - step); }
    if (event.key === "Home") { event.preventDefault(); seek(0); }
    if (event.key === "End") { event.preventDefault(); seek(TOTAL); }
  });

  document.addEventListener("keydown", (event) => {
    if (event.code === "Space" && !event.target.closest("button")) {
      event.preventDefault();
      if (playing) pause();
      else play();
    }
    if (event.key.toLowerCase() === "r" && !event.target.closest("button")) {
      reset(true);
    }
  });

  document.addEventListener("visibilitychange", () => {
    if (document.hidden && playing) pause();
  });

  buildChapters();
  stage.classList.add("paused");
  setScene(0, true);
  render();
  setPlayIcon();

  // Pour tester une scène : window.__animatic.seek(48)
  window.__animatic = {
    seek,
    play,
    pause,
    reset,
    get elapsed() { return elapsed; },
    get playing() { return playing; },
    get audio() { return vo; },
    scenes: SCENES
  };

  const params = new URLSearchParams(window.location.search);
  const initial = Number(params.get("t") || 0);
  if (Number.isFinite(initial) && initial > 0) seek(initial);
  if (params.get("pause") === "1") pause();
})();
