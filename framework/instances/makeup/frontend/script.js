const $ = (id) => document.getElementById(id);

const STORAGE_KEY = "makeupSavedProducts";

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

function money(value) {
  return Number(value || 0).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

function getSavedProducts() {
  return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
}

function setSavedProducts(products) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(products));
}

function setupHomePage() {
  const heroSearch = $("hero-search");
  if (!heroSearch) return;

  heroSearch.addEventListener("submit", (event) => {
    event.preventDefault();
    const query = $("hero-query").value.trim();
    const url = query ? `/buscar.html?query=${encodeURIComponent(query)}` : "/buscar.html";
    window.location.href = url;
  });
}

function setupProfilePage() {
  const form = $("profile-form");
  const statusBox = $("profile-status");

  if (!form || !statusBox) return;

  ["name", "skinType", "finish", "maxPrice"].forEach((id) => {
    const field = $(id);
    if (field) field.addEventListener("input", updatePreview);
  });

  updatePreview();

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    statusBox.innerHTML = `<p class="muted">Salvando perfil...</p>`;

    try {
      const user = await request("/user", {
        method: "POST",
        body: JSON.stringify({
          email: $("email").value.trim(),
          name: $("name").value.trim(),
          skin_type: $("skinType").value.trim(),
          preferred_finish: $("finish").value.trim(),
          max_price: Number($("maxPrice").value),
        }),
      });

      statusBox.innerHTML = `
        <p class="success">Perfil salvo com sucesso.</p>
        <p><strong>${user.name}</strong> — pele ${user.skin_type}, acabamento ${user.preferred_finish}</p>
      `;

      showModal({
        title: "Perfil de beleza salvo",
        message: "Agora a busca consegue ranquear produtos com base no seu tipo de pele, acabamento e orçamento.",
        primaryText: "Buscar produtos",
        secondaryText: "Continuar editando",
        onPrimary: () => {
          window.location.href = "/buscar.html?query=base%20para%20pele%20oleosa%20acabamento%20natural";
        },
      });
    } catch (error) {
      statusBox.innerHTML = `<p class="error">${error.message}</p>`;
    }
  });
}

function updatePreview() {
  const name = $("name")?.value?.trim() || "Bia";
  const skin = $("skinType")?.value?.trim() || "oleosa";
  const finish = $("finish")?.value?.trim() || "natural";
  const maxPrice = $("maxPrice")?.value || "80";

  if ($("preview-name")) $("preview-name").textContent = name;
  if ($("preview-text")) {
    $("preview-text").textContent = `Pele ${skin}, acabamento ${finish} e preço máximo de R$ ${maxPrice}.`;
  }

  if ($("preview-tags")) {
    $("preview-tags").innerHTML = `
      <span>${skin}</span>
      <span>${finish}</span>
      <span>até R$ ${maxPrice}</span>
    `;
  }
}

function setupSearchPage() {
  const form = $("search-form");
  const queryInput = $("query");

  if (!form || !queryInput) return;

  const params = new URLSearchParams(window.location.search);
  const queryParam = params.get("query");

  if (queryParam) queryInput.value = queryParam;

  document.querySelectorAll("[data-query]").forEach((button) => {
    button.addEventListener("click", () => {
      queryInput.value = button.dataset.query;
      searchProducts();
    });
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    searchProducts();
  });

  searchProducts();
}

async function searchProducts() {
  const query = $("query")?.value?.trim();
  const resultsBox = $("results");

  if (!query || !resultsBox) return;

  resultsBox.innerHTML = `<div class="product-card"><p class="muted">Buscando produtos compatíveis...</p></div>`;

  try {
    const products = await request("/search", {
      method: "POST",
      body: JSON.stringify({ query }),
    });

    renderProducts(products);
  } catch (error) {
    resultsBox.innerHTML = `<div class="product-card"><p class="error">${error.message}</p></div>`;
  }
}

