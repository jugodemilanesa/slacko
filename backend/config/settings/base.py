"""Base settings for Slacko project."""

import os
from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
)
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# --- Apps ---

DJANGO_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "channels",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "dj_rest_auth",
    "dj_rest_auth.registration",
]

LOCAL_APPS = [
    "apps.accounts",
    "apps.chat",
    "apps.theory",
    "apps.solver",
    "apps.formulation",
    "apps.orchestrator",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# --- Middleware ---

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # allauth >=0.56 requires this middleware. It must come AFTER auth.
    "allauth.account.middleware.AccountMiddleware",
]

SITE_ID = 1

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# --- Database ---

DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres://slacko:slacko@localhost:5432/slacko"),
}

# --- Auth ---

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- i18n ---

LANGUAGE_CODE = "es"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True

# --- Static ---

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- DRF ---

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

# --- JWT ---

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# --- dj-rest-auth + allauth ---

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# allauth ≥65 settings. The legacy ACCOUNT_EMAIL_REQUIRED / ACCOUNT_UNIQUE_EMAIL
# were removed; email being required + unique is now expressed via the
# ACCOUNT_SIGNUP_FIELDS "email*" marker and uniqueness constraints on the model.
ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_SIGNUP_FIELDS = ["username*", "email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "optional"

REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_HTTPONLY": False,  # frontend reads the JWT from the JSON body
    "SESSION_LOGIN": False,
    # JWT-only: disable the default DRF Token model so dj-rest-auth doesn't
    # require `rest_framework.authtoken` in INSTALLED_APPS.
    "TOKEN_MODEL": None,
    "REGISTER_SERIALIZER": "apps.accounts.serializers.RegisterSerializer",
    "USER_DETAILS_SERIALIZER": "apps.accounts.serializers.UserSerializer",
}

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": env("GOOGLE_OAUTH_CLIENT_ID", default=""),
            "secret": env("GOOGLE_OAUTH_CLIENT_SECRET", default=""),
            "key": "",
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "OAUTH_PKCE_ENABLED": True,
    },
}

# Frontend URL used in password-reset emails and OAuth callbacks.
FRONTEND_BASE_URL = env("FRONTEND_BASE_URL", default="http://localhost:5173")

# --- CORS ---

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:5173"],
)

# --- Channels ---

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# --- LLM (provider-agnostic via LiteLLM Router) ---

# Fallback chain. Cualquier entrada con `api_key` vacía se skipea. Si TODAS
# están vacías, el orquestador opera en modo determinístico (solo wiki).
#
# Campos por provider:
#   name       — id interno, aparece en logs y en Message.metadata.provider
#   model      — string con prefijo de LiteLLM (gemini/..., groq/..., etc.)
#   api_key    — la key
#   api_base   — opcional, para providers OpenAI-compatibles con URL custom
#   rpm        — techo RPM real del free tier (usado por quota tracking)
#   rpd        — techo RPD real del free tier (opcional, None = sin tracking diario)
LLM_PROVIDERS = [
    {
        "name": "gemini",
        "model": env("GEMINI_MODEL", default="gemini/gemini-2.5-flash"),
        "api_key": env("GEMINI_API_KEY", default=""),
        "rpm": 10,
        "rpd": 1500,
        # Gemini 2.5 Flash thinking-mode a veces emite la tool call como texto
        # (`tool_code print(default_api.foo(...))`) en vez de un tool_call
        # estructurado. `reasoning_effort="none"` mapea a thinkingBudget=0 +
        # includeThoughts=False en LiteLLM, lo que evita esa fuga.
        "extra_params": {"reasoning_effort": "none"},
    },
    {
        "name": "groq",
        "model": env("GROQ_MODEL", default="groq/llama-3.3-70b-versatile"),
        "api_key": env("GROQ_API_KEY", default=""),
        "rpm": 30,
        "rpd": 14400,
    },
    {
        # Cerebras — Llama 3.3 70B muy rápido en su tier gratis.
        # https://inference-docs.cerebras.ai/quickstart
        "name": "cerebras",
        "model": env("CEREBRAS_MODEL", default="cerebras/llama-3.3-70b"),
        "api_key": env("CEREBRAS_API_KEY", default=""),
        "rpm": 30,
        "rpd": 14400,
    },
    {
        # SambaNova — Llama 3.1 405B en free tier.
        # https://cloud.sambanova.ai
        "name": "sambanova",
        "model": env(
            "SAMBANOVA_MODEL", default="sambanova/Meta-Llama-3.1-405B-Instruct"
        ),
        "api_key": env("SAMBANOVA_API_KEY", default=""),
        "rpm": 10,
        "rpd": None,
    },
    {
        # Z.ai (Zhipu) — GLM-4.6, OpenAI-compatible vía base custom.
        # https://docs.z.ai/guides/llm/glm-4.6
        # Lo registramos vía el adapter "openai/" de LiteLLM + api_base.
        "name": "zai",
        "model": env("ZAI_MODEL", default="openai/glm-4.6"),
        "api_key": env("ZAI_API_KEY", default=""),
        "api_base": env("ZAI_API_BASE", default="https://api.z.ai/api/paas/v4/"),
        "rpm": None,
        "rpd": None,
    },
    {
        "name": "openrouter",
        "model": env(
            "OPENROUTER_MODEL",
            default="openrouter/meta-llama/llama-3.3-70b-instruct:free",
        ),
        "api_key": env("OPENROUTER_API_KEY", default=""),
        "rpm": 20,
        "rpd": None,
    },
]

# Number of hops (tool-call cycles) the orchestrator will run per user turn.
LLM_MAX_HOPS = env.int("LLM_MAX_HOPS", default=5)
LLM_TEMPERATURE = env.float("LLM_TEMPERATURE", default=0.3)

# Rate-limiting del chat — protege la API key compartida. Defaults pensados
# para el tier gratis de Gemini (10 RPM, 1.500 RPD por key) con margen.
# Si querés liberar después del demo, levantá estos números o desactivá
# pasando 0 (no recomendado en producción).
LLM_THROTTLE_USER_PER_MINUTE = env.int("LLM_THROTTLE_USER_PER_MINUTE", default=6)
LLM_THROTTLE_USER_PER_HOUR = env.int("LLM_THROTTLE_USER_PER_HOUR", default=60)
LLM_THROTTLE_GLOBAL_PER_MINUTE = env.int("LLM_THROTTLE_GLOBAL_PER_MINUTE", default=9)

# --- Wiki / RAG ---

WIKI_DIR = env("WIKI_DIR", default=str(BASE_DIR.parent / "data" / "wiki"))
BIBLIOGRAPHY_DIR = BASE_DIR.parent / "data" / "bibliography"
