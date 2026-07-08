"""
apps/properties/strategies.py
─────────────────────────────
Strategies concretas do HomeMatch para o domínio imobiliário.
"""

from __future__ import annotations

from collections import Counter
from decimal import Decimal
from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg

from apps.properties.models import Condo, Properties, PropertiesPhotos, Reviews, Rooms, RoomsExtras
from apps.properties.services import delete_from_cloud, upload_to_cloud
from framework.abstractions.abstract_match_score_strategy import (
    AbstractMatchScoreStrategy,
)


class HomeMatchMatchScoreStrategy(AbstractMatchScoreStrategy):
    """
    Estratégia concreta de cálculo de match-score para imóveis.

    Esta classe adapta a regra original do HomeMatch para o contrato
    esperado pelo framework.
    """

    FILTER_TO_SCORE_FIELDS = {
        "type": {"property_type"},
        "city": {"city"},
        "neighborhood": {"neighborhood"},
        "min_price": {"min_price"},
        "max_price": {"max_price"},
    }

    def calculate(self, user: Any, posts: list[Any]) -> list[tuple[Any, int]]:
        """
        Calcula o match-score entre um usuário e uma lista de imóveis.
        """
        scores: list[tuple[Any, int]] = []

        try:
            preferences = user.preferences
        except ObjectDoesNotExist:
            preferences = None

        favorite_profile = self._favorite_profile(user)

        for target in posts:
            current_filters = self._current_filters(None)
            ignored_score_fields = self._ignored_score_fields(current_filters.keys())
            score = self._calculate_match_score(
                target,
                preferences=preferences,
                ignored_score_fields=ignored_score_fields,
                favorite_profile=favorite_profile,
            )
            scores.append((target, score))

        return scores

    def rank(
        self,
        *,
        targets: list[Any],
        user: Any,
        query_params: dict | None = None,
    ) -> list[Any]:
        """
        Calcula o match-score de uma lista de imóveis e ordena pelo maior score.
        """
        try:
            preferences = user.preferences
        except ObjectDoesNotExist:
            preferences = None

        favorite_profile = self._favorite_profile(user)
        current_filters = self._current_filters(query_params)
        ignored_score_fields = self._ignored_score_fields(current_filters.keys())

        for target in targets:
            target.match_score = self._calculate_match_score(
                target,
                preferences=preferences,
                ignored_score_fields=ignored_score_fields,
                favorite_profile=favorite_profile,
            )

        return sorted(targets, key=lambda item: item.match_score, reverse=True)

    def persist(self, user: Any, scores: list[tuple[Any, int]]) -> None:
        """
        Persistência de scores é opcional neste domínio.

        O framework exige o método, mas a versão atual armazena o
        resultado em memória como anotação no objeto de propriedade.
        """
        for post, score in scores:
            post.match_score = score

    def _calculate_match_score(
        self,
        property_obj: Any,
        *,
        preferences: Any = None,
        ignored_score_fields: set[str] | None = None,
        favorite_profile: dict | None = None,
    ) -> int:
        weighted_scores = []

        if preferences:
            preference_score = self._preference_score(
                property_obj,
                preferences,
                ignored_score_fields=ignored_score_fields or set(),
            )
            if preference_score is not None:
                weighted_scores.append((preference_score, 45))

        if favorite_profile:
            weighted_scores.append(
                (
                    self._favorite_profile_score(property_obj, favorite_profile),
                    40,
                )
            )

        popularity_score = self._popularity_score(property_obj)

        if weighted_scores:
            weighted_scores.append((popularity_score, 15))
            total_weight = sum(weight for _, weight in weighted_scores)
            return round(
                sum(score * weight for score, weight in weighted_scores) / total_weight
            )

        return popularity_score

    def _preference_score(
        self,
        property_obj: Any,
        preferences: Any,
        *,
        ignored_score_fields: set[str],
    ) -> int | None:
        total_weight = 0
        earned = 0

        rules = [
            (
                "property_type",
                preferences.property_type,
                25,
                property_obj.type == preferences.property_type,
            ),
            (
                "city",
                preferences.city,
                20,
                self._same_text(property_obj.city, preferences.city),
            ),
            (
                "neighborhood",
                preferences.neighborhood,
                15,
                self._same_text(property_obj.neighborhood, preferences.neighborhood),
            ),
        ]

        for field_name, expected, weight, matched in rules:
            if field_name not in ignored_score_fields and expected:
                total_weight += weight
                if matched:
                    earned += weight

        if "min_price" not in ignored_score_fields and preferences.min_price is not None:
            total_weight += 15
            if property_obj.price >= preferences.min_price:
                earned += 15

        if "max_price" not in ignored_score_fields and preferences.max_price is not None:
            total_weight += 25
            if property_obj.price <= preferences.max_price:
                earned += 25
            elif property_obj.price <= preferences.max_price * Decimal("1.1"):
                earned += 10

        if total_weight == 0:
            return None

        return round((earned / total_weight) * 100)

    def _favorite_profile(self, user: Any) -> dict | None:
        favorites = list(
            user.favorites.select_related("rooms").only(
                "type",
                "city",
                "neighborhood",
                "price",
                "rooms__id",
            )
        )

        if not favorites:
            return None

        type_counter = Counter(item.type for item in favorites if item.type)
        city_counter = Counter(
            self._normalize_text(item.city) for item in favorites if item.city
        )
        neighborhood_counter = Counter(
            self._normalize_text(item.neighborhood)
            for item in favorites
            if item.neighborhood
        )
        prices = [item.price for item in favorites if item.price is not None]

        return {
            "favorite_type": self._most_common(type_counter),
            "favorite_city": self._most_common(city_counter),
            "favorite_neighborhoods": {
                value for value, _ in neighborhood_counter.most_common(3)
            },
            "average_price": sum(prices) / len(prices) if prices else None,
        }

    def _favorite_profile_score(self, property_obj: Any, profile: dict) -> int:
        total_weight = 0
        earned = 0

        rules = [
            (
                profile["favorite_type"],
                25,
                property_obj.type == profile["favorite_type"],
            ),
            (
                profile["favorite_city"],
                20,
                self._normalize_text(property_obj.city) == profile["favorite_city"],
            ),
            (
                profile["favorite_neighborhoods"],
                20,
                self._normalize_text(property_obj.neighborhood)
                in profile["favorite_neighborhoods"],
            ),
        ]

        for expected, weight, matched in rules:
            if expected:
                total_weight += weight
                if matched:
                    earned += weight

        average_price = profile["average_price"]

        if average_price:
            total_weight += 35
            price_distance = abs(property_obj.price - average_price) / average_price

            if price_distance <= Decimal("0.10"):
                earned += 35
            elif price_distance <= Decimal("0.20"):
                earned += 25
            elif price_distance <= Decimal("0.35"):
                earned += 10

        if total_weight == 0:
            return 0

        return round((earned / total_weight) * 100)

    def _popularity_score(self, property_obj: Any) -> int:
        favorite_count = getattr(property_obj, "favorite_count", 0) or 0
        average_rating = getattr(property_obj, "average_rating", None) or 0

        rating_score = min(float(average_rating), 5.0) / 5 * 70
        favorite_score = min(favorite_count, 10) / 10 * 30

        return round(rating_score + favorite_score)

    def _same_text(self, value: Any, expected: Any) -> bool:
        if value is None or expected is None:
            return False

        return self._normalize_text(value) == self._normalize_text(expected)

    def _normalize_text(self, value: Any) -> str:
        return str(value).strip().lower()

    def _ignored_score_fields(self, query_params) -> set[str]:
        ignored = set()

        for filter_name in query_params or []:
            ignored.update(self.FILTER_TO_SCORE_FIELDS.get(filter_name, set()))

        return ignored

    def _current_filters(self, query_params: dict | None) -> dict:
        if not query_params:
            return {}

        return {
            name: query_params.get(name)
            for name in self.FILTER_TO_SCORE_FIELDS
            if query_params.get(name) not in (None, "")
        }

    def _most_common(self, counter: Counter) -> Any:
        if not counter:
            return None

        return counter.most_common(1)[0][0]


