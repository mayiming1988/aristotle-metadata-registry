from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from aristotle_mdr.utils import url_slugify_concept
from aristotle_glossary import models


def glossary(request):
    return render(
        request,
        "aristotle_glossary/glossary.html",
        {'terms': models.GlossaryItem.objects.visible(request.user).order_by('name').all()}
    )


class DynamicTemplateView(TemplateView):
    def get_template_names(self):
        return ['aristotle_glossary/static/%s.html' % self.kwargs['template']]


def json_list(request):
    item_ids = []
    for iid in request.GET.getlist('items'):
        try:
            iid = int(iid)
            item_ids.append(iid)
        except:
            return JsonResponse({"error": "Glossary IDs must be integers"})
    items = [{'id':obj.id,'url':url_slugify_concept(obj),'name':obj.name,'definition':obj.definition}
        for obj in models.GlossaryItem.objects.visible(request.user).filter(id__in=item_ids)
    ]
    return JsonResponse({"items": items})
