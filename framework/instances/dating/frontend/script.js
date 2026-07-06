const profileForm = document.getElementById("profile-form");
const searchForm = document.getElementById("search-form");
const heroSearch = document.getElementById("hero-search");
const statusBox = document.getElementById("profile-status");
const resultsBox = document.getElementById("results");
const likedBox = document.getElementById("liked-results");
const savedBox = document.getElementById("saved-results");

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
    email: document.getElementById("email").value.trim(),
    name: document.getElementById("name").value.trim(),
    age: Number(document.getElementById("age").value),
    city: document.getElementById("city").value.trim(),
    bio: document.getElementById("bio").value.trim(),
    interests: csvToList(document.getElementById("interests").value),
    hobbies: csvToList(document.getElementById("hobbies").value),
    preferences: csvToList(document.getElementById("preferences").value),
    lifestyle: document.getElementById("lifestyle").value.trim(),
  };
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

    document.getElementById("descobrir").scrollIntoView({ behavior: "smooth" });
    await searchProfiles();
    await loadMatches();
  } catch (error) {
    statusBox.innerHTML = `<p class="error">${error.message}</p>`;
  }
});

document.querySelectorAll("[data-query]").forEach((button) => {
  button.addEventListener("click", () => {
    document.getElementById("query").value = button.dataset.query;
    searchProfiles();
  });
});

heroSearch.addEventListener("submit", (event) => {
  event.preventDefault();
  document.getElementById("query").value = document.getElementById("hero-query").value;
  document.getElementById("descobrir").scrollIntoView({ behavior: "smooth" });
  searchProfiles();
});

searchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  searchProfiles();
});

document.getElementById("load-matches").addEventListener("click", loadMatches);

async function searchProfiles() {
  const query = document.getElementById("query").value.trim();
  if (!query) return;

  resultsBox.innerHTML = `<div class="profile-card"><p class="muted">Buscando perfis...</p></div>`;

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
  const tags = [...(profile.interests || []), ...(profile.hobbies || [])].slice(0, 5);
  const matchText = profile.match_score ?? "crie um perfil";
  const photoStyle = profile.photo_url ? `style="background-image: url('${profile.photo_url}')"` : "";

  return `
    <article class="profile-card">
      <div class="profile-photo" ${photoStyle}></div>
      <div class="profile-card__body">
        <div class="profile-card__top">
          <div>
            <h3>${profile.name}, ${profile.age}</h3>
            <p class="muted">${profile.city} • ${profile.lifestyle}</p>
          </div>
          <span class="score-pill">Match: ${matchText}</span>
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
  try {
    await request(`/profiles/${profileId}/${action}`, { method: "POST" });
    await searchProfiles();
    await loadMatches();
  } catch (error) {
    resultsBox.insertAdjacentHTML("afterbegin", `<p class="error">${error.message}</p>`);
  }
}

async function loadMatches() {
  likedBox.innerHTML = `<p class="muted">Carregando...</p>`;
  savedBox.innerHTML = `<p class="muted">Carregando...</p>`;

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
      <strong>${item.name}, ${item.age}</strong>
      <span>${item.city} • match ${item.match_score ?? "sem perfil"}</span>
    </article>
  `).join("");
}

searchProfiles();
loadMatches();
