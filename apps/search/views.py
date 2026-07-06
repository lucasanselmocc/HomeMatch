from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.properties.serializers.property_serializers import PropertiesReadSerializer
from apps.search.serializers import NaturalSearchRequestSerializer
from config.homematch_framework import get_homematch_framework


class SearchNaturalView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = NaturalSearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        results = get_homematch_framework().search.search_posts(
            query=serializer.validated_data["query"],
        )

        results_serializer = PropertiesReadSerializer(
            results,
            many=True,
            context={"request": request},
        )

        return Response(
            {
                "query": serializer.validated_data["query"],
                "results": results_serializer.data,
            }
        )