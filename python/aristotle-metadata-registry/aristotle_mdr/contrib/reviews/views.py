from braces.views import LoginRequiredMixin, PermissionRequiredMixin

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q, Count
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
# from django.views.generic import ListView, TemplateView, DeleteView
from django.views.generic import (DetailView,
                                  ListView,
                                  UpdateView,
                                  FormView,
                                  TemplateView,
                                  CreateView,
                                  UpdateView
                                  )

import reversion

from aristotle_mdr import models as MDR
from aristotle_mdr import perms
from aristotle_mdr.forms.forms import ReviewChangesForm
from aristotle_mdr.utils import cascade_items_queryset, get_status_change_details
from aristotle_mdr.views import ReviewChangesView, display_review
from aristotle_mdr.views.actions import ItemSubpageFormView
from aristotle_mdr.views.utils import (
    generate_visibility_matrix,
    paginated_list,
    UserFormViewMixin,
)

import json

from . import models, forms

import logging

logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)

@login_required
def my_review_list(request):
    # Users can see any items they have been asked to review
    q = Q(requester=request.user)
    reviews = models.ReviewRequest.objects.visible(request.user).filter(q).filter(registration_authority__active=0)
    return paginated_list(request, reviews, "aristotle_mdr/reviews/my_review_list.html", {'reviews': reviews})


@login_required
def review_list(request):
    if not request.user.profile.is_registrar:
        raise PermissionDenied
    authorities = [i[0] for i in request.user.profile.registrarAuthorities.filter(active=0).values_list('id')]

    # Registars can see items they have been asked to review
    q = Q(Q(registration_authority__id__in=authorities) & ~Q(status=models.REVIEW_STATES.revoked))

    reviews = models.ReviewRequest.objects.visible(request.user).filter(q)
    return paginated_list(request, reviews, "aristotle_mdr/reviews/reviewers_review_list.html", {'reviews': reviews})


class ReviewActionMixin(UserFormViewMixin):
    pk_url_kwarg = 'review_id'
    context_object_name = "review"
    user_form = True

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        review = self.get_review()
        if not perms.user_can_view_review(self.request.user, review):
            raise PermissionDenied
        # if review.status != models.REVIEW_STATES.open:
        #     return HttpResponseRedirect(reverse('aristotle_reviews:userReviewDetails', args=[review.pk]))
        return super().dispatch(*args, **kwargs)

    def get_review(self):
        self.review = get_object_or_404(models.ReviewRequest, pk=self.kwargs['review_id'])
        return self.review

    def get_context_data(self, *args, **kwargs):
        kwargs = super().get_context_data(*args, **kwargs)
        review = self.get_review()
        kwargs['review'] = review
        kwargs['can_approve_review'] = perms.user_can_approve_review(self.request.user, review)
        kwargs['can_open_close_review'] = perms.user_can_close_or_reopen_review(self.request.user, review)
        if hasattr(self, "active_tab_name"):
            kwargs['active_tab'] = self.active_tab_name
        return kwargs

    def get_queryset(self):
        return models.ReviewRequest.objects.visible(self.request.user)


