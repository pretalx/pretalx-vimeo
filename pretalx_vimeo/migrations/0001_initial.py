# Generated by Django 3.2.4 on 2021-12-15 00:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("submission", "0062_cfp_settings_data"),
    ]

    operations = [
        migrations.CreateModel(
            name="VimeoLink",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("video_id", models.CharField(max_length=20)),
                (
                    "submission",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vimeo_link",
                        to="submission.submission",
                    ),
                ),
            ],
        ),
    ]
