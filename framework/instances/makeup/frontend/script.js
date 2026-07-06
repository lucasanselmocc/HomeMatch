let currentUser = null;

function showTab(tabId) {
  document.querySelectorAll(".tab").forEach(tab => tab.classList.remove("active"));
  document.querySelectorAll(".tabs button").forEach(btn => btn.classList.remove("active"));

  document.getElementById(tabId).classList.add("active");
  event.target.classList.add("active");
}

function setQuery(text) {
  document.getElementById("query").value = text;
}

async function createUser() {
  const response = await fetch("/user", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: document.getElementById("email").value,
      name: document.getElementById("name").value,
      skin_type: document.getElementById("skinType").value,
      preferred_finish: document.getElementById("finish").value,
      max_price: Number(document.getElementById("maxPrice").value),
    }),
  });

  currentUser = await response.json();

  document.getElementById("profileResult").innerHTML = `
    <div class="product">
      <h3>Perfil criado</h3>
      <p><strong>Nome:</strong> ${currentUser.name}</p>
      <p><strong>Tipo de pele:</strong> ${currentUser.skin_type}</p>
      <p><strong>Acabamento preferido:</strong> ${currentUser.preferred_finish}</p>
      <p><strong>Preço máximo:</strong> R$ ${currentUser.max_price}</p>
    </div>
  `;

  showTab("search");
}

async function searchProducts() {
  const response = await fetch("/search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query: document.getElementById("query").value,
    }),
  });

  const products = await response.json();
  const results = document.getElementById("results");

  results.innerHTML = "";

  products.forEach((item) => {
    const div = document.createElement("div");
    div.className = "product";

    div.innerHTML = `
      <h3>${item.name}</h3>
      <p><strong>Marca:</strong> ${item.brand}</p>
      <p><strong>Categoria:</strong> ${item.category}</p>
      <p>${item.description}</p>
      <p><strong>Tipo de pele:</strong> ${item.skin_type}</p>
      <p><strong>Acabamento:</strong> ${item.finish}</p>
      <p><strong>Cor:</strong> ${item.color}</p>
      <p><strong>Preço:</strong> R$ ${item.price}</p>
      <p class="score">Score de busca: ${item.search_score}</p>
      <p class="score">Match-score: ${
        item.match_score === null ? "crie um perfil primeiro" : item.match_score
      }</p>
    `;

    results.appendChild(div);
  });
}