function renderProducts(products) {
  const resultsBox = $("results");
  if (!resultsBox) return;

  if (!products.length) {
    resultsBox.innerHTML = `<div class="product-card"><p class="muted">Nenhum produto encontrado.</p></div>`;
    return;
  }

  resultsBox.innerHTML = products.map(productCard).join("");

  resultsBox.querySelectorAll("[data-save-product]").forEach((button) => {
    button.addEventListener("click", () => {
      const product = products.find((item) => String(item.id) === button.dataset.saveProduct);
      if (product) saveProduct(product);
    });
  });
}

function productCard(product) {
  const match = product.match_score ?? 0;
  const tags = [product.category, product.skin_type, product.finish, product.color].filter(Boolean);

  return `
    <article class="product-card">
      <div class="product-card__top">
        <div>
          <h3>${product.name}</h3>
          <p class="muted">${product.brand}</p>
        </div>
        <strong class="product-card__price">${money(product.price)}</strong>
      </div>

      <p>${product.description}</p>

      <div class="product-tags">
        ${tags.map((tag) => `<span>${tag}</span>`).join("")}
      </div>

      <div class="product-actions">
        <span class="score-pill">Busca ${product.search_score ?? 0}</span>
        <span class="score-pill score-pill--hot">Match ${match}%</span>
        <button class="btn btn--ghost" type="button" data-save-product="${product.id}">Salvar</button>
      </div>
    </article>
  `;
}

function saveProduct(product) {
  const saved = getSavedProducts();
  const exists = saved.some((item) => item.id === product.id);

  if (!exists) {
    saved.push(product);
    setSavedProducts(saved);
  }

  showModal({
    title: exists ? "Produto já estava salvo" : "Produto salvo",
    message: `${product.name} foi adicionado à tela de recomendações.`,
    primaryText: "Ver recomendações",
    secondaryText: "Continuar buscando",
    onPrimary: () => {
      window.location.href = "/recomendacoes.html";
    },
  });
}

function setupRecommendationsPage() {
  const button = $("load-recommendations");
  if (!button) return;

  button.addEventListener("click", loadRecommendations);
  loadRecommendations();
}

async function loadRecommendations() {
  const savedBox = $("saved-products");
  const recommendedBox = $("recommended-products");

  if (!savedBox || !recommendedBox) return;

  const saved = getSavedProducts();
  savedBox.innerHTML = renderMiniList(saved, "Nenhum produto salvo ainda.");

  recommendedBox.innerHTML = `<p class="muted">Carregando recomendações...</p>`;

  try {
    const products = await request("/search", {
      method: "POST",
      body: JSON.stringify({ query: "base para pele oleosa acabamento natural" }),
    });

    const recommended = products
      .slice()
      .sort((a, b) => (b.match_score || 0) - (a.match_score || 0))
      .slice(0, 4);

    recommendedBox.innerHTML = renderMiniList(recommended, "Nenhuma recomendação encontrada.");
  } catch (error) {
    recommendedBox.innerHTML = `<p class="error">${error.message}</p>`;
  }
}

function renderMiniList(items, emptyMessage) {
  if (!items.length) return `<p class="muted">${emptyMessage}</p>`;

  return items.map((item) => `
    <article class="mini-card">
      <div class="mini-product-art"></div>
      <div>
        <strong>${item.name}</strong>
        <span>${item.brand} • ${money(item.price)} • match ${item.match_score ?? 0}%</span>
        <p>${item.description || ""}</p>
      </div>
    </article>
  `).join("");
}

function showModal({ title, message, primaryText = "Ok", secondaryText = "", onPrimary = null }) {
  document.querySelectorAll(".app-modal").forEach((modal) => modal.remove());

  const modal = document.createElement("div");
  modal.className = "app-modal";
  modal.innerHTML = `
    <div class="app-modal__backdrop"></div>
    <section class="app-modal__card" role="dialog" aria-modal="true">
      <div class="app-modal__icon">✦</div>
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
setupSearchPage();
setupRecommendationsPage();
