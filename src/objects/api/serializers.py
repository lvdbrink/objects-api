from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework_gis.serializers import GeometryField

from objects.core.models import Object, ObjectRecord, ObjectType

from .validators import CorrectionValidator, IsImmutableValidator, JsonSchemaValidator


class ObjectRecordSerializer(serializers.ModelSerializer):
    correctionFor = serializers.SlugRelatedField(
        source="correct",
        slug_field="uuid",
        queryset=ObjectRecord.objects.all(),
        required=False,
    )
    correctedBy = serializers.SlugRelatedField(
        source="corrected",
        slug_field="uuid",
        read_only=True,
    )

    class Meta:
        model = ObjectRecord
        fields = (
            "uuid",
            "typeVersion",
            "data",
            "geometry",
            "startDate",
            "endDate",
            "registrationDate",
            "correctionFor",
            "correctedBy",
        )
        extra_kwargs = {
            "uuid": {"read_only": True},
            "typeVersion": {"source": "version"},
            "startDate": {"source": "start_date"},
            "endDate": {"source": "end_date", "read_only": True},
            "registrationDate": {"source": "registration_date", "read_only": True},
        }


class HistoryRecordSerializer(serializers.ModelSerializer):
    correctionFor = serializers.SlugRelatedField(
        source="correct",
        slug_field="uuid",
        read_only=True,
    )
    correctedBy = serializers.SlugRelatedField(
        source="corrected",
        slug_field="uuid",
        read_only=True,
    )

    class Meta:
        model = ObjectRecord
        fields = (
            "uuid",
            "typeVersion",
            "data",
            "geometry",
            "startDate",
            "endDate",
            "registrationDate",
            "correctionFor",
            "correctedBy",
        )
        extra_kwargs = {
            "uuid": {"read_only": True},
            "typeVersion": {"source": "version"},
            "startDate": {"source": "start_date"},
            "endDate": {"source": "end_date", "read_only": True},
            "registrationDate": {"source": "registration_date", "read_only": True},
        }


class ObjectTypeField(serializers.RelatedField):
    default_error_messages = {
        "does_not_exist": _("ObjectType with url={value} is not configured."),
        "invalid": _("Invalid value."),
    }

    def to_internal_value(self, data):
        try:
            return self.get_queryset().get_by_url(data)
        except ObjectDoesNotExist:
            self.fail("does_not_exist", value=smart_text(data))
        except (TypeError, ValueError):
            self.fail("invalid")

    def to_representation(self, obj):
        return obj.url


class ObjectSerializer(serializers.HyperlinkedModelSerializer):
    type = ObjectTypeField(
        source="object_type",
        queryset=ObjectType.objects.all(),
        help_text=_("Url reference to OBJECTTYPE in Objecttypes API"),
        validators=[IsImmutableValidator()],
    )
    record = ObjectRecordSerializer(source="current_record")

    class Meta:
        model = Object
        fields = ("url", "type", "record")
        extra_kwargs = {"url": {"lookup_field": "uuid"}}
        validators = [JsonSchemaValidator(), CorrectionValidator()]

    @transaction.atomic
    def create(self, validated_data):
        record_data = validated_data.pop("current_record")
        object = super().create(validated_data)

        record_data["object"] = object
        ObjectRecordSerializer().create(record_data)
        return object

    @transaction.atomic
    def update(self, instance, validated_data):
        record_data = validated_data.pop("current_record", None)
        object = super().update(instance, validated_data)

        if record_data:
            record_data["object"] = object
            # in case of PATCH:
            if not record_data.get("version"):
                record_data["version"] = object.current_record.version
            ObjectRecordSerializer().create(record_data)
        return object


class GeoWithinSerializer(serializers.Serializer):
    within = GeometryField(required=False)


class ObjectSearchSerializer(serializers.Serializer):
    geometry = GeoWithinSerializer(required=True)
