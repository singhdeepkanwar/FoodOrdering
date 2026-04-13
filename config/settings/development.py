from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Use sqlite for quick dev if DATABASE_URL not set
# Override in .env: DATABASE_URL=postgres://user:pass@localhost/foodordering

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
