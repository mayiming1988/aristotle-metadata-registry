from braces.views import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import ListView, TemplateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from .models import UserViewHistory


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


class RemoveRecentlyViewedView(LoginRequiredMixin, DeleteView):
    template_name = 'aristotle_mdr/dashboard/clear_all_recently_viewed.html'
    model = UserViewHistory
    success_url = reverse_lazy("recently_viewed_metadata")

    def dispatch(self, request, *args, **kwargs):
        self.queryset = request.user.recently_viewed_metadata.all()
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        out = super().delete(request, *args, **kwargs)
        messages.add_message(request, messages.SUCCESS, _("Item removed from view history."))
        return out
