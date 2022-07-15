from hashlib import md5
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.conf import settings

identifier_class = None

if hasattr(settings, "INSTALLED_PLUGINS") and type(settings.INSTALLED_PLUGINS) is dict:
    TRANSLATOR_PLUGIN = settings.INSTALLED_PLUGINS.get("TRANSLATOR", {})
    identifier_class = TRANSLATOR_PLUGIN.get("identifier", None)

# Create your models here.

class CacheTranslations(models.Model):
    plugable = True
    if identifier_class:
        identifier = models.ForeignKey(to=identifier_class, on_delete=models.CASCADE, default="", blank=True, null=True)
    data_integrity = models.CharField(_("Data integrity"), max_length=255, unique=True)
    original_data = models.TextField(_("Original Data"))

    def save(self, *args, **kwargs):
        self.data_integrity = md5(str(self.original_data).encode()).hexdigest()
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")
    
class CacheTranslation(models.Model):
    language = models.CharField(_("Language"), max_length=2)
    cached_translation = models.TextField(_("Translated text"))
    translation_parent = models.ForeignKey(CacheTranslations, on_delete=models.CASCADE, verbose_name=_("Parent table"))
    
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Cached translation")
        verbose_name_plural = _("Cached translations")