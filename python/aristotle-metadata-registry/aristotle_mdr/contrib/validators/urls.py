from django.conf.urls import url
from aristotle_mdr.contrib.validators import views

urlpatterns = [
    url(r'validations/edit/$', views.RegistryValidationRuleEditView.as_view(), name='validation_edit')
]
