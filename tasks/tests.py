from datetime import datetime
from urllib import request, response
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from tasks.models import STATUS_CHOICES, Task
from tasks.tasks import send_mail_reminder


from tasks.views import (
    GenericTaskView,
    GenericCompletedTaskView,
    GenericTaskCompleteView,
)


from .views import GenericAllTaskView, GenericTaskView


class ViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="John Doe", email="johndoe@gmail.com", password="helloworld12345"
        )

    # test to check if a an anonymous user can view the /tasks/ page
    def test_is_authenticated_user_is_not_logged_in(self):
        request = self.factory.get("/tasks/")
        request.user = AnonymousUser()
        response = GenericTaskView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/user/login?next=/tasks/")

    # test to check if a logged in user can acces the /tasks/ page
    def test_is_authenticated_user_is_logged_in(self):
        request = self.factory.get("/tasks/")
        request.user = self.user
        response = GenericTaskView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    # test to check the user login view
    def test_userloginview(self):
        response = self.client.get("/user/login")
        self.assertEqual(response.status_code, 200)

    # test to check the user create view
    def test_usercreateview(self):
        response = self.client.get("/user/signup")
        self.assertEqual(response.status_code, 200)

    # test to check the completed task view
    def test_genericompletedtaskview(self):
        request = self.factory.get("/completed_tasks")
        request.user = self.user
        response = GenericCompletedTaskView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    # test to check the all tasks view
    def test_genericalltaskview(self):
        request = self.factory.get("/all_tasks/")
        request.user = self.user
        response = GenericAllTaskView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    # test to check the task create view and the working of the priority
    def test_generic_task_create_view(self):
        self.client.login(username="John Doe", password="helloworld12345")

        response = self.client.post(
            "/create-task/",
            {
                "title": "Task 1",
                "description": "This is the description of task 1",
                "priority": 1,
                "completed": False,
                "status": STATUS_CHOICES[0][1],
            },
        )
        # checking whether a task has been created successfully
        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            "/create-task/",
            {
                "title": "Task 2",
                "description": "This is the description of task 2",
                "priority": 1,
                "completed": False,
                "status": STATUS_CHOICES[0][1],
            },
        )
        # checking whether a task with same priority has been added
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Task.objects.get(priority=1, user=self.user).title, "Task 2")
        self.assertEqual(Task.objects.get(priority=2, user=self.user).title, "Task 1")
        # checking whether the priority function is working as intended

    # test to check the task update view
    def test_generic_task_update_view(self):
        self.client.login(username="John Doe", password="helloworld12345")

        task = Task(
            title="Task 1",
            priority="2",
            status=STATUS_CHOICES[1][1],
            description="This is the description of task 1",
            completed=False,
            user=self.user,
        )
        task.save()
        print(task.id)
        response = self.client.post(
            f"/update-task/{task.id}/",
            {
                "title": "Task 1 updated",
                "priority": 1,
                "completed": False,
                "status": STATUS_CHOICES[0][1],
                "description": "This is the description of task 1",
            },
        )

        # checking whether the task has been updated successfully
        self.assertEqual(response.status_code, 302)

        task = Task.objects.get(id=task.id)
        self.assertEqual(task.title, "Task 1 updated")
        self.assertEqual(task.priority, 1)

    # test to check the complete task view
    def test_complete_task_view(self):
        self.client.login(username="John Doe", password="helloworld12345")

        task = Task(
            title="Task 1",
            priority=1,
            completed=False,
            description="This is task 1",
            status=STATUS_CHOICES[0][1],
            user=self.user,
        )
        task.save()

        response = self.client.post(f"/complete_task/{task.id}/")

        task = Task.objects.get(id=task.id)
        self.assertEqual(task.completed, True)

    # test to check the delete task view
    def test_delete_task_view(self):
        self.client.login(username="John Doe", password="helloworld12345")

        task = Task(
            title="Task 1",
            priority=1,
            completed=False,
            description="This is task 1",
            status=STATUS_CHOICES[0][1],
            user=self.user,
        )
        task.save()

        response = self.client.post(f"/delete-task/{task.id}/")
        self.assertEqual(response.url, "/tasks")
        self.assertEqual(Task.objects.filter(id=task.id).exists(), False)

    # test to check the detail task view
    def test_detail_task_view(self):
        self.client.login(username="John Doe", password="helloworld12345")

        task = Task(
            title="Task 1",
            priority=1,
            completed=False,
            description="This is task 1",
            status=STATUS_CHOICES[0][1],
            user=self.user,
        )
        task.save()

        response = self.client.get(f"/detail-task/{task.id}/")
        self.assertEqual(response.status_code, 200)

    def test_reminder(self):
        self.client.login(username="John Doe", password="helloworld12345")

        response = self.client.post(
            "/reminder", {"alert_time": datetime.now(), "timezone": "UTC"}
        )
        send_mail_reminder.delay()

        self.assertEqual(response.url, "/tasks")



# test for the api views
class APIViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="John Doe", email="johndoe@gmail.com", password="helloworld12345"
        )

    def test_api_list_view(self):
        self.client.login(username="John Doe", password="helloworld12345")
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code,200)

    def test_api_list_view_createTask(self):
        self.client.login(username="John Doe", password="helloworld12345")

        task = Task(
            title="Task 1",
            priority=1,
            completed=False,
            description="This is task 1",
            status=STATUS_CHOICES[0][1],
            user=self.user,
        )
        task.save()

        response = self.client.get(f"/api/tasks/{task.id}/")
        self.assertEqual(response.status_code,200)

    def test_api_history_view(self):
        self.client.login(username="John Doe", password="helloworld12345")
        response = self.client.get("/api/history/task/")
        self.assertEqual(response.status_code,200)