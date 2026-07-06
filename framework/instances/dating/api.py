from __future__ import annotations

import math
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

api = FastAPI(title="DatingMatch API", version="1.0.0")
api.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class DatingUserPayload(BaseModel):
    email: str
    name: str
    age: int = 23
    city: str = "Natal"
    bio: str = ""
    interests: list[str] = []
    hobbies: list[str] = []
    preferences: list[str] = []
    lifestyle: str = "ao ar livre"
    photo_url: str | None = None


class SearchPayload(BaseModel):
    query: str


CURRENT_USER: dict[str, Any] = {
    "id": 999,
    "email": "lucas@email.com",
    "name": "Lucas",
    "age": 23,
    "city": "Natal",
    "bio": "Gosto de praia, filmes, tecnologia e rolês tranquilos.",
    "interests": ["praia", "esportes", "filmes", "tecnologia"],
    "hobbies": ["cinema", "caminhada", "jogos"],
    "preferences": ["conversa leve", "atividades ao ar livre"],
    "lifestyle": "ao ar livre",
    "photo_url": None,
}

PROFILES: list[dict[str, Any]] = [
    {
        "id": 1,
        "name": "Marina",
        "age": 24,
        "city": "Natal",
        "bio": "Gosto de praia, corrida leve, cafés tranquilos e filmes no fim de semana.",
        "interests": ["praia", "esportes", "filmes", "café"],
        "hobbies": ["corrida", "cinema", "fotografia"],
        "preferences": ["conversa leve", "atividades ao ar livre"],
        "lifestyle": "ao ar livre",
        "photo_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": 2,
        "name": "Ana",
        "age": 27,
        "city": "Parnamirim",
        "bio": "Amo viajar, testar restaurantes novos, assistir séries e planejar trilhas.",
        "interests": ["viagens", "séries", "gastronomia", "trilhas"],
        "hobbies": ["cozinhar", "viajar", "caminhada"],
        "preferences": ["bom humor", "passeios"],
        "lifestyle": "exploradora",
        "photo_url": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": 3,
        "name": "Júlia",
        "age": 22,
        "city": "Natal",
        "bio": "Curto música ao vivo, academia, praia e conversas sobre tecnologia.",
        "interests": ["música", "academia", "praia", "tecnologia"],
        "hobbies": ["violão", "treino", "shows"],
        "preferences": ["interesses em comum", "rotina saudável"],
        "lifestyle": "ativa",
        "photo_url": "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?auto=format&fit=crop&w=900&q=80",
    },
    {
        "id": 4,
        "name": "Lara",
        "age": 25,
        "city": "Natal",
        "bio": "Gosto de livros, cinema, cafés, jogos de tabuleiro e rolês tranquilos.",
        "interests": ["livros", "cinema", "café", "jogos"],
        "hobbies": ["leitura", "board games", "filmes"],
        "preferences": ["calma", "conversa profunda"],
        "lifestyle": "caseira",
        "photo_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=900&q=80",
    },
]

LIKED_IDS: set[int] = set()
SAVED_IDS: set[int] = set()
SKIPPED_IDS: set[int] = set()


STOPWORDS = {
    "a", "o", "os", "as", "um", "uma", "uns", "umas",
    "de", "da", "do", "das", "dos", "e", "ou", "com",
    "que", "quem", "alguem", "alguém", "pessoa", "pessoas",
    "perfil", "perfis", "gosta", "gostam", "goste", "gostar", "curte", "curtem",
    "pratica", "praticam", "assistir", "ver", "para", "por",
}

