from django.conf.urls import url
from django.urls import path

from aristotle_glossary import views

# Recommended to put this at "/glossary" when including these URLs
urlpatterns = [
    path('', views.glossary, name='glossary'),
    url(r'^jsonlist/', views.json_list, name='json_list'),
    url(r'^about/(?P<template>.+)/?$', views.DynamicTemplateView.as_view(), name="about"),
]
