from cgi import test
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path
from tasks.models import Task
from tasks.views import (
    GenericAllTaskView,
    GenericCompletedTaskView,
    GenericTaskCompleteView,
    GenericTaskCreateView,
    GenericTaskDeleteView,
    GenericTaskDetailView,
    GenericTaskUpdateView,
    GenericTaskView,
    UserCreateView,
    UserLoginView,
    session_storage_view,
    ReminderTimeSetView,
)

from tasks.apiviews import TaskHistoryViewSet, TaskListAPI

from rest_framework.routers import SimpleRouter

from tasks.apiviews import TaskViewSet

from tasks.tasks import test_background_jobs

from django.http import HttpResponse


def test_bg(request):
    test_background_jobs.delay()
    return HttpResponse("All Good Here")


router = SimpleRouter()
router.register(prefix="api/tasks", viewset=TaskViewSet)
router.register(prefix="api/history/task", viewset=TaskHistoryViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("taskapi/", TaskListAPI.as_view()),
    # path("createtaskapi/", TaskCreateAPI.as_view()),
    path("tasks/", GenericTaskView.as_view()),
    path("create-task/", GenericTaskCreateView.as_view()),
    path("delete-task/<pk>/", GenericTaskDeleteView.as_view()),
    path("complete_task/<pk>/", GenericTaskCompleteView.as_view()),
    path("completed_tasks/", GenericCompletedTaskView.as_view()),
    path("all_tasks/", GenericAllTaskView.as_view()),
    path("update-task/<pk>/", GenericTaskUpdateView.as_view()),
    path("detail-task/<pk>/", GenericTaskDetailView.as_view()),
    path("sessiontest", session_storage_view),
    path("user/signup", UserCreateView.as_view()),
    path("user/login", UserLoginView.as_view()),
    path("reminder", ReminderTimeSetView.as_view()),
    path("user/logout", LogoutView.as_view()),
    path("test_bg", test_bg),
] + router.urls
