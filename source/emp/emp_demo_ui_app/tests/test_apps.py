from django.test import TestCase
from django.contrib.auth import get_user_model
from guardian.shortcuts import assign_perm

from ..models import DemoAppPage
from ..apps import app_url_prefix
from ..apps import get_app_nav_content_for_user


class TestGetAppNavContentForUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Create test users and two pages with appropriate permissions.
        """
        User = get_user_model()
        cls.test_user_1 = User.objects.create_user(username="u1", password="p1")
        cls.anon_user = User.get_anonymous()

        cls.expected_page_name_1 = "Test Page 1"
        cls.expected_page_slug_1 = "test-page-1"
        cls.page1 = DemoAppPage.objects.create(
            page_name=cls.expected_page_name_1,
            page_slug=cls.expected_page_slug_1,
            page_content="",
        )
        assign_perm(
            "emp_demo_ui_app.view_demoapppage", cls.anon_user, cls.page1
        )

        # This page only to test_user_1
        cls.expected_page_name_2 = "Test Page 2"
        cls.expected_page_slug_2 = "test-page-2"
        cls.page2 = DemoAppPage.objects.create(
            page_name=cls.expected_page_name_2,
            page_slug=cls.expected_page_slug_2,
            page_content="",
        )
        assign_perm(
            "emp_demo_ui_app.view_demoapppage", cls.test_user_1, cls.page2
        )

    def test_navbar_group_name_in_content_dict(self):
        """
        The correct nav group name here is "Demo Ui App".
        """
        app_nav_content = get_app_nav_content_for_user(self.anon_user)
        self.assertIn("Demo UI App", app_nav_content)

    def test_restricted_page_not_visable_for_anon_user(self):
        """
        The anon user should have no access to the pages which no permissions
        where granted.
        """
        app_nav_content = get_app_nav_content_for_user(self.anon_user)
        app_pages = app_nav_content["Demo UI App"]
        self.assertNotIn(self.expected_page_name_2, app_pages)

    def test_restricted_page_visable_for_granted_user(self):
        """
        The user who was granted permissions to a specific page should have
        access.
        """
        app_nav_content = get_app_nav_content_for_user(self.test_user_1)
        app_pages = app_nav_content["Demo UI App"]
        self.assertIn(self.expected_page_name_2, app_pages)

    def test_page_url_correct(self):
        app_nav_content = get_app_nav_content_for_user(self.anon_user)
        page_url = app_nav_content["Demo UI App"][self.expected_page_name_1]
        expected_page_url = (
            "/" + app_url_prefix + "/" + self.expected_page_slug_1 + "/"
        )
        self.assertEqual(page_url, expected_page_url)
