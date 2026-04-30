from django.contrib import admin

from .models import DocumentChunk


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ("source_file", "page_number", "chunk_index", "created_at")
    list_filter = ("source_file",)
    search_fields = ("content",)
