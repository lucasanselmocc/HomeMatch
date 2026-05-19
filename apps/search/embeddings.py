import hashlib
import json
import math
import re
import unicodedata
from decimal import Decimal

from django.conf import settings

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


LOCAL_EMBEDDING_DIMENSIONS = 256


class EmbeddingService:
    @staticmethod
    def embed_text(text: str) -> list[float]:
        text = (text or "").strip()
        if not text:
            return []

        if OpenAI is not None and getattr(settings, "AI_API_KEY", None):
            try:
                client = OpenAI(
                    base_url=getattr(settings, "AI_API_BASE_URL", None),
                    api_key=settings.AI_API_KEY,
                )
                response = client.embeddings.create(
                    model=getattr(
                        settings,
                        "SEARCH_EMBEDDING_MODEL",
                        "text-embedding-004",
                    ),
                    input=text,
                )
                return [float(value) for value in response.data[0].embedding]
            except Exception:
                pass

        return EmbeddingService._local_embedding(text)

    @staticmethod
    def serialize(embedding: list[float]) -> str:
        return json.dumps(embedding or [], separators=(",", ":"))

    @staticmethod
    def deserialize(raw_embedding) -> list[float]:
        if not raw_embedding:
            return []
        if isinstance(raw_embedding, list):
            return [float(value) for value in raw_embedding]
        try:
            parsed = json.loads(raw_embedding)
        except (TypeError, ValueError):
            return []
        if not isinstance(parsed, list):
            return []
        return [float(value) for value in parsed]

    @staticmethod
    def cosine_similarity(left: list[float], right: list[float]) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0

        dot = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(a * a for a in left))
        right_norm = math.sqrt(sum(b * b for b in right))
        if not left_norm or not right_norm:
            return 0.0
        return dot / (left_norm * right_norm)

    @staticmethod
    def refresh_property_embedding(property_obj):
        document = PropertyEmbeddingDocumentBuilder.build(property_obj)
        property_obj.embedding = EmbeddingService.serialize(
            EmbeddingService.embed_text(document)
        )
        property_obj.save(update_fields=["embedding"])
        return property_obj

    @staticmethod
    def _local_embedding(text: str) -> list[float]:
        vector = [0.0] * LOCAL_EMBEDDING_DIMENSIONS
        tokens = re.findall(r"\w+", EmbeddingService._normalize_text(text))

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % LOCAL_EMBEDDING_DIMENSIONS
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if not norm:
            return []
        return [value / norm for value in vector]

    @staticmethod
    def _normalize_text(text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text.lower())
        return "".join(char for char in normalized if not unicodedata.combining(char))


class PropertyEmbeddingDocumentBuilder:
    PROPERTY_TYPE_LABELS = {"A": "apartamento", "H": "casa"}
    PURPOSE_LABELS = {"S": "venda", "R": "aluguel", "B": "venda ou aluguel"}

    ROOM_EXTRA_LABELS = {
        "living_room": "sala de estar",
        "garden": "jardim",
        "kitchen": "cozinha",
        "laundry_room": "lavanderia",
        "pool": "piscina",
        "office": "escritorio home office",
    }

    CONDO_LABELS = {
        "gym": "academia no condominio",
        "pool": "piscina no condominio",
        "court": "quadra no condominio",
        "parks": "parques no condominio",
        "party_spaces": "salao de festas",
        "concierge": "portaria concierge",
    }

    NEARBY_LABELS = {
        "R": "restaurante perto",
        "G": "academia perto",
        "S": "escola perto",
        "H": "hospital perto",
        "SM": "supermercado mercado perto",
        "P": "parque perto",
    }

    @classmethod
    def build(cls, property_obj) -> str:
        parts = [
            cls.PROPERTY_TYPE_LABELS.get(property_obj.type, ""),
            cls.PURPOSE_LABELS.get(property_obj.property_purpose, ""),
            property_obj.description,
            property_obj.address,
            property_obj.neighborhood,
            property_obj.city,
            f"{property_obj.area} metros quadrados",
            f"{cls._format_decimal(property_obj.price)} reais",
            "mobiliado" if property_obj.has_mobilia else "sem mobilia",
        ]

        rooms = getattr(property_obj, "rooms", None)
        if rooms:
            parts.extend(
                [
                    f"{rooms.bedrooms} quartos",
                    f"{rooms.bathrooms} banheiros",
                    f"{rooms.parking_spots} vagas garagem",
                ]
            )

        extras = getattr(property_obj, "rooms_extras", None)
        if extras:
            parts.extend(
                label
                for field, label in cls.ROOM_EXTRA_LABELS.items()
                if getattr(extras, field, False)
            )

        condo = getattr(property_obj, "condo", None)
        if condo:
            parts.extend([condo.name, condo.address])
            parts.extend(
                label
                for field, label in cls.CONDO_LABELS.items()
                if getattr(condo, field, False)
            )

        nearby_places = getattr(property_obj, "nearby_places", None)
        if nearby_places is not None:
            parts.extend(
                f"{place.name} {cls.NEARBY_LABELS.get(place.category, '')}"
                for place in nearby_places.all()
            )

        subjective_attributes = getattr(property_obj, "subjective_attributes", None)
        if subjective_attributes is not None:
            parts.extend(
                attribute.attribute_token.replace(".", " ")
                for attribute in subjective_attributes.all()
                if attribute.strength_mean >= 0.5
            )

        return "\n".join(str(part) for part in parts if part not in (None, ""))

    @staticmethod
    def _format_decimal(value) -> str:
        if isinstance(value, Decimal):
            return format(value, "f")
        return str(value)
