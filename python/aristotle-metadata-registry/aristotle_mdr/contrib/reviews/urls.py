from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^account/reviews/?$', views.my_review_list, name='userMyReviewRequests'),
    url(r'^account/registrartools/review/?$', views.review_list, name='userReadyForReview'),

    url(r'^account/registrartools/review/(?P<review_id>\d+)/accept/?$', views.ReviewAcceptView.as_view(), name='accept_review'),
    url(r'^account/registrartools/review/(?P<review_id>\d+)/endorse/?$', views.ReviewEndorseView.as_view(), name='endorse_review'),

    url(r'^action/review/start$', views.ReviewCreateView.as_view(), name='review_create'),

    url(r'^account/registrartools/review/(?P<review_id>\d+)/details/?$', views.ReviewDetailsView.as_view(), name='review_details'),
    url(r'^account/registrartools/review/(?P<review_id>\d+)/list/?$', views.ReviewListItemsView.as_view(), name='review_list'),
    url(r'^account/registrartools/review/(?P<review_id>\d+)/impact/?$', views.ReviewImpactView.as_view(), name='request_impact'),
    url(r'^account/registrartools/review/(?P<review_id>\d+)/supersedes/edit/?$', views.ReviewSupersedesEditView.as_view(), name='request_supersedes_edit'),
    url(r'^account/registrartools/review/(?P<review_id>\d+)/supersedes/?$', views.ReviewSupersedesInfoView.as_view(), name='request_supersedes'),
    url(r'^account/registrartools/review/(?P<review_id>\d+)/checks/?$', views.ReviewValidationView.as_view(), name='request_checks'),
    url(r'^account/registrartools/review/(?P<review_id>\d+)/update/?$', views.ReviewUpdateView.as_view(), name='request_update'),
    url(r'^account/registrartools/review/(?P<review_id>\d+)/issues/?$', views.ReviewIssuesView.as_view(), name='request_issues'),
]
