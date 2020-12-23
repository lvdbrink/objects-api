import datetime

from django.db import models

from vng_api_common.utils import get_uuid_from_path
from zgw_consumers.models import Service


class ObjectTypeQuerySet(models.QuerySet):
    def get_by_url(self, url):
        service = Service.get_service(url)
        uuid = get_uuid_from_path(url)
        return self.get(service=service, uuid=uuid)


class ObjectQuerySet(models.QuerySet):
    def filter_for_token(self, token):
        if not token:
            return self.none()
        allowed_object_types = token.permissions.values("object_type")
        return self.filter(object_type__in=models.Subquery(allowed_object_types))

    def filter_for_date(self, date=None):
        actual_date = date or datetime.date.today()
        return (
            self.filter(records__start_date__lte=actual_date)
            .filter(
                models.Q(records__end_date__gte=actual_date)
                | models.Q(records__end_date__isnull=True)
            )
            .distinct()
        )
