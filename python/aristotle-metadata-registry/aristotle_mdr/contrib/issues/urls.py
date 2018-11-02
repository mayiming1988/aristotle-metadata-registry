from django.conf.urls import url
from aristotle_mdr.contrib.issues import views

urlpatterns = [
    url(r'^item/(?P<iid>\d+)/issues/?$', views.IssueDisplay.as_view(), name='item_issues')
]
