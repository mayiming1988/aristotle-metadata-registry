from braces.views import LoginRequiredMixin, PermissionRequiredMixin

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
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

from aristotle_mdr import models as MDR
from aristotle_mdr import perms
from aristotle_mdr.forms.forms import ReviewChangesForm
from aristotle_mdr.views import ReviewChangesView, display_review
from aristotle_mdr.views.actions import ItemSubpageFormView
from aristotle_mdr.views.utils import (
    generate_visibility_matrix,
    paginated_list
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
    return paginated_list(request, reviews, "aristotle_mdr/user/my_review_list.html", {'reviews': reviews})


@login_required
def review_list(request):
    if not request.user.profile.is_registrar:
        raise PermissionDenied
    authorities = [i[0] for i in request.user.profile.registrarAuthorities.filter(active=0).values_list('id')]

    # Registars can see items they have been asked to review
    q = Q(Q(registration_authority__id__in=authorities) & ~Q(status=models.REVIEW_STATES.cancelled))

    reviews = models.ReviewRequest.objects.visible(request.user).filter(q)
    return paginated_list(request, reviews, "aristotle_mdr/user/userReviewList.html", {'reviews': reviews})


class ReviewDetailsView(DetailView):
    pk_url_kwarg = 'review_id'
    template_name = "aristotle_mdr/user/request_review_details.html"
    context_object_name = "review"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(*args, **kwargs)
        context['next'] = self.request.GET.get('next', reverse('aristotle_reviews:userReadyForReview'))
        context['active_tab'] = "conversation"
        return context

    def get_queryset(self):
        return models.ReviewRequest.objects.visible(self.request.user)


class SubmitForReviewView(ItemSubpageFormView):
    form_class = forms.RequestReviewForm
    template_name = "aristotle_mdr/actions/request_review.html"

    def get_context_data(self, *args, **kwargs):
        kwargs = super().get_context_data(*args, **kwargs)
        kwargs['reviews'] = self.get_item().review_requests.filter(status=MDR.REVIEW_STATES.submitted).all()
        kwargs['status_matrix'] = json.dumps(generate_visibility_matrix(self.request.user))
        return kwargs

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        item = self.get_item()

        if form.is_valid():
            review = models.ReviewRequest.objects.create(
                registration_authority=form.cleaned_data['registrationAuthorities'],
                message=form.cleaned_data['changeDetails'],
                state=form.cleaned_data['state'],
                registration_date=form.cleaned_data['registrationDate'],
                cascade_registration=form.cleaned_data['cascadeRegistration'],
                requester=request.user
            )

            review.concepts.add(item)
            message = mark_safe(
                _("<a href='{url}'>Review submitted, click to review</a>").format(url=reverse('aristotle_reviews:userReviewDetails', args=[review.pk]))
            )
            messages.add_message(request, messages.INFO, message)
            return HttpResponseRedirect(item.get_absolute_url())
        else:
            return self.form_invalid(form)


class ReviewActionMixin(object):
    user_form = True

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        review = self.get_review()
        if not perms.user_can_view_review(self.request.user, review):
            raise PermissionDenied
        if review.status != models.REVIEW_STATES.submitted:
            return HttpResponseRedirect(reverse('aristotle_reviews:userReviewDetails', args=[review.pk]))
        return super().dispatch(*args, **kwargs)

    def get_review(self):
        self.review = get_object_or_404(models.ReviewRequest, pk=self.kwargs['review_id'])
        return self.review

    def get_context_data(self, *args, **kwargs):
        kwargs = super().get_context_data(*args, **kwargs)
        kwargs['review'] = self.get_review()
        return kwargs

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.user_form:
            kwargs['user'] = self.request.user
        return kwargs


class ReviewUpdateView(ReviewActionMixin, UpdateView):
    template_name = "aristotle_mdr/reviews/update.html"
    fields = [
        'due_date', 'registration_date', 'concepts',
        'message'
    ]
    pk_url_kwarg = 'review_id'
    context_object_name = "item" #review"
    model = models.ReviewRequest
    user_form = False

    def get_success_url(self):
        return self.get_review().get_absolute_url()


class ReviewCancelView(ReviewActionMixin, FormView):
    form_class = forms.RequestReviewCancelForm
    template_name = "aristotle_mdr/user/user_request_cancel.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        review = self.get_review()
        if not self.request.user == review.requester:
            raise PermissionDenied
        if review.status != models.REVIEW_STATES.submitted:
            return HttpResponseRedirect(reverse('aristotle_reviews:userReviewDetails', args=[review.pk]))

        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_review()
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            review = form.save(commit=False)
            review.status = models.REVIEW_STATES.cancelled
            review.save()
            message = _("Review successfully cancelled")
            messages.add_message(request, messages.INFO, message)
            return HttpResponseRedirect(reverse('aristotle_reviews:userMyReviewRequests'))
        else:
            return self.form_invalid(form)


class ReviewRejectView(ReviewActionMixin, FormView):
    form_class = forms.RequestReviewRejectForm
    template_name = "aristotle_mdr/user/user_request_reject.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_review()
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.status = MDR.REVIEW_STATES.rejected
            review.save()
            message = _("Review successfully rejected")
            messages.add_message(request, messages.INFO, message)
            return HttpResponseRedirect(reverse('aristotle_reviews:userReadyForReview'))
        else:
            return self.form_invalid(form)


class ReviewAcceptView(ReviewChangesView):

    change_step_name = 'review_accept'

    form_list = [
        ('review_accept', forms.RequestReviewAcceptForm),
        ('review_changes', ReviewChangesForm)
    ]

    templates = {
        'review_accept': 'aristotle_mdr/user/user_request_accept.html',
        'review_changes': 'aristotle_mdr/actions/review_state_changes.html'
    }

    condition_dict = {'review_changes': display_review}
    display_review = None
    review = None

    def dispatch(self, request, *args, **kwargs):

        review = self.get_review()

        if not self.ra_active_check(review):
            return HttpResponseNotFound('Registration Authority is not active')

        if not perms.user_can_view_review(self.request.user, review):
            raise PermissionDenied
        if review.status != models.REVIEW_STATES.submitted:
            return HttpResponseRedirect(reverse('aristotle_reviews:userReviewDetails', args=[review.pk]))

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
            'state': review.state,
            'registrationDate': review.registration_date,
            'cascadeRegistration': review.cascade_registration,
            'changeDetails': review.message
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

    def done(self, form_list, form_dict, **kwargs):
        review = self.get_review()

        message = self.register_changes_with_message(form_dict)

        # Update review object
        # review.reviewer = self.request.user
        # review.response = form_dict['review_accept'].cleaned_data['response']
        review.status = models.REVIEW_STATES.accepted
        review.save()

        messages.add_message(self.request, messages.INFO, message)

        return HttpResponseRedirect(reverse('aristotle_reviews:userReadyForReview'))


class ReviewCommentCreateView(ReviewActionMixin, CreateView):
    pk_url_kwarg = 'review_id'
    template_name = "aristotle_mdr/user/request_review_details.html"
    context_object_name = "review"
    fields = ['body']
    model = models.ReviewComment
    user_form = False

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        form.instance.request = self.get_review()
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return self.get_review().get_absolute_url()

    # def get(self, request, *args, **kwargs):
    #     return HttpResponseRedirect(
    #         reverse('aristotle_reviews:request_review', args=[self.kwargs.get('review_id')])
    #     )

    # def get_context_data(self, *args, **kwargs):
    #     # Call the base implementation first to get a context
    #     context = super().get_context_data(*args, **kwargs)
    #     context['next'] = self.request.GET.get('next', reverse('aristotle_reviews:userReadyForReview'))
    #     return context

    # def get_queryset(self):
    #     return models.ReviewRequest.objects.visible(self.request.user)

class ReviewImpactView(ReviewActionMixin, TemplateView):
    pk_url_kwarg = 'review_id'
    template_name = "aristotle_mdr/user/request_review_details.html"
    context_object_name = "review"

    def get_context_data(self, *args, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(*args, **kwargs)
        context['active_tab'] = "impact"


        # TODO: These are hacky imports for the below code
        from aristotle_mdr.models import Status, STATES
        from aristotle_mdr.utils import status_filter
        ra = self.get_review().registration_authority
        user = self.request.user
        queryset = self.get_review().concepts.all()
        static_content = {'new_state': self.get_review().state}

        # TODO:
        # This was stolen from aristotle_mdr.forms.fields.ReviewChangesChoiceField.build_extra_info
        # Make this generic
        extra_info = {}
        subclassed_queryset = list(queryset.select_subclasses())
        statuses = Status.objects.filter(concept__in=queryset, registrationAuthority=ra).select_related('concept')
        statuses = status_filter(statuses).order_by("-registrationDate", "-created")

        new_state_num = static_content['new_state']
        new_state = str(STATES[new_state_num])

        # Build a dict mapping concepts to their status data
        # So that no additional status queries need to be made
        states_dict = {}
        for status in statuses:
            state_name = str(STATES[status.state])
            reg_date = status.registrationDate
            if status.concept.id not in states_dict:
                states_dict[status.concept.id] = {
                    'name': state_name,
                    'reg_date': reg_date,
                    'state': status.state
                }

        deselections = False
        for concept in subclassed_queryset:
            url = reverse('aristotle:registrationHistory', kwargs={'iid': concept.id})

            innerdict = {}
            # Get class name
            innerdict['type'] = concept.__class__.get_verbose_name()
            innerdict['checked'] = True

            try:
                state_info = states_dict[concept.id]
            except KeyError:
                state_info = None

            if state_info:
                innerdict['old'] = {
                    'url': url,
                    'text': state_info['name'],
                    'old_reg_date': state_info['reg_date']
                }
                if state_info['state'] >= new_state_num:
                    innerdict['checked'] = False
                    deselections = True

            innerdict['perm'] = perms.user_can_change_status(user, concept)
            innerdict['new_state'] = {'url': url, 'text': new_state}

            extra_info[concept.id] = innerdict

        # TODO: End of copied code
        for concept in subclassed_queryset:
            concept.info = extra_info[concept.id]

        context['statuses'] = subclassed_queryset

        return context


import yaml
from os import path
from django.conf import settings
from django.utils.module_loading import import_string
import jsonschema
from aristotle_mdr.contrib.validators.validators import Checker

class ReviewValidationView(ReviewActionMixin, TemplateView):
    pk_url_kwarg = 'review_id'
    template_name = "aristotle_mdr/user/request_review_details.html"
    context_object_name = "review"
    base_dir=path.dirname(path.dirname(path.dirname(__file__)))

    def get_context_data(self, *args, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(*args, **kwargs)
        context['active_tab'] = "checks"


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
    