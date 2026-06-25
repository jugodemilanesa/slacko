"""Custom authentication classes."""

from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """SessionAuthentication sin enforcement de CSRF.

    En el deploy split (frontend en Vercel, backend en otro dominio) el JS del
    frontend no puede leer la cookie ``csrftoken`` del backend —vive en otro
    origen—, así que el header ``X-CSRFToken`` nunca llega y el chequeo CSRF de
    Django rechazaría todo POST (incluido el login). Deshabilitamos ese chequeo
    y nos apoyamos en la lista blanca de CORS (``CORS_ALLOWED_ORIGINS``) + la
    cookie de sesión ``SameSite=None; Secure`` para acotar el riesgo.
    """

    def enforce_csrf(self, request):  # noqa: D102
        return  # no-op: ver docstring
