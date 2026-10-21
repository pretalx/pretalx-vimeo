from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("pretalx_vimeo", "0002_data")]

    operations = [
        migrations.AddField(
            model_name="vimeolink",
            name="video_hash",
            field=models.CharField(blank=True, default="", max_length=20),
        )
    ]
