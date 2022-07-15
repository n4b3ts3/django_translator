from django.contrib import admin
from django.conf import global_settings, settings
from django.utils import module_loading
from .models import CacheTranslations, CacheTranslation

# Plugin configuration
sites = ()
admin_parents = {}

if hasattr(settings, "INSTALLED_PLUGINS") and type(settings.INSTALLED_PLUGINS) is dict:
    TRANSLATOR_PLUGIN = settings.INSTALLED_PLUGINS.get("TRANSLATOR", {})
    sites = TRANSLATOR_PLUGIN.get("sites", sites)
    admin_parents = TRANSLATOR_PLUGIN.get("admin_parents", admin_parents)
    for key in admin_parents.keys():
        admin_parents[key] = module_loading.import_string(admin_parents[key])

# Register your models here.

class CacheTranslationInline(admin_parents.get("CacheTranslationInline", admin.TabularInline)):
    model = CacheTranslation
    fieldsets = (
        (None, {
            "fields": (
                "language", "cached_translation"
            ),
        }),
    )
    extra = 0

class CacheTranslationAdmin(admin_parents.get("CacheTranslationAdmin", admin.ModelAdmin)):
    list_display = ("original_data", "data_integrity")
    fieldsets = (
        ("Django translations", {
            "fields": (
                "original_data", 
            ),
        }),
    )
    inlines = (CacheTranslationInline, )
    readonly_fields = ("original_data",)


# Plugin section

for site in sites:
    site_class = module_loading.import_string(site)
    site_class.register(CacheTranslations, CacheTranslationAdmin)
