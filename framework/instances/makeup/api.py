from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from framework.instances.makeup.app import create_makeup_app
from framework.instances.makeup.strategies.ai_analyzer import MakeupAIAnalyzer


api = FastAPI(title="MakeupMatch API")

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
FRONTEND_DIR = BASE_DIR / "frontend"

api.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

makeup = create_makeup_app(
    ai_analyzer=MakeupAIAnalyzer(),
    query_interpreter=None,
)

current_user = None


class UserInput(BaseModel):
    email: str
    name: str
    skin_type: str
    preferred_finish: str
    max_price: float


class SearchInput(BaseModel):
    query: str


def to_dict(obj):
    return {
        key: value
        for key, value in obj.__dict__.items()
        if key != "owner"
    }


@api.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


seller = makeup.users.create_user(
    email="loja@makeup.com",
    name="BeautyLab Store",
    user_type="vendedor",
    password="123",
)

for product in [
    {
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
        "name": "Batom Red Night",
        "brand": "ColorLux",
        "category": "batom",
        "description": "Batom vermelho intenso para usar à noite.",
        "skin_type": "todos",
        "finish": "matte",
        "color": "vermelho",
        "price": 45,
    },
]:
    makeup.posts.create_post(owner=seller, validated_data=product)


@api.post("/user")
def create_user(data: UserInput):
    global current_user

    try:
        current_user = makeup.users.get_user_by_email(email=data.email)
    except Exception:
        current_user = makeup.users.create_user(
            email=data.email,
            name=data.name,
            user_type="cliente",
            password="123",
        )

    current_user.name = data.name
    current_user.skin_type = data.skin_type
    current_user.preferred_finish = data.preferred_finish
    current_user.max_price = data.max_price

    return to_dict(current_user)


@api.post("/search")
def search_products(data: SearchInput):
    results = makeup.search.search_posts(query=data.query)
    response = []

    for product in results:
        item = to_dict(product)

        if current_user is not None:
            scores = makeup.match_score.calculate_match_score(
                user=current_user,
                posts=[product],
            )
            item["match_score"] = scores[0][1]
        else:
            item["match_score"] = None

        response.append(item)

    return response