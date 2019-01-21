from django.contrib import admin
import aristotle_mdr.contrib.help.models as HelpModels


class HelpAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'app_label', 'modified')
    search_fields = ['title']


admin.site.register(HelpModels.HelpPage, HelpAdmin)
admin.site.register(HelpModels.ConceptHelp, HelpAdmin)