class ReviewDetailsView(ReviewActionMixin, DetailView):
    template_name = "aristotle_mdr/reviews/review/details.html"
    active_tab_name = "details"

    def get_context_data(self, *args, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(*args, **kwargs)
        # context['next'] = self.request.GET.get('next', reverse('aristotle_reviews:userReadyForReview'))
        review = self.get_review()
        context['can_accept_review'] = review.status == models.REVIEW_STATES.open and perms.user_can_approve_review(self.request.user, self.get_review())
        return context


class ReviewListItemsView(ReviewActionMixin, DetailView):
    template_name = "aristotle_mdr/reviews/review/list.html"
    active_tab_name = "itemlist"

    def get_context_data(self, *args, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(*args, **kwargs)
        context['next'] = self.request.GET.get('next', reverse('aristotle_reviews:userReadyForReview'))
        return context


class ReviewUpdateView(ReviewActionMixin, UpdateView):
    template_name = "aristotle_mdr/reviews/review/update.html"
    form_class = forms.RequestReviewUpdateForm
    context_object_name = "item" #review"
    model = models.ReviewRequest
    user_form = True

    def get_success_url(self):
        return self.get_review().get_absolute_url()


class ReviewCreateView(UserFormViewMixin, CreateView):
    template_name = "aristotle_mdr/reviews/review/create.html"
    form_class = forms.RequestReviewCreateForm
    model = models.ReviewRequest
    user_form = True

    def get_initial(self):
        initial = super().get_initial()
        
        item_ids = self.request.GET.getlist("items")
        initial_metadata = MDR._concept.objects.visible(self.request.user).filter(id__in=item_ids)
        initial.update({
            "concepts": initial_metadata,
        })
            
        return initial

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save(commit=False)
        self.object.requester = self.request.user
        self.object.save()
        return super().form_valid(form)


class ReviewStatusChangeBase(ReviewActionMixin, ReviewChangesView):

    change_step_name = 'review_accept'

    condition_dict = {'review_changes': display_review}
    display_review = None
    review = None
    user_form = True

    def dispatch(self, request, *args, **kwargs):

        review = self.get_review()

        if not self.ra_active_check(review):
            return HttpResponseNotFound('Registration Authority is not active')

        if not perms.user_can_approve_review(self.request.user, review):
            raise PermissionDenied
        if review.status != models.REVIEW_STATES.open:
            messages.add_message(self.request, messages.WARNING, "This review is already closed. Re-open this review to endorse content.")
            return HttpResponseRedirect(reverse('aristotle_reviews:review_details', args=[review.pk]))

        return super().dispatch(request, *args, **kwargs)

    def ra_active_check(self, review):
        return review.registration_authority.is_active

    def get_items(self):
        return self.get_review().concepts.all()

    def get_change_data(self, register=False):
        review = self.get_review()

        # Register status changes
        change_data = {
            'registrationAuthorities': [review.registration_authority],
            'state': review.target_registration_state,
            'registrationDate': review.registration_date,
            'cascadeRegistration': review.cascade_registration,
            'changeDetails': self.get_cleaned_data_for_step(self.change_step_name)['status_message']
        }

        if register:
            # If registering cascade needs to be a boolean
            # This is done autmoatically on clean for the change status forms
            change_data['cascadeRegistration'] = (review.cascade_registration == 1)

        return change_data

    def get_context_data(self, *args, **kwargs):
        kwargs = super().get_context_data(*args, **kwargs)
        kwargs['status_matrix'] = json.dumps(generate_visibility_matrix(self.request.user))
        kwargs['review'] = self.get_review()
        return kwargs

    def get_form_kwargs(self, step):

        kwargs = super().get_form_kwargs(step)

        if step == 'review_accept':
            return {'user': self.request.user}

        return kwargs


class ReviewAcceptView(ReviewStatusChangeBase):

    form_list = [
        ('review_accept', forms.RequestReviewAcceptForm),
        ('review_changes', ReviewChangesForm)
    ]

    templates = {
        'review_accept': 'aristotle_mdr/user/user_request_accept.html',
        'review_changes': 'aristotle_mdr/actions/review_state_changes.html'
    }

    def done(self, form_list, form_dict, **kwargs):
        review = self.get_review()

        with transaction.atomic(), reversion.revisions.create_revision():
            message = self.register_changes_with_message(form_dict)
    
            if form_dict['review_accept'].cleaned_data['close_review'] == "1":
                review.status = models.REVIEW_STATES.approved
                review.save()
    
            update = models.ReviewStatusChangeTimeline.objects.create(
                request=review, status=models.REVIEW_STATES.approved,
                actor=self.request.user
            )
            update = models.ReviewEndorsementTimeline.objects.create(
                request=review,
                registration_state=review.target_registration_state,
                actor=self.request.user
            )
    
            messages.add_message(self.request, messages.INFO, message)

        return HttpResponseRedirect(reverse('aristotle_reviews:review_details', args=[review.pk]))


class ReviewEndorseView(ReviewStatusChangeBase):

    form_list = [
        ('review_accept', forms.RequestReviewEndorseForm),
        ('review_changes', ReviewChangesForm)
    ]

    templates = {
        'review_accept': 'aristotle_mdr/user/user_request_endorse.html',
        'review_changes': 'aristotle_mdr/actions/review_state_changes.html'
    }

    def get_change_data(self, register=False):
        change_data = super().get_change_data(register)
        change_data['state'] = int(self.get_cleaned_data_for_step(self.change_step_name)['registration_state'])
        change_data['registrationDate'] = self.get_cleaned_data_for_step(self.change_step_name)['registration_date']

        return change_data

    def done(self, form_list, form_dict, **kwargs):
        review = self.get_review()

        with transaction.atomic(), reversion.revisions.create_revision():
            message = self.register_changes_with_message(form_dict)

            if int(form_dict['review_accept'].cleaned_data['close_review']) == 1:
                review.status = models.REVIEW_STATES.closed
                review.save()
    
            update = models.ReviewEndorsementTimeline.objects.create(
                request=review,
                registration_state=self.get_cleaned_data_for_step(self.change_step_name)['registration_state'],
                actor=self.request.user
            )
    
            messages.add_message(self.request, messages.INFO, message)

        return HttpResponseRedirect(reverse('aristotle_reviews:review_details', args=[review.pk]))


class ReviewIssuesView(ReviewActionMixin, TemplateView):
    pk_url_kwarg = 'review_id'
    template_name = "aristotle_mdr/reviews/review/issues.html"
    context_object_name = "review"
    active_tab_name = "issues"

    def get_context_data(self, *args, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(*args, **kwargs)

        from aristotle_mdr.contrib.issues.models import Issue
        base_qs = Issue.objects.filter(item__rr_review_requests=self.get_review())
        context['open_issues'] = base_qs.filter(isopen=True).order_by('created')
        context['closed_issues'] = base_qs.filter(isopen=False).order_by('created')

        return context


class ReviewImpactView(ReviewActionMixin, TemplateView):
    pk_url_kwarg = 'review_id'
    template_name = "aristotle_mdr/reviews/review/impact.html"
    context_object_name = "review"
    active_tab_name = "impact"

    def get_context_data(self, *args, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(*args, **kwargs)
        review = self.get_review()
        if review.cascade_registration:
            queryset = cascade_items_queryset(items=review.concepts.all())
        else:
            queryset = review.concepts.all()
        extra_info, any_higher = get_status_change_details(queryset,review.registration_authority, review.state)

        for concept in queryset:
            concept.info = extra_info[concept.id]

        context['statuses'] = queryset

        return context


import yaml
from os import path
from django.conf import settings
from django.utils.module_loading import import_string
import jsonschema
from aristotle_mdr.contrib.validators.validators import Checker

class ReviewValidationView(ReviewActionMixin, TemplateView):
    pk_url_kwarg = 'review_id'
    template_name = "aristotle_mdr/reviews/review/validation.html"
    context_object_name = "review"
    base_dir=path.dirname(path.dirname(path.dirname(__file__)))
    active_tab_name = "checks"

    def get_context_data(self, *args, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(*args, **kwargs)

        # TODO: more copies
        with open(path.join(self.base_dir, 'schema/schema.json')) as schemafile:
            self.schema = json.load(schemafile)

        aristotle_validators = settings.ARISTOTLE_VALIDATORS
        self.validators = {x: import_string(y) for x, y in aristotle_validators.items()}
        # Hard coded setup for now
        with open(path.join(self.base_dir, 'schema/setup.yaml')) as setupfile:
            self.setup = yaml.load(setupfile)
        self.ra = self.get_review().registration_authority

        _kwargs = kwargs
        kwargs = {}
        total_results = []
        for concept in self.get_review().concepts.all():
            kwargs = {}
            
            #TODO: Copied agin
            
            # Slow query
            item = concept.item
            itemtype = type(item).__name__
    
            valid = True
            try:
                jsonschema.validate(self.setup, self.schema)
            except jsonschema.exceptions.ValidationError as e:
                logger.critical(e)
                valid = False
    
            results = []
            if valid:
                for itemsetup in self.setup:
                    checker = Checker(itemsetup)
                    results += checker.run_rules(item, self.get_review().state, self.ra)

            kwargs['setup_valid'] = valid
            kwargs['results'] = results
            kwargs['item_name'] = item.name

            total_results.append(kwargs)

        context['total_results'] = total_results
        context['setup_valid'] = True

        return context
    