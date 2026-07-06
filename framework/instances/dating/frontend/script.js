const $ = (id) => document.getElementById(id);

let selectedProfilePhoto = localStorage.getItem("datingProfilePhoto") || "";

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const message = data?.detail || data?.message || `Erro HTTP ${response.status}`;
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }

  return data;
}

function csvToList(value) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function profilePayload() {
  return {
    email: $("email").value.trim(),
    name: $("name").value.trim(),
    age: Number($("age").value),
    city: $("city").value.trim(),
    bio: $("bio").value.trim(),
    interests: csvToList($("interests").value),
    hobbies: csvToList($("hobbies").value),
    preferences: csvToList($("preferences").value),
    lifestyle: $("lifestyle").value.trim(),
    photo_url: selectedProfilePhoto,
  };
}

function setupHomePage() {
  const heroSearch = $("hero-search");
  if (!heroSearch) return;

  heroSearch.addEventListener("submit", (event) => {
    event.preventDefault();
    const query = $("hero-query").value.trim();
    const url = query
      ? `/descobrir.html?query=${encodeURIComponent(query)}`
      : "/descobrir.html";
    window.location.href = url;
  });
}

function setupProfilePage() {
  const profileForm = $("profile-form");
  const statusBox = $("profile-status");
  const photoInput = $("photo");

  if (!profileForm || !statusBox) return;

  hydratePreview();

  ["name", "age", "city", "bio", "interests", "lifestyle"].forEach((id) => {
    const field = $(id);
    if (field) field.addEventListener("input", updateProfilePreview);
  });

  if (photoInput) {
    photoInput.addEventListener("change", async () => {
      const file = photoInput.files?.[0];
      if (!file) return;

      try {
        selectedProfilePhoto = await resizeImageToDataUrl(file, 900);
        localStorage.setItem("datingProfilePhoto", selectedProfilePhoto);
        updateProfilePreview();
        showToast({
          title: "Foto carregada",
          message: "Sua foto já aparece no preview do perfil.",
          primaryText: "Fechar",
        });
      } catch (error) {
        showToast({
          title: "Erro ao carregar foto",
          message: error.message,
          primaryText: "Entendi",
        });
      }
    });
  }

  profileForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    statusBox.innerHTML = `<p class="muted">Salvando perfil...</p>`;

    try {
      const user = await request("/user", {
        method: "POST",
        body: JSON.stringify(profilePayload()),
      });

      statusBox.innerHTML = `
        <p class="success">Perfil criado/atualizado com sucesso.</p>
        <p><strong>${user.name}</strong> — ${user.age} anos, ${user.city}, estilo ${user.lifestyle}</p>
      `;

      showToast({
        title: "Perfil salvo com sucesso",
        message: "Agora você pode descobrir pessoas compatíveis com esse perfil.",
        primaryText: "Ir para Descobrir",
        secondaryText: "Continuar editando",
        onPrimary: () => {
          window.location.href = "/descobrir.html?query=pessoas%20que%20gostam%20de%20praia%20e%20praticam%20esportes";
        },
      });
    } catch (error) {
      statusBox.innerHTML = `<p class="error">${error.message}</p>`;
    }
  });
}

function hydratePreview() {
  if (selectedProfilePhoto) updateProfilePreview();
}

function updateProfilePreview() {
  const card = $("profile-preview-card");
  const namePreview = $("preview-name");
  const bioPreview = $("preview-bio");
  const tagsPreview = $("preview-tags");

  if (!card || !namePreview || !bioPreview || !tagsPreview) return;

  const name = $("name")?.value?.trim() || "Lucas";
  const age = $("age")?.value?.trim() || "23";
  const city = $("city")?.value?.trim() || "Natal";
  const bio = $("bio")?.value?.trim() || "Praia, tecnologia, filmes e rolês tranquilos.";
  const lifestyle = $("lifestyle")?.value?.trim() || "ao ar livre";
  const interests = csvToList($("interests")?.value || "filmes, tecnologia").slice(0, 3);

  namePreview.textContent = `${name}, ${age}`;
  bioPreview.textContent = bio;
  tagsPreview.innerHTML = [city, lifestyle, ...interests]
    .filter(Boolean)
    .slice(0, 5)
    .map((tag) => `<span>${tag}</span>`)
    .join("");

  if (selectedProfilePhoto) {
    card.style.backgroundImage = `
      linear-gradient(180deg, rgba(15,23,42,.04), rgba(51,16,26,.86)),
      url("${selectedProfilePhoto}")
    `;
  }
}

