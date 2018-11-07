from django.conf.urls import url
from aristotle_mdr_api.v4 import views

urlpatterns = [
    url(r'issues/$', views.IssueCreateView.as_view(), name='issues_create'),
    url(r'issues/(?P<pk>\d+)/$', views.IssueView.as_view(), name='issues'),
    url(r'issues/(?P<pk>\d+)/updatecomment/$', views.IssueUpdateAndCommentView.as_view(), name='issue_update_and_comment'),
    url(r'issues/comments/$', views.IssueCommentCreateView.as_view(), name='issue_comment'),
    url(r'issues/comments/(?P<pk>\d+)/$', views.IssueCommentRetrieveView.as_view(), name='issue_comment_get'),
]
