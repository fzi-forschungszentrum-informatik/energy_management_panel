from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from guardian.shortcuts import assign_perm


from ..models import DemoAppPage
from ..apps import app_url_prefix


class TestDemoUIPageView(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Create test users and two pages with appropriate permissions.
        """
        User = get_user_model()
        cls.test_user_1 = User.objects.create_user(username="u1", password="p1")
        cls.test_user_2 = User.objects.create_user(username="u2", password="p2")
        cls.anon_user = User.get_anonymous()

        # This page should be visable to anybody.
        page_slug_1 = "test-page-1"
        cls.page_1_url = "/" + app_url_prefix + "/" + page_slug_1 + "/"
        cls.expected_page_content_1 = "Content 1"
        cls.expected_page_background_color_1 = "red"
        cls.page1 = DemoAppPage.objects.create(
            page_name="Test Page 1",
            page_slug=page_slug_1,
            page_content=cls.expected_page_content_1,
            page_background_color=cls.expected_page_background_color_1,
        )
        assign_perm("emp_demo_ui_app.view_demoapppage", cls.anon_user, cls.page1)

        # This page should be visable to anybody.
        page_slug_2 = "test-page-2"
        cls.page_2_url = "/" + app_url_prefix + "/" + page_slug_2 + "/"
        cls.expected_page_content_2 = "Content 2"
        cls.expected_page_background_color_2 = "yellow"
        cls.page2 = DemoAppPage.objects.create(
            page_name="Test Page 2",
            page_slug=page_slug_2,
            page_content=cls.expected_page_content_2,
            page_background_color=cls.expected_page_background_color_2,
        )
        assign_perm("emp_demo_ui_app.view_demoapppage", cls.test_user_1, cls.page2)

        # This is an url to a page which does not exist.
        page_slug_na = "test-page-na"
        cls.page_na_url = "/" + app_url_prefix + "/" + page_slug_na + "/"

    def test_page_background_color_in_context(self):
        """
        The page background color is required by the template.
        """
        response = self.client.get(self.page_1_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("page_background_color", response.context)
        test_background_color = response.context["page_background_color"]
        self.assertEqual(test_background_color, self.expected_page_background_color_1)

    def test_page_content_in_context(self):
        """
        The page_content is required by the template.
        """
        response = self.client.get(self.page_1_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("page_content", response.context)
        test_content = response.context["page_content"]
        self.assertEqual(test_content, self.expected_page_content_1)

    def test_correct_template_used(self):
        response = self.client.get(self.page_1_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "./emp_demo_ui_app/demo_page.html")

    def test_invalid_page_slug_returns_403(self):
        """
        The emp doesn't distinguish between pages that do not exist and those
        for which the user has no permissions, for performance reasons, and
        always returns 403 in such cases.
        """
        response = self.client.get(self.page_na_url)
        self.assertEqual(response.status_code, 403)

    # Redirecting to the login page is currently not installed, this could
    # change later.
    #
    # def test_redirect_if_not_logged_in(self):
    #     """
    #     If a anon user tries to access a page which the anon user has no
    #     permissions for, he/she should be redirected to the login page.
    #     """
    #     response = self.client.get(self.page_2_url)
    #     self.assertRedirects(
    #         response,
    #         '/accounts/login/?next=' + self.page_2_url
    #     )

    def test_page_loaded_for_logged_in_user_with_permissions(self):
        """
        This user has permissions, should thus be able to load the page.
        """
        client = Client()
        login_success = client.login(username="u1", password="p1")
        self.assertTrue(login_success)

        response = client.get(self.page_2_url)
        self.assertEqual(response.status_code, 200)

    def test_page_returns_403_for_logged_in_user_without_permissions(self):
        """
        This user is authenticated but has not permissions for the page.
        """
        client = Client()
        login_success = client.login(username="u2", password="p2")
        self.assertTrue(login_success)

        response = client.get(self.page_2_url)
        self.assertEqual(response.status_code, 403)
