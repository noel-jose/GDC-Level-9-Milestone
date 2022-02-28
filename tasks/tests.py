from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User

from .views import GenericTaskView


class QuestionModelTest(TestCase):
    # def test_always_fail(self):
    #     """
    #     This test will always fail
    #     """
    #     self.assertIs(True, False)

    # def test_authenticated(self):
    #     """
    #     Try to GET the task listing page, expect the result to be redirected to the login page
    #     """
    #     response = self.client.get("/tasks")
    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(response.url, "user/login?next=/tasks")

    def setUp(self):
        # every  test needs access to the request factoru
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="bruce_wayne",
            email="bruce_wayne@gmail.com",
            password="i_am_batman",
        )

    def test_authenticated(self):
        """
        Try to GET task listing page, expect the response to redirect to the login page
        """

        # create an instance of get request
        request = self.factory.get("/tasks")
        # set the user instance on the request
        request.user = self.user
        # we simply create the view and call it like a regular functino
        response = GenericTaskView.as_view()(request)
        # since we are authenticated we get a 200 response
        self.assertEqual(response.status_code, 200)
