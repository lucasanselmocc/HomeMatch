/**
 * HomeMatch Frontend — API Client
 */

export const BASE_URL = "http://localhost:8000";

export const Auth = {
  getAccess: () => localStorage.getItem("hm_access"),
  getRefresh: () => localStorage.getItem("hm_refresh"),

  set(access, refresh) {
    localStorage.setItem("hm_access", access);
    if (refresh) localStorage.setItem("hm_refresh", refresh);
  },

  clear() {
    localStorage.removeItem("hm_access");
    localStorage.removeItem("hm_refresh");
  },

  isLoggedIn: () => !!localStorage.getItem("hm_access"),
};

export function formatApiError(data, fallback = "Erro na requisição.") {
  if (!data) return fallback;

  if (typeof data === "string") return data;

  if (Array.isArray(data)) {
    const parts = data
      .map((item) => formatApiError(item, ""))
      .filter(Boolean);

    return parts.join(" ") || fallback;
  }

  if (typeof data === "object") {
    if (data.detail) return formatApiError(data.detail, fallback);
    if (data.error) return formatApiError(data.error, fallback);
    if (data.message) return formatApiError(data.message, fallback);

    const parts = [];

    function walk(value, prefix = "") {
      if (value === null || value === undefined || value === "") return;

      if (typeof value === "string") {
        parts.push(prefix ? `${prefix}: ${value}` : value);
        return;
      }

      if (Array.isArray(value)) {
        value.forEach((item) => walk(item, prefix));
        return;
      }

      if (typeof value === "object") {
        const entries = Object.entries(value);

        if (!entries.length) return;

        entries.forEach(([key, child]) => {
          const nextPrefix = prefix ? `${prefix}.${key}` : key;
          walk(child, nextPrefix);
        });

        return;
      }

      parts.push(prefix ? `${prefix}: ${String(value)}` : String(value));
    }

    walk(data);

    return parts.join(" | ") || fallback;
  }

  return String(data) || fallback;
}

async function req(path, { method = "GET", body, auth = false, isForm = false } = {}) {
  const headers = {};

  if (body && !isForm) headers["Content-Type"] = "application/json";
  if (auth && Auth.getAccess()) headers["Authorization"] = `Bearer ${Auth.getAccess()}`;

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? (isForm ? body : JSON.stringify(body)) : undefined,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));

    if (res.status === 401) {
      Auth.clear();

      throw Object.assign(new Error("Sessão expirada. Faça login novamente."), {
        status: res.status,
        data: err,
        authExpired: true,
      });
    }

    throw Object.assign(
      new Error(formatApiError(err, `Erro HTTP ${res.status}. Verifique os campos enviados.`)),
      { status: res.status, data: err }
    );
  }

  return res.status === 204 ? null : res.json();
}

function cleanParams(params = {}) {
  return Object.fromEntries(
    Object.entries(params).filter(([, value]) => value !== "" && value !== null && value !== undefined)
  );
}

function queryString(params = {}) {
  return new URLSearchParams(cleanParams(params)).toString();
}

export function listItems(data) {
  return Array.isArray(data) ? data : (data?.results ?? []);
}

export function resolveImageUrl(url) {
  if (!url) return "";
  if (url.startsWith("http://") || url.startsWith("https://")) return url;
  if (url.startsWith("/")) return `${BASE_URL}${url}`;
  return `${BASE_URL}/${url}`;
}

// Auth
export async function login(email, password) {
  const data = await req("/api/users/login/", {
    method: "POST",
    body: { email, password },
  });

  Auth.set(data.access, data.refresh);
  return data;
}

export async function register(name, email, password, user_type = "S") {
  return req("/api/users/register/", {
    method: "POST",
    body: { name, email, password, user_type },
  });
}

export async function logout() {
  const refresh = Auth.getRefresh();

  if (refresh) {
    await req("/api/users/logout/", {
      method: "POST",
      body: { refresh },
      auth: true,
    }).catch(() => {});
  }

  Auth.clear();
}

export async function getMe() {
  return req("/api/users/me/", { auth: true });
}

export async function updateMe(data) {
  return req("/api/users/me/", {
    method: "PATCH",
    body: data,
    auth: true,
  });
}

// Properties
export async function getProperties(params = {}) {
  const qs = queryString(params);
  return req(`/api/properties/${qs ? "?" + qs : ""}`);
}

export async function searchProperties(params = {}) {
  const qs = queryString(params);
  return req(`/api/search/properties/${qs ? "?" + qs : ""}`);
}

export async function getProperty(id) {
  return req(`/api/properties/${id}/`);
}

export async function createProperty(data) {
  return req("/api/properties/", {
    method: "POST",
    body: data,
    auth: true,
  });
}

export async function updateProperty(id, data) {
  return req(`/api/properties/${id}/`, {
    method: "PATCH",
    body: data,
    auth: true,
  });
}

export async function deleteProperty(id) {
  return req(`/api/properties/${id}/`, {
    method: "DELETE",
    auth: true,
  });
}

export async function uploadPropertyPhoto(propertyId, file, order = 1) {
  const form = new FormData();
  form.append("image", file);
  form.append("order", String(order));

  return req(`/api/properties/${propertyId}/photos/`, {
    method: "POST",
    body: form,
    auth: true,
    isForm: true,
  });
}

export async function deletePropertyPhoto(photoId) {
  return req(`/api/properties/photos/${photoId}/`, {
    method: "DELETE",
    auth: true,
  });
}

export async function getMyProperties() {
  const [me, data] = await Promise.all([getMe(), getProperties()]);
  const items = listItems(data);

  return items.filter((p) => {
    if (p.owner !== undefined && p.owner !== null) return Number(p.owner) === Number(me.id);
    if (p.owner_id !== undefined && p.owner_id !== null) return Number(p.owner_id) === Number(me.id);
    return p.owner_name === me.name;
  });
}

// Favorites
export async function getFavorites() {
  return req("/api/users/favorites/", { auth: true });
}

export async function addFavorite(property_id) {
  return req("/api/users/favorites/", {
    method: "POST",
    body: { property_id },
    auth: true,
  });
}

export async function removeFavorite(property_id) {
  return req("/api/users/favorites/", {
    method: "DELETE",
    body: { property_id },
    auth: true,
  });
}

// Reviews
export async function getReviews(property_id) {
  return req(`/api/properties/${property_id}/reviews/`);
}

export async function createReview(property_id, rating, comment) {
  return req(`/api/properties/${property_id}/reviews/`, {
    method: "POST",
    body: { rating, comment },
    auth: true,
  });
}

// Formatting
export function fmtPrice(value) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    maximumFractionDigits: 0,
  }).format(value);
}

export const TYPE_LABEL = {
  A: "Apartamento",
  H: "Casa",
};

export const PURPOSE_LABEL = {
  S: "Venda",
  R: "Aluguel",
  B: "Venda/Aluguel",
};
