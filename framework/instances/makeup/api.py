from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

api = FastAPI(title="MakeupMatch API", version="1.0.0")
api.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class MakeupUserPayload(BaseModel):
    email: str
    name: str
    skin_type: str = "oleosa"
    preferred_finish: str = "natural"
    max_price: float = 80


class SearchPayload(BaseModel):
    query: str


CURRENT_USER: dict[str, Any] = {
    "id": 1,
    "email": "bia@email.com",
    "name": "Bia",
    "user_type": "cliente",
    "password": "123",
    "skin_type": "oleosa",
    "preferred_finish": "natural",
    "max_price": 80,
}


PRODUCTS: list[dict[str, Any]] = [
    {
        "id": 1,
        "name": "Base Natural Glow",
        "brand": "BeautyLab",
        "category": "base",
        "description": "Base leve para pele oleosa com acabamento natural.",
        "skin_type": "oleosa",
        "finish": "natural",
        "color": "bege médio",
        "price": 65,
    },
    {
        "id": 2,
        "name": "Base Matte Control",
        "brand": "SkinPro",
        "category": "base",
        "description": "Base de alta cobertura para pele oleosa com acabamento matte.",
        "skin_type": "oleosa",
        "finish": "matte",
        "color": "bege claro",
        "price": 89,
    },
    {
        "id": 3,
        "name": "Corretivo Soft Cover",
        "brand": "GlowUp",
        "category": "corretivo",
        "description": "Corretivo cremoso para olheiras com acabamento natural.",
        "skin_type": "mista",
        "finish": "natural",
        "color": "médio",
        "price": 42,
    },
    {
        "id": 4,
        "name": "Batom Red Night",
        "brand": "ColorLux",
        "category": "batom",
        "description": "Batom vermelho intenso para usar à noite.",
        "skin_type": "todos",
        "finish": "matte",
        "color": "vermelho",
        "price": 45,
    },
    {
        "id": 5,
        "name": "Blush Peach Glow",
        "brand": "GlowUp",
        "category": "blush",
        "description": "Blush pêssego com efeito glow para acabamento iluminado.",
        "skin_type": "todos",
        "finish": "glow",
        "color": "pêssego",
        "price": 38,
    },
]


STOPWORDS = {
    "a", "o", "os", "as", "um", "uma", "uns", "umas",
    "de", "da", "do", "das", "dos", "e", "ou", "com",
    "para", "por", "que", "quero", "produto", "produtos",
    "maquiagem", "maquiagens", "usar", "uso",
}


CATEGORY_ALIASES = {
    "base": {"base", "bases"},
    "corretivo": {"corretivo", "corretivos", "olheira", "olheiras"},
    "batom": {"batom", "batons"},
    "blush": {"blush"},
}


def normalize(text: Any) -> str:
    value = "" if text is None else str(text).lower()
    value = unicodedata.normalize("NFD", value)
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    return value


def tokenize(text: str) -> list[str]:
    normalized = normalize(text)
    tokens = re.findall(r"[a-z0-9]+", normalized)
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1]


def detect_category(query: str) -> str | None:
    query_terms = set(tokenize(query))

    for category, aliases in CATEGORY_ALIASES.items():
        normalized_aliases = {normalize(alias) for alias in aliases}
        if query_terms.intersection(normalized_aliases):
            return category

    return None


def product_text(product: dict[str, Any]) -> str:
    return normalize(
        " ".join(
            [
                product.get("name", ""),
                product.get("brand", ""),
                product.get("category", ""),
                product.get("description", ""),
                product.get("skin_type", ""),
                product.get("finish", ""),
                product.get("color", ""),
            ]
        )
    )


def calculate_search_score(product: dict[str, Any], query: str) -> int:
    terms = tokenize(query)
    text = product_text(product)

    if not terms:
        return 0

    score = 0

    for term in terms:
        if term in text:
            score += 1

        if term == normalize(product.get("category", "")):
            score += 5

        if term == normalize(product.get("skin_type", "")):
            score += 3

        if term == normalize(product.get("finish", "")):
            score += 3

        if term == normalize(product.get("color", "")):
            score += 2

    return score


def calculate_match_score(product: dict[str, Any]) -> int:
    score = 0

    if normalize(product.get("skin_type")) == normalize(CURRENT_USER.get("skin_type")):
        score += 40

    if product.get("skin_type") == "todos":
        score += 20

    if normalize(product.get("finish")) == normalize(CURRENT_USER.get("preferred_finish")):
        score += 35

    try:
        if float(product.get("price", 0)) <= float(CURRENT_USER.get("max_price", 0)):
            score += 25
    except (TypeError, ValueError):
        pass

    return min(score, 100)


def serialize_product(product: dict[str, Any], search_score: int = 0) -> dict[str, Any]:
    return {
        **product,
        "search_score": search_score,
        "match_score": calculate_match_score(product),
    }


@api.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@api.get("/perfil.html")
def profile_page():
    return FileResponse(FRONTEND_DIR / "perfil.html")


@api.get("/buscar.html")
def search_page():
    return FileResponse(FRONTEND_DIR / "buscar.html")


@api.get("/recomendacoes.html")
def recommendations_page():
    return FileResponse(FRONTEND_DIR / "recomendacoes.html")


@api.get("/products")
def list_products():
    return [serialize_product(product) for product in PRODUCTS]


@api.post("/user")
def create_or_update_user(payload: MakeupUserPayload):
    CURRENT_USER.update(payload.model_dump())
    CURRENT_USER["id"] = CURRENT_USER.get("id", 1)
    CURRENT_USER["user_type"] = "cliente"
    CURRENT_USER["password"] = "123"
    return CURRENT_USER


@api.get("/user")
def get_current_user():
    return CURRENT_USER


@api.post("/search")
def search_products(payload: SearchPayload):
    category = detect_category(payload.query)
    ranked: list[tuple[dict[str, Any], int, int]] = []

    for product in PRODUCTS:
        if category and normalize(product.get("category")) != normalize(category):
            continue

        search_score = calculate_search_score(product, payload.query)
        match_score = calculate_match_score(product)

        if search_score > 0 or category:
            ranked.append((product, search_score, match_score))

    ranked.sort(key=lambda item: (item[1], item[2]), reverse=True)

    return [
        serialize_product(product, search_score=search_score)
        for product, search_score, _ in ranked
    ]