ALIASES = {
    "esporte": {"esporte", "esportes", "corrida", "academia", "treino", "caminhada", "trilha", "trilhas"},
    "esportes": {"esporte", "esportes", "corrida", "academia", "treino", "caminhada", "trilha", "trilhas"},
    "filme": {"filme", "filmes", "cinema", "serie", "series", "série", "séries"},
    "filmes": {"filme", "filmes", "cinema", "serie", "series", "série", "séries"},
    "viajar": {"viajar", "viagem", "viagens", "trilha", "trilhas", "exploradora"},
    "viagem": {"viajar", "viagem", "viagens", "trilha", "trilhas", "exploradora"},
    "viagens": {"viajar", "viagem", "viagens", "trilha", "trilhas", "exploradora"},
    "livro": {"livro", "livros", "leitura"},
    "livros": {"livro", "livros", "leitura"},
    "cafe": {"cafe", "cafes", "café", "cafés"},
    "cafes": {"cafe", "cafes", "café", "cafés"},
    "musica": {"musica", "música", "violao", "violão", "shows", "show"},
    "tecnologia": {"tecnologia", "tech"},
    "caseira": {"caseira", "calma", "livros", "leitura", "cafe", "cafes"},
    "praia": {"praia", "ar livre", "outdoor"},
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


def expanded_terms(term: str) -> set[str]:
    normalized = normalize(term)
    aliases = ALIASES.get(normalized, {normalized})
    return {normalize(item) for item in aliases}


def profile_text(profile: dict[str, Any]) -> str:
    chunks = [
        profile.get("name", ""),
        profile.get("city", ""),
        profile.get("bio", ""),
        profile.get("lifestyle", ""),
        " ".join(profile.get("interests", [])),
        " ".join(profile.get("hobbies", [])),
        " ".join(profile.get("preferences", [])),
    ]
    return normalize(" ".join(chunks))


def relevance_score(profile: dict[str, Any], query: str) -> tuple[int, int, list[str]]:
    terms = tokenize(query)
    if not terms:
        return 0, 0, []

    text = profile_text(profile)
    matched_terms: list[str] = []
    score = 0

    for term in terms:
        options = expanded_terms(term)
        matched = any(option in text for option in options)

        if matched:
            matched_terms.append(term)

            if any(option in normalize(" ".join(profile.get("interests", []))) for option in options):
                score += 4
            if any(option in normalize(" ".join(profile.get("hobbies", []))) for option in options):
                score += 3
            if any(option in normalize(" ".join(profile.get("preferences", []))) for option in options):
                score += 2
            if any(option in normalize(profile.get("bio", "")) for option in options):
                score += 2
            if any(option in normalize(profile.get("lifestyle", "")) for option in options):
                score += 2
            if any(option in normalize(profile.get("city", "")) for option in options):
                score += 1

    return score, len(matched_terms), terms


def calculate_match_score(profile: dict[str, Any]) -> int:
    user_terms = {
        *map(normalize, CURRENT_USER.get("interests", [])),
        *map(normalize, CURRENT_USER.get("hobbies", [])),
        *map(normalize, CURRENT_USER.get("preferences", [])),
        normalize(CURRENT_USER.get("lifestyle", "")),
        normalize(CURRENT_USER.get("city", "")),
    }

    profile_terms = {
        *map(normalize, profile.get("interests", [])),
        *map(normalize, profile.get("hobbies", [])),
        *map(normalize, profile.get("preferences", [])),
        normalize(profile.get("lifestyle", "")),
        normalize(profile.get("city", "")),
    }

    user_terms = {item for item in user_terms if item}
    profile_terms = {item for item in profile_terms if item}

    if not user_terms:
        return 0

    common = user_terms.intersection(profile_terms)
    base = int((len(common) / max(len(user_terms), 1)) * 100)

    if normalize(CURRENT_USER.get("city")) == normalize(profile.get("city")):
        base += 10

    return min(100, max(20, base))


def serialize_profile(profile: dict[str, Any], search_score: int | None = None) -> dict[str, Any]:
    return {
        **profile,
        "search_score": search_score,
        "owner_name": profile["name"],
        "owner_email": f'{normalize(profile["name"])}@dating.com',
        "match_score": calculate_match_score(profile),
        "liked": profile["id"] in LIKED_IDS,
        "skipped": profile["id"] in SKIPPED_IDS,
        "saved": profile["id"] in SAVED_IDS,
    }


def get_profile(profile_id: int) -> dict[str, Any]:
    for profile in PROFILES:
        if profile["id"] == profile_id:
            return profile
    raise ValueError("Perfil não encontrado.")


@api.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@api.get("/perfil.html")
def profile_page():
    return FileResponse(FRONTEND_DIR / "perfil.html")


@api.get("/descobrir.html")
def discover_page():
    return FileResponse(FRONTEND_DIR / "descobrir.html")


@api.get("/matches.html")
def matches_page():
    return FileResponse(FRONTEND_DIR / "matches.html")


@api.get("/profiles")
def list_profiles():
    return [serialize_profile(profile) for profile in PROFILES]


@api.post("/user")
def create_or_update_user(payload: DatingUserPayload):
    CURRENT_USER.update(payload.model_dump())
    CURRENT_USER["id"] = 999
    return CURRENT_USER


@api.get("/user")
def get_current_user():
    return CURRENT_USER


@api.post("/search")
def search_profiles(payload: SearchPayload):
    ranked: list[tuple[dict[str, Any], int, int, int]] = []

    for profile in PROFILES:
        score, matched_count, terms = relevance_score(profile, payload.query)

        if not terms:
            continue

        required_matches = len(set(terms))

        if matched_count >= required_matches:
            ranked.append((profile, score, matched_count, calculate_match_score(profile)))

    ranked.sort(key=lambda item: (item[1], item[2], item[3]), reverse=True)

    return [
        serialize_profile(profile, search_score=score)
        for profile, score, _, _ in ranked
        if profile["id"] not in SKIPPED_IDS
    ]


@api.post("/profiles/{profile_id}/like")
def like_profile(profile_id: int):
    get_profile(profile_id)
    LIKED_IDS.add(profile_id)
    SKIPPED_IDS.discard(profile_id)
    return {"message": "Perfil curtido.", "profile_id": profile_id}


@api.post("/profiles/{profile_id}/skip")
def skip_profile(profile_id: int):
    get_profile(profile_id)
    SKIPPED_IDS.add(profile_id)
    LIKED_IDS.discard(profile_id)
    return {"message": "Perfil ignorado.", "profile_id": profile_id}


@api.post("/profiles/{profile_id}/save")
def save_profile(profile_id: int):
    get_profile(profile_id)

    if profile_id in SAVED_IDS:
        SAVED_IDS.remove(profile_id)
        return {"message": "Perfil removido dos salvos.", "profile_id": profile_id, "saved": False}

    SAVED_IDS.add(profile_id)
    return {"message": "Perfil salvo.", "profile_id": profile_id, "saved": True}


@api.get("/matches")
def matches():
    liked = [
        serialize_profile(profile)
        for profile in PROFILES
        if profile["id"] in LIKED_IDS
    ]

    saved = [
        serialize_profile(profile)
        for profile in PROFILES
        if profile["id"] in SAVED_IDS
    ]

    compatible = [
        serialize_profile(profile)
        for profile in sorted(PROFILES, key=calculate_match_score, reverse=True)
        if calculate_match_score(profile) >= 55
    ]

    return {
        "liked": liked or compatible,
        "saved": saved,
    }