class PropertyUseCase:
    @staticmethod
    def create_property(validated_data: dict) -> Properties:
        from apps.properties.repositories import PropertyRepository

        return PropertyRepository().create_post(owner=None, validated_data=validated_data)

    @staticmethod
    def update_property(instance: Properties, validated_data: dict) -> Properties:
        from apps.properties.repositories import PropertyRepository

        return PropertyRepository().update_post(post=instance, validated_data=validated_data)


class PhotoUseCase:
    @staticmethod
    def create_photo(property_obj: Properties, validated_data: dict) -> PropertiesPhotos:
        from apps.properties.repositories import PhotoRepository

        return PhotoRepository().create_photo(
            post=property_obj,
            image=validated_data["image"],
            order=validated_data.get("order", 0),
        )

    @staticmethod
    def update_photo(instance: PropertiesPhotos, validated_data: dict) -> PropertiesPhotos:
        from apps.properties.repositories import PhotoRepository

        repo = PhotoRepository()
        new_image = validated_data.get("image")

        if new_image is not None:
            return repo.replace_photo_image(instance, new_image)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        return repo.save_photo(instance)


class ReviewUseCase:
    @staticmethod
    def validate_unique_review(*, user: Any, property_id: int, instance: Any = None) -> bool:
        from apps.properties.repositories import ReviewRepository

        return not ReviewRepository.user_has_review_for_property(
            user=user,
            property_id=property_id,
            instance=instance,
        )

    @staticmethod
    def get_reviews_for_property(property_id: int):
        from apps.properties.repositories import ReviewRepository

        return ReviewRepository.review_queryset_for_property(property_id)

    @staticmethod
    def get_average_rating(property_obj: Properties) -> float | None:
        from apps.properties.repositories import ReviewRepository

        return ReviewRepository.average_rating_for_property(property_obj)
