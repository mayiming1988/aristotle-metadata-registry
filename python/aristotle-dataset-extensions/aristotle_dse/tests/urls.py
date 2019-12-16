from django.urls import path, include

urlpatterns = [
    path('', include(('aristotle_dse.urls', "aristotle_dse"), namespace="aristotle_dse")),
    path('', include('aristotle_mdr.urls')),
    path('', include(('aristotle_mdr.contrib.slots.urls', "aristotle_slots"), namespace="aristotle_slots")),
    path('browse/', include('aristotle_mdr.contrib.browse.urls')),
    path('help/', include(('aristotle_mdr.contrib.help.urls', "aristotle_help"), namespace="aristotle_help")),
]
