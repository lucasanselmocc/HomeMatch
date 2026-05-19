import json
import re
from decimal import Decimal, InvalidOperation
from django.conf import settings

from apps.ai_analysis.schema import VALID_TOKENS
from apps.search.embeddings import EmbeddingService
from apps.search.repositories import SearchRepository
from apps.search.serializers import NaturalSearchCriteriaSerializer

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


PROPERTY_TYPE_MAP = {
    "apartment": "A",
    "apartamento": "A",
    "apartamentos": "A",
    "ap": "A",
    "apt": "A",
    "casa": "H",
    "casas": "H",
    "house": "H",
}

NEARBY_CATEGORY_MAP = {
    "restaurant": "R",
    "restaurante": "R",
    "restaurantes": "R",
    "gym": "G",
    "academia": "G",
    "academias": "G",
    "school": "S",
    "escola": "S",
    "escolas": "S",
    "hospital": "H",
    "hospitais": "H",
    "supermarket": "SM",
    "supermercado": "SM",
    "mercado": "SM",
    "mercados": "SM",
    "park": "P",
    "parque": "P",
    "parques": "P",
}

ATTRIBUTE_KEYWORDS = {
    "iluminado": "aesthetics.color.brightness",
    "iluminada": "aesthetics.color.brightness",
    "claro": "aesthetics.color.brightness",
    "clara": "aesthetics.color.brightness",
    "aconchegante": "livability.coziness",
    "confortavel": "livability.coziness",
    "verde": "livability.verdancy",
    "plantas": "livability.verdancy",
    "amplo": "livability.spaciousness",
    "ampla": "livability.spaciousness",
    "espacoso": "livability.spaciousness",
    "espacosa": "livability.spaciousness",
    "ventilado": "current_state.ventilation",
    "ventilada": "current_state.ventilation",
    "limpo": "current_state.cleanliness",
    "limpa": "current_state.cleanliness",
    "lazer": "current_state.leisure",
    "moderno": "aesthetics.architecture.contemporary",
    "moderna": "aesthetics.architecture.contemporary",
    "minimalista": "aesthetics.architecture.minimalist",
}


