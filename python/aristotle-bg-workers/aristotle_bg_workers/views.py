from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Q
from django.http.response import HttpResponse, JsonResponse
from django.views.generic import View, ListView, TemplateView

from aristotle_mdr.mixins import IsSuperUserMixin

from django_celery_results.models import TaskResult

from aristotle_bg_workers.celery import app
from aristotle_bg_workers.helpers import date_convert, get_pretty_name

import json
import logging
logger = logging.getLogger(__name__)

User = get_user_model()


class GenericTaskView(IsSuperUserMixin, View):

    def get(self, request, task_name):

        task_promise = app.send_task(task_name, kwargs={"requester": self.request.user.email})

        return HttpResponse(task_promise.id)


class GenericTaskStopView(IsSuperUserMixin, View):

    def get(self, request):
        task_id = request.GET.get("uuid")
        if task_id is not None:
            meta = {"requester": self.request.user.email}
        else:
            task_result_pk = request.GET.get("pk")
            result = TaskResult.objects.get(pk=task_result_pk)
            task_id = result.task_id
        # AsyncResult(task_id).forget()
        from celery.task.control import revoke
        revoke(task_id, terminate=True)

        return HttpResponse(task_id)


class TaskListView(IsSuperUserMixin, ListView):

    model = TaskResult
    template_name = "aristotle_bg_workers/task_history.html"
    paginate_by = 25
    ordering = ['-date_done']

    def get_queryset(self):
        if '__all__' in self.request.GET.keys():
            return super().get_queryset()
        if 'taskname' in self.request.GET.keys():
            return super().get_queryset().filter(task_name__iexact=self.request.GET.get('taskname'))
        return super().get_queryset().filter(
            Q(task_name__istartswith="long__") | Q(task_name__isnull=True)
        ).filter(hidden=False)

    def tasks_with_users(self, qs):
        users = {}
        def get_user(task):
            try:
                email = task.safe_result.get("requester", None)
                if not email:
                    logger.debug("No user with email [{}] found".format(email))
                    return None
                if email in users.keys():
                    return users[email]
                user = User.objects.get(email=email)
                users[email] = user
                return user
            except Exception as e:
                logger.warning(e)
                return None

        for task in qs:
            task.safe_result = json.loads(task.result)
            task.requester = get_user(task)
            task.display_name = get_pretty_name(task.task_name)
            yield task

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'annotated_list': self.get_annotated_list(context['page_obj'])})
        return context

    def get_annotated_list(self, qs):
        return self.tasks_with_users(qs)


class TaskListLimitedView(TaskListView):
    # Used for display of tasks on cloud dashboard

    template_name = "aristotle_bg_workers/task_list.html"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'noresult': True})
        return context


class TaskRunnerView(IsSuperUserMixin, TemplateView):

    template_name = "aristotle_bg_workers/task_runner.html"

    def get_context_data(self, **kwargs):

        tasks = ['long__reindex', 'long__load_help', 'long__recache_visibility']
        task_buttons = []
        from aristotle_bg_workers.helpers import get_pretty_name

        for task in tasks:
            task_buttons.append({'display_name': get_pretty_name(task), 'task_name': task})

        kwargs['tasks'] = task_buttons
        return super().get_context_data(**kwargs)


class GetTaskStatusView(TaskListView):

    def get(self, request):

        cached_status_list = cache.get('task_status')

        if False and cached_status_list:
            return JsonResponse({'results': cached_status_list})
        else:

            results_list = []

            # Get most recent 5 tasks
            tasks = self.get_annotated_list(self.get_queryset().order_by('-id')[:5])

            for task in tasks:

                date_done = date_convert(task.date_done)
                if task.status == 'STARTED':
                    date_done = ''

                result = ""
                try:
                    result = task.safe_result.get('result',"")
                except:
                    result = ""
                try:
                    start_date = date_convert(task.safe_result.get('start_date',""))
                except:
                    start_date = "-"
                if result and task.status != 'STARTED':
                    formatted_result = result.strip('\"').replace("\\n", "<br />")
                else:
                    formatted_result = ""

                results_list.append({
                    'pk': task.id,
                    'id': task.task_id,
                    'task_name': task.task_name,
                    'display_name': task.display_name,
                    'status': task.status,
                    'date_done': date_done,
                    'date_started': start_date,
                    'user': getattr(task.requester, "email", "Unknown"),
                    'result': formatted_result
                })

            cache.set('task_status', results_list)

            return JsonResponse({'results': results_list})
