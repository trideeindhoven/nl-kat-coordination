"""
Django settings for rocky project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

import environ
from django.conf import locale
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _

from rocky.otel import OpenTelemetryHelper

env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(BASE_DIR / ".env")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

QUEUE_URI = env.url("QUEUE_URI", "").geturl()

OCTOPOES_API = env.url("OCTOPOES_API", "").geturl()

SCHEDULER_API = env.url("SCHEDULER_API", "").geturl()

KATALOGUS_API = env.url("KATALOGUS_API", "").geturl()

BYTES_API = env.url("BYTES_API", "").geturl()
BYTES_USERNAME = env("BYTES_USERNAME", default="")
BYTES_PASSWORD = env("BYTES_PASSWORD", default="")

KEIKO_API = env.url("KEIKO_API", "").geturl()
# Report generation timeout in seconds
KEIKO_REPORT_TIMEOUT = env.int("KEIKO_REPORT_TIMEOUT", 60)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", False)

# Make sure this header can never be set by an attacker, see also the security
# warning at https://docs.djangoproject.com/en/4.2/howto/auth-remote-user/
REMOTE_USER_HEADER = env("REMOTE_USER_HEADER", default=None)
REMOTE_USER_FALLBACK = env.bool("REMOTE_USER_FALLBACK", False)

if REMOTE_USER_HEADER:
    # Optional list of default organizations to add remote users to,
    # format: space separated list of ORGANIZATION_CODE:GROUP_NAME, e.g. `test:admin test2:redteam`
    REMOTE_USER_DEFAULT_ORGANIZATIONS = env.list("REMOTE_USER_DEFAULT_ORGANIZATIONS", default=[])
    AUTHENTICATION_BACKENDS = [
        "rocky.auth.remote_user.RemoteUserBackend",
    ]
    if REMOTE_USER_FALLBACK:
        AUTHENTICATION_BACKENDS += [
            "django.contrib.auth.backends.ModelBackend",
        ]

# SECURITY WARNING: enable two factor authentication in production!
TWOFACTOR_ENABLED = env.bool("TWOFACTOR_ENABLED", not REMOTE_USER_HEADER)

# A list of strings representing the host/domain names that this Django site can serve.
# https://docs.djangoproject.com/en/4.2/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])

SPAN_EXPORT_GRPC_ENDPOINT = env("SPAN_EXPORT_GRPC_ENDPOINT", default=None)
if SPAN_EXPORT_GRPC_ENDPOINT is not None:
    OpenTelemetryHelper.setup_instrumentation(SPAN_EXPORT_GRPC_ENDPOINT)

# -----------------------------
# EMAIL CONFIGURATION for SMTP
# -----------------------------
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_FILE_PATH = env.path("EMAIL_FILE_PATH", BASE_DIR / "rocky/email_logs")  # directory to store output files
EMAIL_HOST = env("EMAIL_HOST", default="localhost")  # localhost
try:
    EMAIL_PORT = env.int("EMAIL_PORT", default=25)
except ValueError:
    # We have an empty EMAIL_PORT= to rocky.conf in the Debian package. We
    # handle the empty string as default value here so we don't generate an
    # exception for this
    if env("EMAIL_PORT"):
        raise

    EMAIL_PORT = 25

EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="")
SERVER_EMAIL = env("SERVER_EMAIL", default="")
EMAIL_SUBJECT_PREFIX = env("EMAIL_SUBJECT_PREFIX", default="KAT - ")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", False)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", False)
EMAIL_SSL_CERTFILE = env("EMAIL_SSL_CERTFILE", default=None)
EMAIL_SSL_KEYFILE = env("EMAIL_SSL_KEYFILE", default=None)
EMAIL_TIMEOUT = 30  # 30 seconds
# ----------------------------

HELP_DESK_EMAIL = env("HELP_DESK_EMAIL", default="")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.forms",
    "django_otp",
    "django_otp.plugins.otp_static",
    "django_otp.plugins.otp_totp",
    "two_factor",
    "account",
    "tools",
    "fmea",
    "crisis_room",
    "onboarding",
    "katalogus",
    "django_password_validators",
    "django_password_validators.password_history",
    "rest_framework",
    "tagulous",
    # "drf_standardized_errors",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]

if REMOTE_USER_HEADER:
    MIDDLEWARE += ["rocky.middleware.remote_user.RemoteUserMiddleware"]

MIDDLEWARE += [
    "django_otp.middleware.OTPMiddleware",
    "rocky.middleware.auth_required.AuthRequiredMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "rocky.middleware.onboarding.OnboardingMiddleware",
]

if SPAN_EXPORT_GRPC_ENDPOINT is not None:
    MIDDLEWARE += ["rocky.middleware.otel.OTELInstrumentTemplateMiddleware"]

ROOT_URLCONF = "rocky.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "rocky/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "tools.context_processors.languages",
                "tools.context_processors.organizations_including_blocked",
                "tools.context_processors.rocky_version",
            ],
            "builtins": ["tools.templatetags.ooi_extra"],
        },
    },
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

WSGI_APPLICATION = "rocky.wsgi.application"

AUTH_USER_MODEL = "account.KATUser"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# try reading ROCKY_DB_DSN from environment, if not set fallback to old environment variables
try:
    POSTGRES_DB = env.db("ROCKY_DB_DSN")
except ImproperlyConfigured:
    POSTGRES_DB = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("ROCKY_DB", default=None),
        "USER": env("ROCKY_DB_USER", default=None),
        "PASSWORD": env("ROCKY_DB_PASSWORD", default=None),
        "HOST": env("ROCKY_DB_HOST", default=None),
        "PORT": env.int("ROCKY_DB_PORT", default=5432),
    }

DATABASES = {"default": POSTGRES_DB}

if env.bool("POSTGRES_SSL_ENABLED", False):
    DATABASES["default"]["OPTIONS"] = {
        "sslmode": env("POSTGRES_SSL_MODE"),
        "sslrootcert": env.path("POSTGRES_SSL_ROOTCERT"),
        "sslcert": env.path("POSTGRES_SSL_CERT"),
        "sslkey": env.path("POSTGRES_SSL_KEY"),
    }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": env.int("PASSWORD_MIN_LENGTH", 12),
        },
    },
    {
        "NAME": "django_password_validators.password_character_requirements"
        ".password_validation.PasswordCharacterValidator",
        "OPTIONS": {
            "min_length_digit": env.int("PASSWORD_MIN_DIGIT", 2),
            "min_length_alpha": env.int("PASSWORD_MIN_ALPHA", 2),
            "min_length_special": env.int("PASSWORD_MIN_SPECIAL", 2),
            "min_length_lower": env.int("PASSWORD_MIN_LOWER", 2),
            "min_length_upper": env.int("PASSWORD_MIN_UPPER", 2),
            "special_characters": " ~!@#$%^&*()_+{}\":;'[]",
        },
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en"
LANGUAGE_COOKIE_NAME = "language"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (BASE_DIR / "rocky/locale",)

# Add custom languages not provided by Django
EXTRA_LANG_INFO = {
    "pap": {"bidi": False, "code": "pap", "name": "Papiamentu", "name_local": "Papiamentu"},
}
LANG_INFO = locale.LANG_INFO.copy()
LANG_INFO.update(EXTRA_LANG_INFO)
locale.LANG_INFO = LANG_INFO

LANGUAGES = [
    ("en", "en"),
    ("nl", "nl"),
    ("pap", "pap"),
    ("it", "it"),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_DIRS = (BASE_DIR / "assets",)

LOGIN_URL = "two_factor:login"
LOGIN_REDIRECT_URL = "crisis_room"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SESSION_EXPIRE_SECONDS = env.int("SESSION_EXPIRE_SECONDS", 7200)
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True

# Require session cookie to be secure, so only a https session can be started
SESSION_COOKIE_SECURE = True

# Also set the max age on the session cookie
SESSION_COOKIE_AGE = SESSION_EXPIRE_SECONDS

SESSION_COOKIE_SAMESITE = "Strict"

# only allow http to read session cookies, not Javascript
SESSION_COOKIE_HTTPONLY = True

# No secure connection means you're not allowed to submit a form
CSRF_COOKIE_SECURE = True

# Chrome does not send the csrfcookie
CSRF_COOKIE_SAMESITE = "Strict"

# only allow http to read csrf cookies, not Javascript
CSRF_COOKIE_HTTPONLY = True

# A list of trusted origins for unsafe requests (e.g. POST)
# https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

# Configuration for Gitpod
if GITPOD_WORKSPACE_URL := env("GITPOD_WORKSPACE_URL", default=None):
    # example environment variable: GITPOD_WORKSPACE_URL=https://minvws-nlkatcoordinatio-fykdue22b07.ws-eu98.gitpod.io
    # public url on https://8000-minvws-nlkatcoordinatio-fykdue22b07.ws-eu98.gitpod.io/
    ALLOWED_HOSTS.append("8000-" + GITPOD_WORKSPACE_URL.split("//")[1])
    CSRF_TRUSTED_ORIGINS.append(GITPOD_WORKSPACE_URL.replace("//", "//8000-"))

# Configuration for GitHub Codespaces
if GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN := env("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", default=None):
    # example environment variable: GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN=preview.app.github.dev
    # public url on https://praseodym-organic-engine-9j6465vx3xgx6-8000.preview.app.github.dev/
    ALLOWED_HOSTS.append("." + GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN)
    CSRF_TRUSTED_ORIGINS.append("https://*." + GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN)

# Setup sane security defaults for application
# Deny x-framing, which is standard since Django 3.0
# There is no need to embed this in a frame anywhere, not desired.
X_FRAME_OPTIONS = "DENY"
# Send some legacy security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

CSP_HEADER = env.bool("CSP_HEADER", True)

if CSP_HEADER:
    MIDDLEWARE += ["csp.middleware.CSPMiddleware"]
    INSTALLED_APPS += ["csp"]

CSP_DEFAULT_SRC = ["'none'"]
CSP_IMG_SRC = ["'self'"]
CSP_FONT_SRC = ["'self'"]
CSP_STYLE_SRC = ["'self'"]
CSP_FRAME_ANCESTORS = ["'none'"]
CSP_BASE = ["'none'"]
CSP_FORM_ACTION = ["'self'"]
CSP_INCLUDE_NONCE_IN = ["script-src"]
CSP_CONNECT_SRC = ["'self'"]

CSP_BLOCK_ALL_MIXED_CONTENT = True

DEFAULT_RENDERER_CLASSES = ["rest_framework.renderers.JSONRenderer"]

# Turn on the browsable API by default if DEBUG is True, but disable by default in production
BROWSABLE_API = env.bool("BROWSABLE_API", DEBUG)

if BROWSABLE_API:
    DEFAULT_RENDERER_CLASSES = DEFAULT_RENDERER_CLASSES + ["rest_framework.renderers.BrowsableAPIRenderer"]

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        # For now this will provide a safe default, but non-admin users will
        # need to be able to use the API in the future..
        "rest_framework.permissions.IsAdminUser",
    ],
    "DEFAULT_RENDERER_CLASSES": DEFAULT_RENDERER_CLASSES,
    "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
}

SERIALIZATION_MODULES = {
    "xml": "tagulous.serializers.xml_serializer",
    "json": "tagulous.serializers.json",
    "python": "tagulous.serializers.python",
    "yaml": "tagulous.serializers.pyyaml",
}
TAGULOUS_SLUG_ALLOW_UNICODE = True

TAG_COLORS = [
    ("color-1-light", _("Blue light")),
    ("color-1-medium", _("Blue medium")),
    ("color-1-dark", _("Blue dark")),
    ("color-2-light", _("Green light")),
    ("color-2-medium", _("Green medium")),
    ("color-2-dark", _("Green dark")),
    ("color-3-light", _("Yellow light")),
    ("color-3-medium", _("Yellow medium")),
    ("color-3-dark", _("Yellow dark")),
    ("color-4-light", _("Orange light")),
    ("color-4-medium", _("Orange medium")),
    ("color-4-dark", _("Orange dark")),
    ("color-5-light", _("Red light")),
    ("color-5-medium", _("Red medium")),
    ("color-5-dark", _("Red dark")),
    ("color-6-light", _("Violet light")),
    ("color-6-medium", _("Violet medium")),
    ("color-6-dark", _("Violet dark")),
]

TAG_BORDER_TYPES = [
    ("plain", _("Plain")),
    ("solid", _("Solid")),
    ("dashed", _("Dashed")),
    ("dotted", _("Dotted")),
]
