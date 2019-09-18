from django.contrib import admin
from aristotle_mdr.contrib.identifiers import models
import reversion


class NamespaceAdmin(admin.ModelAdmin):
    list_display = ['shorthand_prefix']
    list_filter = ['shorthand_prefix']
    search_fields = ['shorthand_prefix']


admin.site.register(models.Namespace, NamespaceAdmin)


class ScopedIdentifierInline(admin.TabularInline):
    model = models.ScopedIdentifier


reversion.revisions.register(models.ScopedIdentifier)
