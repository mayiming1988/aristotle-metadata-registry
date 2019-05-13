from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, TemplateView
from aristotle_mdr.utils import get_concepts_for_apps, fetch_metadata_apps
from collections import OrderedDict
from aristotle_mdr.models import _concept


class BrowseApps(TemplateView):
    template_name = "aristotle_mdr_browse/apps_list.html"
    ordering = 'app_label'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        aristotle_apps = fetch_metadata_apps()
        out = {}

        for m in get_concepts_for_apps(aristotle_apps):
            # Only output subclasses of 11179 concept
            app_models = out.get(m.app_label, {'app': None, 'models': []})
            if app_models['app'] is None:
                app_models['app'] = getattr(
                    apps.get_app_config(m.app_label),
                    'verbose_name',
                    _("No name")  # Where no name is configured in the app_config, set a dummy so we don't keep trying
                )

            app_models['models'].append(m)
            out[m.app_label] = app_models

        context['apps'] = OrderedDict(sorted(out.items(), key=lambda app: app[1]['app']))
        return context


class AppBrowser(ListView):
    """ListView with some extra context (subclassed by following views)"""

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        if self.kwargs['app'] not in fetch_metadata_apps():
            raise Http404
        context['app_label'] = self.kwargs['app']
        context['app'] = apps.get_app_config(self.kwargs['app'])
        return context


class BrowseModels(AppBrowser):
    """Show a list of models"""
    template_name = "aristotle_mdr_browse/model_list.html"
    context_object_name = "model_list"
    paginate_by = 25

    def get_queryset(self):
        app = self.kwargs['app']
        if self.kwargs['app'] not in fetch_metadata_apps():
            raise Http404
        return get_concepts_for_apps([app])


class BrowseConcepts(AppBrowser):
    """Show a list of items of a particular model"""
    _model = None
    paginate_by = 25

    @property
    def model(self):
        if self.kwargs['app'] not in fetch_metadata_apps():
            raise Http404
        if self._model is None:
            app = self.kwargs['app']
            model = self.kwargs['model']
            ct = ContentType.objects.filter(app_label=app, model=model)
            if not ct:
                raise Http404
            else:
                self._model = ct.first().model_class()
        if not issubclass(self._model, _concept):
            raise Http404
        return self._model

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        return queryset.visible(self.request.user).prefetch_related('statuses__registrationAuthority')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['model'] = self.model
        context['model_name'] = self.model._meta.model_name
        context['sort'] = self.order
        context['total_queryset_size'] = self.get_queryset().count()
        return context

    def get_template_names(self):
        app_label = self.kwargs['app']
        names = super().get_template_names()
        names.append('aristotle_mdr_browse/list.html')
        names.insert(0, 'aristotle_mdr_browse/%s/%s_list.html' % (app_label, self.model._meta.model_name))
        return names

    def get_ordering(self):
        from aristotle_mdr.views.utils import paginate_sort_opts
        self.order = self.request.GET.get('sort', 'name_asc')
        return paginate_sort_opts.get(self.order)
