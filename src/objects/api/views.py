from django.db import models

from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from vng_api_common.search import SearchMixin

from objects.core.models import Object, ObjectRecord
from objects.token.permissions import ObjectTypeBasedPermission

from .filters import ObjectFilterSet
from .mixins import GeoMixin
from .serializers import (
    HistoryRecordSerializer,
    ObjectSearchSerializer,
    ObjectSerializer,
)


class ObjectViewSet(SearchMixin, GeoMixin, viewsets.ModelViewSet):
    queryset = (
        Object.objects.select_related("object_type", "object_type__service")
        .prefetch_related("records")
        .order_by("-pk")
    )
    serializer_class = ObjectSerializer
    filterset_class = ObjectFilterSet
    lookup_field = "uuid"
    search_input_serializer_class = ObjectSearchSerializer
    permission_classes = [ObjectTypeBasedPermission]

    def get_queryset(self):
        base = super().get_queryset()

        if self.action not in ("list", "search"):
            return base

        return base.filter_for_date().filter_for_token(self.request.auth)

    @swagger_auto_schema(responses={"200": HistoryRecordSerializer(many=True)})
    @action(detail=True, methods=["get"], serializer_class=HistoryRecordSerializer)
    def history(self, request, uuid=None):
        records = self.get_object().records.order_by("id")
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def search(self, request):
        """Perform a (geo) search on Objects"""
        search_input = self.get_search_input()

        within = search_input["geometry"]["within"]
        queryset = (
            self.filter_queryset(self.get_queryset())
            .filter(records__geometry__within=within)
            .distinct()
        )

        return self.get_search_output(queryset)

    def get_search_output(self, queryset: models.QuerySet) -> Response:
        """wrapper to make sure the result is a Response subclass"""
        result = super().get_search_output(queryset)

        if not isinstance(result, Response):
            result = Response(result)

        return result

    search.is_search_action = True
