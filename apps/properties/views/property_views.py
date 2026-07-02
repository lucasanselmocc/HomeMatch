from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.properties.models import Properties, Reviews
from apps.properties.filters import PropertiesFilters
from apps.properties.serializers.property_serializers import (
    PropertiesWriteSerializer,
    PropertiesReadSerializer,
)
from apps.properties.serializers.reviews_serializers import ReviewsSerializer
from apps.properties.permissions import (
    IsAdvertiser,
    IsReviewOwner,
    IsPropertyOwner,
)
from apps.properties.tasks import search_nearby_places
from apps.properties.services import NomatimService
from apps.properties.pagination import HomeMatchPagination
from apps.properties.strategies import ReviewUseCase

from config.homematch_framework import get_homematch_framework


class CreateListReviewPropertyView(generics.ListCreateAPIView):
    serializer_class = ReviewsSerializer
    pagination_class = HomeMatchPagination

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return ReviewUseCase.get_reviews_for_property(self.kwargs["pk"])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["property_id"] = self.kwargs["pk"]
        return context

    def perform_create(self, serializer):
        property_obj = get_object_or_404(Properties, pk=self.kwargs["pk"])
        serializer.save(user=self.request.user, property=property_obj)


class RUDReviewPropertyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer
    lookup_url_kwarg = "review_pk"

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated(), IsReviewOwner()]
        return [AllowAny()]


class CreateListPropertyView(generics.ListCreateAPIView):
    filterset_class = PropertiesFilters
    pagination_class = HomeMatchPagination

    def get_queryset(self):
        return get_homematch_framework().posts.list_posts()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        should_match = request.query_params.get("match") == "true"

        if should_match and request.user.is_authenticated:
            queryset = get_homematch_framework().match_score.rank_matches(
                targets=list(queryset),
                user=request.user,
                query_params=request.query_params,
            )

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PropertiesWriteSerializer
        return PropertiesReadSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdvertiser()]
        return [AllowAny()]

    def perform_create(self, serializer):
        property_obj = get_homematch_framework().posts.create_post(
            owner=self.request.user,
            validated_data=serializer.validated_data,
        )

        NomatimService.geocode(property_obj)

        if property_obj.latitude and property_obj.longitude:
            search_nearby_places.delay(property_obj.id)


class RUDPropertyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Properties.objects.all()
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return PropertiesWriteSerializer
        return PropertiesReadSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated(), IsPropertyOwner()]
        return [AllowAny()]

    def perform_update(self, serializer):
        property_obj = self.get_object()

        get_homematch_framework().posts.update_post(
            post=property_obj,
            validated_data=serializer.validated_data,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        get_homematch_framework().posts.delete_post(post=instance)

        return Response(
            {"message": "Delete successful!"},
            status=status.HTTP_204_NO_CONTENT,
        )


class SearchPropertyAIView(APIView):
    pass