function resizeImageToDataUrl(file, maxSize = 900) {
  return new Promise((resolve, reject) => {
    if (!file.type.startsWith("image/")) {
      reject(new Error("Selecione um arquivo de imagem."));
      return;
    }

    const reader = new FileReader();

    reader.onload = () => {
      const img = new Image();

      img.onload = () => {
        const scale = Math.min(1, maxSize / Math.max(img.width, img.height));
        const width = Math.round(img.width * scale);
        const height = Math.round(img.height * scale);

        const canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = height;

        const context = canvas.getContext("2d");
        context.drawImage(img, 0, 0, width, height);

        resolve(canvas.toDataURL("image/jpeg", 0.82));
      };

      img.onerror = () => reject(new Error("Não foi possível processar a imagem."));
      img.src = reader.result;
    };

    reader.onerror = () => reject(new Error("Não foi possível ler a imagem."));
    reader.readAsDataURL(file);
  });
}

function setupDiscoverPage() {
  const searchForm = $("search-form");
  const queryInput = $("query");

  if (!searchForm || !queryInput) return;

  const params = new URLSearchParams(window.location.search);
  const queryParam = params.get("query");

  if (queryParam) {
    queryInput.value = queryParam;
  }

  document.querySelectorAll("[data-query]").forEach((button) => {
    button.addEventListener("click", () => {
      queryInput.value = button.dataset.query;
      searchProfiles();
    });
  });

  searchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    searchProfiles();
  });

  searchProfiles();
}

function setupMatchesPage() {
  const loadButton = $("load-matches");
  if (!loadButton) return;

  loadButton.addEventListener("click", loadMatches);
  loadMatches();
}

async function searchProfiles() {
  const queryInput = $("query");
  const resultsBox = $("results");

  if (!queryInput || !resultsBox) return;

  const query = queryInput.value.trim();
  if (!query) return;

  resultsBox.innerHTML = `<div class="profile-card profile-card--loading"><p class="muted">Buscando perfis compatíveis...</p></div>`;

  try {
    const profiles = await request("/search", {
      method: "POST",
      body: JSON.stringify({ query }),
    });

    renderProfiles(profiles);
  } catch (error) {
    resultsBox.innerHTML = `<div class="profile-card"><p class="error">${error.message}</p></div>`;
  }
}

function renderProfiles(profiles) {
  const resultsBox = $("results");
  if (!resultsBox) return;

  if (!profiles.length) {
    resultsBox.innerHTML = `<div class="profile-card"><p class="muted">Nenhum perfil encontrado.</p></div>`;
    return;
  }

  resultsBox.innerHTML = profiles.map(profileCard).join("");

  resultsBox.querySelectorAll("[data-like]").forEach((button) => {
    button.addEventListener("click", () => interactProfile(button.dataset.like, "like"));
  });

  resultsBox.querySelectorAll("[data-skip]").forEach((button) => {
    button.addEventListener("click", () => interactProfile(button.dataset.skip, "skip"));
  });

  resultsBox.querySelectorAll("[data-save]").forEach((button) => {
    button.addEventListener("click", () => interactProfile(button.dataset.save, "save"));
  });
}

function profileCard(profile) {
  const tags = [...(profile.interests || []), ...(profile.hobbies || [])].slice(0, 6);
  const matchText = profile.match_score ?? "crie perfil";
  const photoStyle = profile.photo_url
    ? `style="background-image: linear-gradient(180deg, rgba(15, 23, 42, 0.04), rgba(51, 16, 26, 0.82)), url('${profile.photo_url}')"`
    : "";

  return `
    <article class="profile-card">
      <div class="profile-photo" ${photoStyle}>
        <span class="score-pill">Match: ${matchText}${typeof profile.match_score === "number" ? "%" : ""}</span>
      </div>
      <div class="profile-card__body">
        <div class="profile-card__top">
          <div>
            <h3>${profile.name}, ${profile.age}</h3>
            <p class="muted">${profile.city} • ${profile.lifestyle}</p>
          </div>
        </div>
        <p>${profile.bio}</p>
        <div class="profile-tags">
          ${tags.map((tag) => `<span>${tag}</span>`).join("")}
        </div>
        <div class="card-actions">
          <button class="btn btn--ghost" type="button" data-skip="${profile.id}">${profile.skipped ? "Passado" : "Passar"}</button>
          <button class="btn btn--ghost" type="button" data-save="${profile.id}">${profile.saved ? "Salvo" : "Salvar"}</button>
          <button class="btn" type="button" data-like="${profile.id}">${profile.liked ? "Curtido" : "Curtir"}</button>
        </div>
      </div>
    </article>
  `;
}

