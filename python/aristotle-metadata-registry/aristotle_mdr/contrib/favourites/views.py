from typing import Dict
from django.shortcuts import get_object_or_404
from aristotle_mdr.utils import url_slugify_concept
from aristotle_mdr.models import _concept
from aristotle_mdr.perms import user_can_view
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http.response import JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from aristotle_mdr.contrib.favourites.models import Favourite, Tag
from django.db.models import Case, Count, F, Max, Prefetch, When
from aristotle_mdr.models import _concept

import json


class ToggleFavourite(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        itemid = self.kwargs['iid']
        item = get_object_or_404(_concept, pk=itemid).item

        if not user_can_view(request.user, item):
            return HttpResponseForbidden()

        favourited = request.user.profile.toggleFavourite(item)

        if request.is_ajax():
            return self.get_json_response(item, favourited)
        else:
            if self.request.GET.get('next', None):
                return HttpResponseRedirect(self.request.GET.get('next'))
            else:
                return self.redirect_with_message(item, favourited)

    def get_message(self, item, favourited):

        if favourited:
            message = _("%s added to favourites.") % (item.name)
        else:
            message = _("%s removed from favourites.") % (item.name)

        message = _(message + " Review your favourites from the user menu.")
        return message

    def redirect_with_message(self, item, favourited):
        message = self.get_message(item, favourited)
        messages.add_message(self.request, messages.SUCCESS, message)
        return HttpResponseRedirect(url_slugify_concept(item))

    def get_json_response(self, item, favourited):
        message = self.get_message(item, favourited)
        response_dict = {
            'success': True,
            'message': message,
            'favourited': favourited
        }
        return JsonResponse(response_dict)


class EditTags(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        user = self.request.user
        post_data = self.request.POST
        item_id = self.kwargs['iid']
        item = get_object_or_404(_concept, pk=item_id)

        # Get all the tags on this item by this user
        current_tags = Favourite.objects.filter(
            tag__profile=user.profile,
            tag__primary=False,
            item=item
        ).values_list('tag__name', 'tag__id')

        tags_map = dict(current_tags)
        tags_json = post_data.get('tags', '')

        if tags_json:
            tags = set(json.loads(tags_json))
            logger.debug(tags)
            current_set = set(tags_map.keys())

            new = tags - current_set
            deleted = current_set - tags

            for tag in new:
                tag_obj, created = Tag.objects.get_or_create(
                    profile=user.profile,
                    name=tag,
                    primary=False
                )
                Favourite.objects.create(
                    tag=tag_obj,
                    item=item
                )
                tags_map[tag_obj.name] = tag_obj.id

            for tag in deleted:
                tag_obj, created = Tag.objects.get_or_create(
                    profile=user.profile,
                    name=tag,
                    primary=False
                )
                Favourite.objects.filter(
                    tag=tag_obj,
                    item=item
                ).delete()
                del tags_map[tag]

        return self.get_json_response(tags_map)

    def get_json_response(self, tags_map: Dict[str, int]):
        tags_list = []
        for name, id in tags_map.items():
            tags_list.append({'id': id, 'name': name})

        response = {'tags': tags_list}

        return JsonResponse(response)


class FavouritesAndTags(LoginRequiredMixin, ListView):

    paginate_by = 20
    template_name = "aristotle_mdr/favourites/userFavourites.html"

    def get_queryset(self):

        favourite_queryset = Favourite.objects.filter(
            tag__profile=self.request.user.profile,
            tag__primary=False
        ).select_related('tag')

        return _concept.objects.filter(
            favourites__tag__profile=self.request.user.profile
        ).distinct().prefetch_related(
            Prefetch('favourites', queryset=favourite_queryset, to_attr='user_favourites')
        ).annotate(
            item_favourite=Count(
                Case(When(favourites__tag__primary=True, then=1))
            ),
            used=Max('favourites__created')
        ).order_by('-used')

    def get_tags(self):

        # Get a users tags ordered by last usage, limited to 5
        return Tag.objects.filter(
            profile=self.request.user.profile,
            primary=False
        ).annotate(
            used=Max('favourites__created')
        ).order_by(
            F('used').desc(nulls_last=True)
        )[:5]

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['help'] = self.request.GET.get('help', False)
        context['favourite'] = self.request.GET.get('favourite', False)
        context['tags'] = self.get_tags()
        context['count_favourites'] = self.get_queryset().count()
        return context


class TagView(LoginRequiredMixin, ListView):

    paginate_by = 20
    template_name = "aristotle_mdr/favourites/tags.html"

    def dispatch(self, request, *args, **kwargs):
        self.tagid = self.kwargs['tagid']
        self.tag = get_object_or_404(Tag, pk=self.tagid)

        if self.tag.profile != request.user.profile:
            return HttpResponseForbidden()

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):

        return _concept.objects.annotate(
            item_favourite=Count(
                Case(When(favourites__tag__primary=True, then=1))
            ),
            used=Max('favourites__created')
        ).filter(
            favourites__tag_id=self.tagid
        ).order_by('-used')

    def get_context_data(self):

        context = super().get_context_data()
        context['tag'] = self.tag
        context['title'] = self.tag.name
        return context


class FavouriteView(LoginRequiredMixin, ListView):

    paginate_by = 20
    template_name = "aristotle_mdr/favourites/tags.html"

    def get_queryset(self):
        try:
            tag = Tag.objects.get(profile=self.request.user.profile, primary=True)
        except Tag.DoesNotExist:
            return _concept.objects.none()

        return _concept.objects.annotate(
            used=Max('favourites__created')
        ).filter(
            favourites__tag=tag
        ).order_by('-used')

    def get_context_data(self):

        context = super().get_context_data()
        context['title'] = 'My Favourites'
        context['all_favourite'] = True
        return context


class AllTagView(LoginRequiredMixin, ListView):

    paginate_by = 20
    template_name = "aristotle_mdr/favourites/all_tags.html"

    def get_queryset(self):
        return Tag.objects.filter(
            profile=self.request.user.profile,
            primary=False
        ).annotate(
            num_items=Count('favourites')
        ).order_by('-created')

    def get_context_data(self):
        context = super().get_context_data()
        return context
