from django.test import TestCase, Client
from django.urls import reverse


class GetCookieViewTestCase(TestCase):
    def test_get_cookie_view(self):
        header = {"HTTP_USER_AGENT": "Test"}
        response = self.client.get(reverse("myauth:cookie-get"), HTTP_USER_AGENT="Test")
        self.assertContains(response, "Cookie value")


# class FooBarViewTestCase(TestCase):
#     def test(self):
#         response = self.client.get(reverse("myauth:cookie-get"), HTTP_USER_AGENT="Test")
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.headers["content-type"], "application/json")
#         expected_data = {}
#         self.assertJSONEqual(expected_data, response.content)
