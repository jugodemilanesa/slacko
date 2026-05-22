# Adds the "llm" choice to Session.mode so sessions created from the LLM chat
# pass model validation. No schema change — just metadata on the field.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0002_session_enrichment_message_artifacts"),
    ]

    operations = [
        migrations.AlterField(
            model_name="session",
            name="mode",
            field=models.CharField(
                blank=True,
                choices=[
                    ("guided", "Guiado"),
                    ("free", "Libre"),
                    ("llm", "LLM"),
                ],
                max_length=10,
            ),
        ),
    ]
