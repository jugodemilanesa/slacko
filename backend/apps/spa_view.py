"""Serve the SvelteKit SPA from spa_build."""

import mimetypes
import os

from django.http import HttpResponse, Http404
from django.views.generic import View

SPA_DIR = os.path.join(os.path.dirname(__file__), "..", "spa_build")


def guess_content_type(path):
    mime, _ = mimetypes.guess_type(path)
    return mime or "application/octet-stream"


class SpaView(View):
    """Serve static files if they exist, otherwise serve index.html (SPA fallback)."""

    def get(self, request, *args, **kwargs):
        path = kwargs.get("path", "")

        # Try to serve the exact file from spa_build
        if path:
            file_path = os.path.join(SPA_DIR, path)
            if os.path.isfile(file_path):
                content_type = guess_content_type(path)
                with open(file_path, "rb") as f:
                    return HttpResponse(f.read(), content_type=content_type)

        # SPA fallback: serve index.html
        index_path = os.path.join(SPA_DIR, "index.html")
        try:
            with open(index_path, "r") as f:
                return HttpResponse(f.read(), content_type="text/html")
        except FileNotFoundError:
            return HttpResponse("Frontend not built.", status=501)
