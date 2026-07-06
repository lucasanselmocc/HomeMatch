"""
framework/instances/dating/api.py
─────────────────────────────────
API FastAPI da instância Dating, no mesmo padrão da instância Makeup.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from framework.instances.dating.app import create_dating_app
from framework.instances.dating.strategies.ai_analyzer import DatingAIAnalyzer


api = FastAPI(title="DatingMatch API")

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
FRONTEND_DIR = BASE_DIR / "frontend"

api.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

dating = create_dating_app(
    ai_analyzer=DatingAIAnalyzer(),
    query_interpreter=None,
)

current_user: Any | None = None
liked_profile_ids: set[int] = set()
skipped_profile_ids: set[int] = set()
saved_profile_ids: set[int] = set()


class UserInput(BaseModel):
    email: str
    name: str
    age: int = Field(ge=18, le=120)
    city: str
    bio: str
    interests: list[str] = Field(default_factory=list)
    hobbies: list[str] = Field(default_factory=list)
    preferences: list[str] = Field(default_factory=list)
    lifestyle: str


class SearchInput(BaseModel):
    query: str


def normalize_text(value: str) -> str:
    return value.strip().lower()


def normalize_list(values: list[str]) -> list[str]:
    return [normalize_text(value) for value in values if value and value.strip()]


def to_dict(obj: Any) -> dict[str, Any]:
    data = {
        key: value
        for key, value in getattr(obj, "__dict__", {}).items()
        if key not in {"owner", "password"}
    }

    owner = getattr(obj, "owner", None)
    if owner is not None:
        data["owner_name"] = getattr(owner, "name", "")
        data["owner_email"] = getattr(owner, "email", "")

    return data


def score_profile(profile: Any) -> int | None:
    if current_user is None:
        return None

    scores = dating.match_score.calculate_match_score(
        user=current_user,
        posts=[profile],
    )
    return scores[0][1] if scores else None


def serialize_profile(profile: Any) -> dict[str, Any]:
    item = to_dict(profile)
    item["match_score"] = score_profile(profile)
    item["liked"] = profile.id in liked_profile_ids
    item["skipped"] = profile.id in skipped_profile_ids
    item["saved"] = profile.id in saved_profile_ids
    return item


def get_profile_or_404(profile_id: int) -> Any:
    profile = dating.posts.get_post(post_id=profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.")
    return profile


@api.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


seed_profiles = [
    {
        "user": {
            "email": "marina@dating.com",
            "name": "Marina",
            "user_type": "perfil",
            "password": "123",
        },
        "profile": {
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
    },
    {
        "user": {
            "email": "ana@dating.com",
            "name": "Ana",
            "user_type": "perfil",
            "password": "123",
        },
        "profile": {
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
    },
    {
        "user": {
            "email": "julia@dating.com",
            "name": "Júlia",
            "user_type": "perfil",
            "password": "123",
        },
        "profile": {
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
    },
    {
        "user": {
            "email": "lara@dating.com",
            "name": "Lara",
            "user_type": "perfil",
            "password": "123",
        },
        "profile": {
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
    },
]

for item in seed_profiles:
    user = dating.users.create_user(**item["user"])
    dating.posts.create_post(owner=user, validated_data=item["profile"])


@api.get("/profiles")
def list_profiles():
    profiles = dating.posts.list_posts()
    return [serialize_profile(profile) for profile in profiles]


@api.post("/user")
def create_or_update_user(data: UserInput):
    global current_user

    try:
        current_user = dating.users.get_user_by_email(email=data.email)
    except Exception:
        current_user = None

    if current_user is None:
        current_user = dating.users.create_user(
            email=data.email,
            name=data.name,
            user_type="pessoa",
            password="123",
        )

    current_user.name = data.name.strip()
    current_user.age = data.age
    current_user.city = data.city.strip()
    current_user.bio = data.bio.strip()
    current_user.interests = normalize_list(data.interests)
    current_user.hobbies = normalize_list(data.hobbies)
    current_user.preferences = normalize_list(data.preferences)
    current_user.lifestyle = data.lifestyle.strip().lower()

    return to_dict(current_user)


@api.post("/search")
def search_profiles(data: SearchInput):
    results = dating.search.search_posts(query=data.query)
    return [serialize_profile(profile) for profile in results]


@api.post("/profiles/{profile_id}/like")
def like_profile(profile_id: int):
    profile = get_profile_or_404(profile_id)
    liked_profile_ids.add(profile.id)
    skipped_profile_ids.discard(profile.id)
    return serialize_profile(profile)


@api.post("/profiles/{profile_id}/skip")
def skip_profile(profile_id: int):
    profile = get_profile_or_404(profile_id)
    skipped_profile_ids.add(profile.id)
    liked_profile_ids.discard(profile.id)
    return serialize_profile(profile)


@api.post("/profiles/{profile_id}/save")
def save_profile(profile_id: int):
    profile = get_profile_or_404(profile_id)

    if profile.id in saved_profile_ids:
        saved_profile_ids.remove(profile.id)
    else:
        saved_profile_ids.add(profile.id)

    return serialize_profile(profile)


@api.get("/matches")
def list_matches():
    profiles = dating.posts.list_posts()
    serialized = [serialize_profile(profile) for profile in profiles]

    compatible = [
        item
        for item in serialized
        if item["id"] in liked_profile_ids or (item.get("match_score") or 0) >= 55
    ]
    saved = [item for item in serialized if item["id"] in saved_profile_ids]

    compatible.sort(key=lambda item: item.get("match_score") or 0, reverse=True)
    saved.sort(key=lambda item: item.get("match_score") or 0, reverse=True)

    return {
        "liked": compatible,
        "saved": saved,
    }
