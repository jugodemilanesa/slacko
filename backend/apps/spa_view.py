"""Serve the SvelteKit SPA from spa_build."""

import os

from django.http import HttpResponse, Http404
from django.views.generic import View

SPA_DIR = os.path.join(os.path.dirname(__file__), "..", "spa_build")

ALLOWED_PREFIXES = ("_app/", "_immutable/")


class SpaView(View):
    """Serve index.html for SPA routes, static assets for /_app/ etc."""

    def get(self, request, *args, **kwargs):
        path = kwargs.get("path", "")

        # Serve static assets from the SPA build (_app/, _immutable/, etc.)
        if any(path.startswith(p) for p in ALLOWED_PREFIXES):
            file_path = os.path.join(SPA_DIR, path)
            if os.path.isfile(file_path):
                content_type = "application/javascript"
                if path.endswith(".css"):
                    content_type = "text/css"
                elif path.endswith(".svg"):
                    content_type = "image/svg+xml"
                elif path.endswith(".png"):
                    content_type = "image/png"
                elif path.endswith(".woff2"):
                    content_type = "font/woff2"
                elif path.endswith(".woff"):
                    content_type = "font/woff"
                elif path.endswith(".ttf"):
                    content_type = "font/ttf"
                with open(file_path, "rb") as f:
                    return HttpResponse(f.read(), content_type=content_type)
            raise Http404

        # Everything else: serve index.html (SPA fallback)
        index_path = os.path.join(SPA_DIR, "index.html")
        try:
            with open(index_path, "r") as f:
                return HttpResponse(f.read(), content_type="text/html")
        except FileNotFoundError:
            return HttpResponse("Frontend not built.", status=501)
