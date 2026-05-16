import uuid

from django.db import models
from pgvector.django import VectorField


class DocumentChunk(models.Model):
    """A chunk of text from a bibliography PDF, with its embedding."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_file = models.CharField(max_length=255)
    page_number = models.IntegerField(null=True, blank=True)
    chunk_index = models.IntegerField()
    content = models.TextField()
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fragmento de documento"
        verbose_name_plural = "Fragmentos de documentos"
        ordering = ["source_file", "chunk_index"]

    def __str__(self) -> str:
        return f"{self.source_file} (p.{self.page_number}, chunk {self.chunk_index})"
