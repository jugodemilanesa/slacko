from django.contrib import admin

from .models import Message, Session


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("id", "role", "content", "created_at")


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "mode", "state", "created_at")
    list_filter = ("mode", "state")
    inlines = [MessageInline]
