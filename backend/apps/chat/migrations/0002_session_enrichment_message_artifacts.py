# Generated for the LLM-integration branch: Session sidebar fields +
# Message orchestrator artifacts. Written by hand so `docker compose up`
# can run `migrate --noinput` without an interactive `makemigrations`.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0001_initial"),
    ]

    operations = [
        # ── Session: history sidebar enrichment ──
        migrations.AddField(
            model_name="session",
            name="title",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="session",
            name="archived",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="session",
            name="pinned",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="session",
            name="tags",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterModelOptions(
            name="session",
            options={
                "ordering": ["-pinned", "-updated_at"],
                "verbose_name": "Sesión de chat",
                "verbose_name_plural": "Sesiones de chat",
            },
        ),
        migrations.AddIndex(
            model_name="session",
            index=models.Index(
                fields=["user", "archived"],
                name="idx_chat_sess_user_arch",
            ),
        ),
        migrations.AddIndex(
            model_name="session",
            index=models.Index(
                fields=["user", "-updated_at"],
                name="idx_chat_sess_user_upd",
            ),
        ),
        # ── Message: orchestrator artifacts ──
        migrations.AddField(
            model_name="message",
            name="tool_calls",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="message",
            name="citations",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="message",
            name="cost_tokens",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="message",
            name="parent_id_uuid",
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name="message",
            index=models.Index(
                fields=["session", "created_at"],
                name="idx_chat_msg_sess_created",
            ),
        ),
    ]
