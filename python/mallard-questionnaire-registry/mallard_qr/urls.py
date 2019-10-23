from django.urls import path

# from mallard_qr import views,forms
from aristotle_mdr.contrib.generic.views import GenericAlterOneToManyView


from . import models
urlpatterns = [
    path('question/<int:iid>/responses/?',
        GenericAlterOneToManyView.as_view(
            model_base=models.Question,
            model_to_add=models.ResponseDomain,
            model_base_field='response_domains',
            model_to_add_field='question',
            ordering_field='order',
        ), name='question_alter_responses'),

    # These are required for about pages to work. Include them, or custom items will die!
    # path('about/<int:template>/?$', views.DynamicTemplateView.as_view(), name="about"),
    # path('about/?', TemplateView.as_view(template_name='comet/static/about_comet_mdr.html'), name="about"),
]
