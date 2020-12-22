# Generated by Django 2.2.12 on 2020-12-22 16:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("zgw_consumers", "0011_remove_service_extra"),
        ("core", "0015_objectrecord_geometry"),
    ]

    operations = [
        migrations.AlterField(
            model_name="objectrecord",
            name="correct",
            field=models.OneToOneField(
                blank=True,
                help_text="Object record which corrects the current record",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="corrected",
                to="core.ObjectRecord",
                verbose_name="correction for",
            ),
        ),
        migrations.CreateModel(
            name="ObjectType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(
                        help_text="Unique identifier (UUID4) of the OBJECTTYPE in Objecttypes API"
                    ),
                ),
                (
                    "_name",
                    models.CharField(
                        help_text="Cached name of the objecttype retrieved from the Objecttype API",
                        max_length=100,
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="object_types",
                        to="zgw_consumers.Service",
                    ),
                ),
            ],
            options={
                "unique_together": {("service", "uuid")},
            },
        ),
        migrations.AddField(
            model_name="object",
            name="object_type_fk",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="core.ObjectType",
            ),
            preserve_default=False,
        ),
    ]
