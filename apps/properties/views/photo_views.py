from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.properties.permissions import IsPropertyOwner
from apps.properties.models import Properties, PropertiesPhotos
from apps.properties.serializers.photo_serializers import (
    PropertiesUploadPhotosSerializer,
    PropertiesPhotosSerializer,
)
from config.homematch_framework import get_homematch_framework


class UploadPhotoPropertyView(generics.CreateAPIView):
    queryset = Properties.objects.all()
    permission_classes = [IsAuthenticated, IsPropertyOwner]
    serializer_class = PropertiesUploadPhotosSerializer
    lookup_field = "pk"

    def perform_create(self, serializer):
        property_obj = self.get_object()

        get_homematch_framework().photos.upload_photo(
            post=property_obj,
            validated_data=serializer.validated_data,
        )


class RUDPhotoPropertyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PropertiesPhotos.objects.all()
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return PropertiesUploadPhotosSerializer
        return PropertiesPhotosSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated(), IsPropertyOwner()]
        return [AllowAny()]

    def perform_update(self, serializer):
        photo = self.get_object()

        get_homematch_framework().photos.update_photo(
            photo=photo,
            validated_data=serializer.validated_data,
        )

    def perform_destroy(self, instance):
        get_homematch_framework().photos.delete_photo(photo=instance)