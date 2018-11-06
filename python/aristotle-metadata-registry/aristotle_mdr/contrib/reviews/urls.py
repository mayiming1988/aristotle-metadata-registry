from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^account/reviews/?$', views.my_review_list, name='userMyReviewRequests'),
    url(r'^account/reviews/cancel/(?P<review_id>\d+)/?$', views.ReviewCancelView.as_view(), name='userReviewCancel'),
    url(r'^action/review/(?P<iid>\d+)?$', views.SubmitForReviewView.as_view(), name='request_review'),
    # url(r'^action/review/(?P<iid>\d+)/comment?$', views.ReviewCommentCreateView.as_view(), name='request_add_comment'),
    url(r'^account/registrartools/review/?$', views.review_list, name='userReadyForReview'),
    url(r'^account/registrartools/review/(?P<review_id>\d+)/?$', views.ReviewDetailsView.as_view(), name='userReviewDetails'),
    url(r'^account/registrartools/review/(?P<review_id>\d+)/details/?$', views.ReviewDetailsView.as_view(), name='userReviewDetails'),
    url(r'^account/registrartools/review/(?P<review_id>\d+)/accept/?$', views.ReviewAcceptView.as_view(), name='userReviewAccept'),
    url(r'^account/registrartools/review/(?P<review_id>\d+)/reject/?$', views.ReviewRejectView.as_view(), name='userReviewReject'),
    url(r'^account/registrartools/review/(?P<review_id>\d+)/comment/?$', views.ReviewCommentCreateView.as_view(), name='request_add_comment'),
    url(r'^account/registrartools/review/(?P<review_id>\d+)/impact/?$', views.ReviewImpactView.as_view(), name='request_impact'),
    url(r'^account/registrartools/review/(?P<review_id>\d+)/checks/?$', views.ReviewValidationView.as_view(), name='request_checks'),
    url(r'^account/registrartools/review/(?P<review_id>\d+)/update/?$', views.ReviewUpdateView.as_view(), name='request_update'),
]
