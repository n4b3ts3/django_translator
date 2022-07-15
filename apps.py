from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class DjangoTranslatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_translator'
    verbose_name = _("Django translation")
