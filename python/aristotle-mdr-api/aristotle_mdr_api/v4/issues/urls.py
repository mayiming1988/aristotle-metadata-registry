from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.IssueCreateView.as_view(), name='create'),
    url(r'^(?P<pk>\d+)/$', views.IssueView.as_view(), name='issue'),
    url(r'^(?P<pk>\d+)/updatecomment/$', views.IssueUpdateAndCommentView.as_view(), name='update_and_comment'),
    url(r'^(?P<pk>\d+)/approve/$', views.IssueApproveView.as_view(), name='approve'),
    url(r'^comments/$', views.IssueCommentCreateView.as_view(), name='comment'),
    url(r'^comments/(?P<pk>\d+)/$', views.IssueCommentRetrieveView.as_view(), name='comment_get'),
]
