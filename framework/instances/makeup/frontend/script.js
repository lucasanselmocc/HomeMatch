const profileForm = document.getElementById("profile-form");
const searchForm = document.getElementById("search-form");
const heroSearch = document.getElementById("hero-search");
const statusBox = document.getElementById("profile-status");
const resultsBox = document.getElementById("results");

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

function profilePayload() {
  return {
    email: document.getElementById("email").value.trim(),
    name: document.getElementById("name").value.trim(),
    skin_type: document.getElementById("skinType").value.trim(),
    preferred_finish: document.getElementById("finish").value.trim(),
    max_price: Number(document.getElementById("maxPrice").value),
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
      <p><strong>${user.name}</strong> — pele ${user.skin_type}, acabamento ${user.preferred_finish}, até R$ ${user.max_price}</p>
    `;

    document.getElementById("busca").scrollIntoView({ behavior: "smooth" });
  } catch (error) {
    statusBox.innerHTML = `<p class="error">${error.message}</p>`;
  }
});

function setQuery(value) {
  document.getElementById("query").value = value;
}

document.querySelectorAll("[data-query]").forEach((button) => {
  button.addEventListener("click", () => setQuery(button.dataset.query));
});

heroSearch.addEventListener("submit", (event) => {
  event.preventDefault();
  document.getElementById("query").value = document.getElementById("hero-query").value;
  document.getElementById("busca").scrollIntoView({ behavior: "smooth" });
  searchProducts();
});

searchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  searchProducts();
});

async function searchProducts() {
  const query = document.getElementById("query").value.trim();
  if (!query) return;

  resultsBox.innerHTML = `<div class="product-card"><p class="muted">Buscando produtos...</p></div>`;

  try {
    const products = await request("/search", {
      method: "POST",
      body: JSON.stringify({ query }),
    });

    renderResults(products);
  } catch (error) {
    resultsBox.innerHTML = `<div class="product-card"><p class="error">${error.message}</p></div>`;
  }
}

function renderResults(products) {
  if (!products.length) {
    resultsBox.innerHTML = `<div class="product-card"><p class="muted">Nenhum produto encontrado.</p></div>`;
    return;
  }

  resultsBox.innerHTML = products.map((product) => `
    <article class="product-card">
      <div class="product-card__top">
        <div>
          <h3>${product.name}</h3>
          <p class="muted">${product.brand} • ${product.category}</p>
        </div>
        <strong class="product-card__price">R$ ${product.price}</strong>
      </div>
      <p>${product.description}</p>
      <div class="product-tags">
        <span>${product.skin_type}</span>
        <span>${product.finish}</span>
        <span>${product.color}</span>
      </div>
      <div class="score-row">
        <span class="score-pill">Busca: ${product.search_score ?? 0}</span>
        <span class="score-pill score-pill--pink">Match: ${product.match_score ?? "crie um perfil"}</span>
      </div>
    </article>
  `).join("");
}