async function interactProfile(profileId, action) {
  const resultsBox = $("results");

  try {
    await request(`/profiles/${profileId}/${action}`, { method: "POST" });
    await searchProfiles();

    if (action === "like") {
      showToast({
        title: "Perfil curtido!",
        message: "Esse perfil foi adicionado aos seus compatíveis. Deseja ver seus matches agora?",
        primaryText: "Ver matches",
        secondaryText: "Continuar descobrindo",
        onPrimary: () => {
          window.location.href = "/matches.html";
        },
      });
    }

    if (action === "save") {
      showToast({
        title: "Perfil salvo",
        message: "Você pode encontrar esse perfil depois na tela de Matches.",
        primaryText: "Ver salvos",
        secondaryText: "Continuar",
        onPrimary: () => {
          window.location.href = "/matches.html";
        },
      });
    }
  } catch (error) {
    if (resultsBox) {
      resultsBox.insertAdjacentHTML("afterbegin", `<p class="error">${error.message}</p>`);
    }
  }
}

async function loadMatches() {
  const likedBox = $("liked-results");
  const savedBox = $("saved-results");

  if (!likedBox || !savedBox) return;

  likedBox.innerHTML = `<p class="muted">Carregando compatíveis...</p>`;
  savedBox.innerHTML = `<p class="muted">Carregando salvos...</p>`;

  try {
    const data = await request("/matches");
    likedBox.innerHTML = renderMiniList(data.liked, "Nenhum match ainda.");
    savedBox.innerHTML = renderMiniList(data.saved, "Nenhum perfil salvo ainda.");
  } catch (error) {
    likedBox.innerHTML = `<p class="error">${error.message}</p>`;
    savedBox.innerHTML = "";
  }
}

function renderMiniList(items, emptyMessage) {
  if (!items.length) return `<p class="muted">${emptyMessage}</p>`;

  return items.map((item) => `
    <article class="mini-card">
      <div class="mini-avatar" style="background-image: url('${item.photo_url || ""}')"></div>
      <div>
        <strong>${item.name}, ${item.age}</strong>
        <span>${item.city} • match ${item.match_score ?? "sem perfil"}${typeof item.match_score === "number" ? "%" : ""}</span>
        <p>${item.bio || ""}</p>
      </div>
    </article>
  `).join("");
}

function showToast({ title, message, primaryText = "Ok", secondaryText = "", onPrimary = null }) {
  document.querySelectorAll(".app-modal").forEach((modal) => modal.remove());

  const modal = document.createElement("div");
  modal.className = "app-modal";
  modal.innerHTML = `
    <div class="app-modal__backdrop"></div>
    <section class="app-modal__card" role="dialog" aria-modal="true">
      <div class="app-modal__icon">♥</div>
      <h2>${title}</h2>
      <p>${message}</p>
      <div class="app-modal__actions">
        ${secondaryText ? `<button class="btn btn--ghost" type="button" data-close>${secondaryText}</button>` : ""}
        <button class="btn" type="button" data-primary>${primaryText}</button>
      </div>
    </section>
  `;

  document.body.appendChild(modal);

  modal.querySelector("[data-close]")?.addEventListener("click", () => modal.remove());

  modal.querySelector(".app-modal__backdrop")?.addEventListener("click", () => modal.remove());

  modal.querySelector("[data-primary]")?.addEventListener("click", () => {
    modal.remove();
    if (typeof onPrimary === "function") onPrimary();
  });
}

setupHomePage();
setupProfilePage();
setupDiscoverPage();
setupMatchesPage();
