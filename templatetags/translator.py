from hashlib import md5
from django import template
from django.utils.html import mark_safe
from django.utils import module_loading
from django.utils.translation import get_language
from django.conf import settings
from django_translator.models import CacheTranslations, CacheTranslation
from googletrans import Translator

register = template.Library()

identifier_resolver = None

if hasattr(settings, "INSTALLED_PLUGINS") and type(settings.INSTALLED_PLUGINS) is dict:
    TRANSLATOR_PLUGIN = settings.INSTALLED_PLUGINS.get("TRANSLATOR", {})
    identifier_resolver = TRANSLATOR_PLUGIN.get("id_resolver", identifier_resolver)
    if identifier_resolver is not None:
        identifier_resolver = module_loading.import_string(identifier_resolver)


@register.simple_tag(takes_context=True)
def translate(context, data: str, *args, **kwargs):
    if data is None or len(data) == 0:
        return data if not kwargs.get("safe", False) else mark_safe(data)
    if identifier_resolver is not None:
        identifier = identifier_resolver(context)
    data_integrity = md5(str(data).encode()).hexdigest()
    cached_data = CacheTranslations.objects.filter(data_integrity=data_integrity).first()
    if cached_data is not None:
        cached_translation = CacheTranslation.objects.filter(language=kwargs.get("to", get_language()), translation_parent=cached_data).first()
        if cached_translation is not None:
            return cached_translation.cached_translation if not kwargs.get("safe", False) else mark_safe(cached_translation.cached_translation)
        else:
            try:
                #print("Calling network ", data)
                data_translated = Translator().translate(data, dest=kwargs.get("to", get_language())).text
            except:
                return data.capitalize() if not kwargs.get("safe", False) else mark_safe(data)
            new_translation = CacheTranslation.objects.create(language=kwargs.get("to", get_language()),
                cached_translation=data_translated.capitalize(), translation_parent=cached_data,)
    else:
        try:
            #print("Calling network ", data)
            data_translated = Translator().translate(data, dest=kwargs.get("to", get_language())).text
        except:
            return data.capitalize() if not kwargs.get("safe", False) else mark_safe(data)
        translation_table = CacheTranslations.objects.create(data_integrity=data_integrity, original_data=data, identifier=identifier)
        new_translation = CacheTranslation.objects.create(language=kwargs.get("to", get_language()),
            cached_translation=data_translated.capitalize(), translation_parent=translation_table)
    return data_translated.capitalize() if not kwargs.get("safe", False) else mark_safe(data_translated)