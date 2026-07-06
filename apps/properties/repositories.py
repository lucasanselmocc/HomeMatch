from __future__ import annotations

from typing import Any, Optional

from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404

from apps.properties.models import Condo, Properties, PropertiesPhotos, Reviews, Rooms, RoomsExtras
from apps.properties.services import delete_from_cloud, upload_to_cloud
from apps.search.repositories import SearchRepository
from framework.abstractions.abstract_post_repository import AbstractPostRepository
from framework.abstractions.abstract_photo_repository import AbstractPhotoRepository


class PropertyRepository(AbstractPostRepository):
    """
    Repositório concreto de postagens do HomeMatch.

    No domínio imobiliário, uma postagem do framework corresponde
    a um imóvel cadastrado no Django.
    """

    def create_post(self, *, owner: Any, validated_data: dict) -> Any:
        rooms_data = validated_data.pop("rooms")
        rooms_extras_data = validated_data.pop("rooms_extras")
        condo_data = validated_data.pop("condo", None)

        rooms, _ = Rooms.objects.get_or_create(**rooms_data)
        rooms_extras, _ = RoomsExtras.objects.get_or_create(**rooms_extras_data)
        condo = None

        if condo_data:
            condo, _ = Condo.objects.get_or_create(**condo_data)

        validated_data.setdefault("embedding", "[]")

        return Properties.objects.create(
            owner=owner,
            rooms=rooms,
            rooms_extras=rooms_extras,
            condo=condo,
            **validated_data,
        )

    def update_post(self, *, post: Any, validated_data: dict) -> Any:
        rooms_data = validated_data.pop("rooms", None)
        rooms_extras_data = validated_data.pop("rooms_extras", None)
        condo_data = validated_data.pop("condo", None)

        if rooms_data:
            rooms, _ = Rooms.objects.get_or_create(**rooms_data)
            post.rooms = rooms

        if rooms_extras_data:
            rooms_extras, _ = RoomsExtras.objects.get_or_create(**rooms_extras_data)
            post.rooms_extras = rooms_extras

        if condo_data:
            condo, _ = Condo.objects.update_or_create(
                id=post.condo.id if post.condo else None,
                defaults=condo_data,
            )
            post.condo = condo

        for field, value in validated_data.items():
            setattr(post, field, value)

        post.save()
        return post

    def delete_post(self, post: Any) -> None:
        post.delete()

    def get_by_id(self, post_id: int) -> Optional[Any]:
        return Properties.objects.filter(id=post_id).first()

    def get_or_404(self, post_id: int) -> Any:
        return get_object_or_404(Properties, id=post_id)

    def list_posts(self) -> Any:
        return (
            Properties.objects.select_related("rooms", "rooms_extras", "condo", "owner")
            .prefetch_related("photos", "nearby_places")
            .annotate(
                average_rating=Avg("reviews__rating"),
                favorite_count=Count("favorited_by", distinct=True),
            )
            .order_by("created_at")
        )

    def save_post(self, post: Any) -> Any:
        post.save()
        return post

    def filter_posts(self, criteria: dict) -> list[Any]:
        return list(SearchRepository.filter_properties(criteria))

class PhotoRepository(AbstractPhotoRepository):
    """
    Repositório concreto de fotos do HomeMatch.

    No domínio imobiliário, uma foto pertence a um imóvel.
    """

    def create_photo(self, *, post: Any, image: Any, order: int) -> Any:
        r2_key = upload_to_cloud(image)

        try:
            return PropertiesPhotos.objects.create(
                property=post,
                r2_key=r2_key,
                order=order,
            )
        except Exception:
            delete_from_cloud(r2_key)
            raise

    def get_by_id(self, photo_id: int) -> Optional[Any]:
        return PropertiesPhotos.objects.filter(id=photo_id).first()

    def get_photo_by_id(self, photo_id: int) -> Optional[Any]:
        return self.get_by_id(photo_id)

    def delete_photo(self, photo: Any) -> None:
        delete_from_cloud(photo.r2_key)
        photo.delete()

    def list_by_post(self, post: Any) -> list[Any]:
        return list(PropertiesPhotos.objects.filter(property=post).order_by("order"))

    def list_photos_by_post(self, post: Any) -> list[Any]:
        return self.list_by_post(post)

    def save_photo(self, photo: Any) -> Any:
        photo.save()
        return photo

    def replace_photo_image(self, photo: Any, new_image: Any) -> Any:
        delete_from_cloud(photo.r2_key)
        photo.r2_key = upload_to_cloud(new_image)
        photo.save()
        return photo


# Compatibility alias used by config.homematch_framework
DjangoPostRepository = PropertyRepository

class ReviewRepository:
    @staticmethod
    def user_has_review_for_property(*, user, property_id, instance=None):
        queryset = Reviews.objects.filter(user=user, property_id=property_id)
        if instance:
            queryset = queryset.exclude(pk=instance.pk)
        return queryset.exists()

    @staticmethod
    def review_queryset_for_property(property_id):
        return Reviews.objects.filter(property_id=property_id).order_by("-created_at")

    @staticmethod
    def average_rating_for_property(property_obj):
        result = property_obj.reviews.aggregate(Avg("rating"))
        return result["rating__avg"]