class NaturalLanguageQueryInterpreter:
    """Turns a free-text real-estate search query into structured criteria."""

    EMPTY_RESULT = {
        "property_type": None,
        "min_price": None,
        "max_price": None,
        "city": None,
        "neighborhood": None,
        "bedrooms": None,
        "bathrooms": None,
        "parking_spots": None,
        "desired_attributes": [],
        "nearby_categories": [],
    }

    RESPONSE_FORMAT = {
        "type": "json_schema",
        "json_schema": {
            "name": "natural_search_filters",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "required": list(EMPTY_RESULT.keys()),
                "properties": {
                    "property_type": {"type": ["string", "null"], "enum": ["A", "H", None]},
                    "min_price": {"type": ["number", "null"]},
                    "max_price": {"type": ["number", "null"]},
                    "city": {"type": ["string", "null"]},
                    "neighborhood": {"type": ["string", "null"]},
                    "bedrooms": {"type": ["integer", "null"]},
                    "bathrooms": {"type": ["integer", "null"]},
                    "parking_spots": {"type": ["integer", "null"]},
                    "desired_attributes": {
                        "type": "array",
                        "items": {"type": "string", "enum": sorted(VALID_TOKENS)},
                    },
                    "nearby_categories": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["R", "G", "S", "H", "SM", "P"]},
                    },
                },
            },
        },
    }

    @classmethod
    def interpret(cls, query: str) -> dict:
        query = (query or "").strip()
        if not query:
            return cls._validate(cls.EMPTY_RESULT.copy())

        if OpenAI is None or not getattr(settings, "AI_API_KEY", None):
            return cls._rule_based_interpret(query)

        try:
            return cls._validate(cls._normalize(cls._llm_interpret(query)))
        except Exception:
            return cls._rule_based_interpret(query)

    @classmethod
    def _llm_interpret(cls, query: str) -> dict:
        client = OpenAI(
            base_url=getattr(settings, "AI_API_BASE_URL", None),
            api_key=settings.AI_API_KEY,
        )
        response = client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You extract structured real-estate search criteria from "
                        "Brazilian Portuguese or English user queries. Return only "
                        "the JSON requested by the schema. Use null when unknown. "
                        "Use property_type A for apartment and H for house."
                    ),
                },
                {"role": "user", "content": query},
            ],
            response_format=cls.RESPONSE_FORMAT,
            temperature=0,
        )
        content = response.choices[0].message.content
        return json.loads(content)

    @classmethod
    def _rule_based_interpret(cls, query: str) -> dict:
        normalized = cls._strip_accents(query.lower())
        result = cls.EMPTY_RESULT.copy()

        for token, property_type in PROPERTY_TYPE_MAP.items():
            if re.search(rf"\b{re.escape(token)}\b", normalized):
                result["property_type"] = property_type
                break

        result["bedrooms"] = cls._extract_number_before(
            normalized, ["quarto", "quartos", "dormitorio", "dormitorios"]
        )
        result["bathrooms"] = cls._extract_number_before(
            normalized, ["banheiro", "banheiros"]
        )
        result["parking_spots"] = cls._extract_number_before(
            normalized, ["vaga", "vagas", "garagem"]
        )
        result["max_price"] = cls._extract_max_price(normalized)

        result["desired_attributes"] = sorted(
            {
                attribute
                for keyword, attribute in ATTRIBUTE_KEYWORDS.items()
                if re.search(rf"\b{re.escape(keyword)}\b", normalized)
            }
        )
        result["nearby_categories"] = sorted(
            {
                category
                for keyword, category in NEARBY_CATEGORY_MAP.items()
                if re.search(rf"\b{re.escape(keyword)}\b", normalized)
            }
        )

        return cls._validate(cls._normalize(result))

    @classmethod
    def _normalize(cls, data: dict) -> dict:
        result = cls.EMPTY_RESULT.copy()
        result.update(data or {})

        result["property_type"] = cls._normalize_property_type(result["property_type"])
        result["min_price"] = cls._normalize_decimal(result["min_price"])
        result["max_price"] = cls._normalize_decimal(result["max_price"])
        result["bedrooms"] = cls._normalize_int(result["bedrooms"])
        result["bathrooms"] = cls._normalize_int(result["bathrooms"])
        result["parking_spots"] = cls._normalize_int(result["parking_spots"])
        result["desired_attributes"] = [
            item for item in result["desired_attributes"] if item in VALID_TOKENS
        ]
        result["nearby_categories"] = [
            item
            for item in result["nearby_categories"]
            if item in {"R", "G", "S", "H", "SM", "P"}
        ]

        for key in ("city", "neighborhood"):
            value = result[key]
            result[key] = value.strip() if isinstance(value, str) and value.strip() else None

        return result

    @staticmethod
    def _validate(data: dict) -> dict:
        serializer = NaturalSearchCriteriaSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    @staticmethod
    def _normalize_property_type(value):
        if value in {"A", "H", None}:
            return value
        return PROPERTY_TYPE_MAP.get(str(value).strip().lower())

    @staticmethod
    def _normalize_decimal(value):
        if value in (None, ""):
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return None

    @staticmethod
    def _normalize_int(value):
        if value in (None, ""):
            return None
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return None
        return parsed if parsed >= 0 else None

    @staticmethod
    def _extract_number_before(query, words):
        pattern = rf"(\d+)\s+(?:{'|'.join(re.escape(word) for word in words)})"
        match = re.search(pattern, query)
        return int(match.group(1)) if match else None

    @staticmethod
    def _extract_max_price(query):
        match = re.search(
            r"(?:ate|menos de|no maximo)\s+r?\$?\s*(\d+(?:[.,]\d+)?)\s*(milhao|milhoes|mil|k)?",
            query,
        )
        if not match:
            return None

        value = Decimal(match.group(1).replace(",", "."))
        suffix = match.group(2)
        if suffix in {"milhao", "milhoes"}:
            value *= Decimal("1000000")
        elif suffix in {"mil", "k"}:
            value *= Decimal("1000")
        return value

    @staticmethod
    def _strip_accents(value: str) -> str:
        translation = str.maketrans(
            "áàãâäéèêëíìîïóòõôöúùûüç",
            "aaaaaeeeeiiiiooooouuuuc",
        )
        return value.translate(translation)


def query_interpreter(query: str) -> dict:
    return NaturalLanguageQueryInterpreter.interpret(query)


def query_interpretor(query: str) -> dict:
    return query_interpreter(query)


class NaturalSearchService:
    @staticmethod
    def search(query: str):
        criteria = NaturalLanguageQueryInterpreter.interpret(query)
        query_embedding = EmbeddingService.embed_text(query)
        queryset = SearchRepository.filter_properties(criteria)
        results = SearchRepository.rank_properties_by_embedding(
            query_embedding,
            queryset,
        )
        return {
            "interpreted_filters": criteria,
            "results": results,
        }
