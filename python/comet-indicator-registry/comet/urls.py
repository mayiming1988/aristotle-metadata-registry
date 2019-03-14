from django.conf.urls import url

from comet import views
from django.views.generic import TemplateView
from aristotle_mdr.contrib.generic.views import GenericAlterManyToManyView
from comet import models


urlpatterns = [
    url(r'^/?$', TemplateView.as_view(template_name='comet/static/about_comet_mdr.html')),

    # These are required for about pages to work. Include them, or custom items will die!
    url(r'^about/(?P<template>.+)/?$', views.DynamicTemplateView.as_view(), name="about"),
    url(r'^about/?$', TemplateView.as_view(template_name='comet/static/about_comet_mdr.html'), name="about"),
]
