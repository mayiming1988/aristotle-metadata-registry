from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import ListView, TemplateView
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class RecentlyViewedView(LoginRequiredMixin, ListView):
    template_name = "aristotle_mdr/dashboard/recently_viewed.html"
    context_object_name = "page"

    def get_queryset(self):
        return self.request.user.recently_viewed_metadata.all().order_by("-view_date")

    def get_paginate_by(self, queryset):
        return self.request.GET.get('pp', 20)

class ClearRecentlyViewedView(LoginRequiredMixin, TemplateView):
    template_name = 'aristotle_mdr/dashboard/clear_all_recently_viewed.html'

    def post(self, request, *args, **kwargs):
        request.user.recently_viewed_metadata.all().delete()
        messages.add_message(request, messages.SUCCESS, _("Metadata view history successfully cleared."))
        return HttpResponseRedirect(reverse("recently_viewed_metadata"))

