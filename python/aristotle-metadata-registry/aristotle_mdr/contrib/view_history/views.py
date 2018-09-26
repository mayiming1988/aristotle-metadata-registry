from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView


class RecentlyViewedView(LoginRequiredMixin, ListView):
    template_name = "aristotle_mdr/dashboard/recently_viewed.html"
    context_object_name = "page"

    def get_queryset(self):
        return self.request.user.recently_viewed_metadata.all().order_by("-view_date")

    def get_paginate_by(self, queryset):
        return self.request.GET.get('pp', 20)
