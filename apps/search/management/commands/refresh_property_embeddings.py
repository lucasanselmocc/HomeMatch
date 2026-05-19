from django.core.management.base import BaseCommand

from apps.properties.models import Properties
from apps.search.embeddings import EmbeddingService


class Command(BaseCommand):
    help = "Regenerates semantic search embeddings for active properties."

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Refresh inactive properties too.",
        )

    def handle(self, *args, **options):
        queryset = (
            Properties.objects.select_related("rooms", "rooms_extras", "condo", "owner")
            .prefetch_related("nearby_places", "subjective_attributes")
            .order_by("id")
        )
        if not options["all"]:
            queryset = queryset.filter(status=True)

        total = queryset.count()
        for index, property_obj in enumerate(queryset.iterator(), start=1):
            EmbeddingService.refresh_property_embedding(property_obj)
            self.stdout.write(f"[{index}/{total}] property {property_obj.id} refreshed")

        self.stdout.write(self.style.SUCCESS(f"Refreshed {total} property embeddings."))
