from django.test import TestCase
from django.templatetags.static import static
from django.contrib.auth import get_user_model

from emp_demo_ui_app.apps import app_url_prefix

class TestEMPBaseView(TestCase):
    """
    Correct opertation of check_permissions_for_url() of the EmpBaseView is
    also tested as art of emp_demo_ui_app.tests.test_views.TestDemoUIPageView .

    TODO: Check that expected values are in context and that the navbar content is loaded as expected.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Create test users and two pages with appropriate permissions.
        """
        User = get_user_model()
        cls.anon_user = User.get_anonymous()
        cls.welcome_page_url = "/welcome/"
        # This is used to ensure the welcome page can actually be accessed.
        cls.urls_whitelist = [
            "/welcome/",
        ]

    def test_welcome_page_access_denied_if_not_whitelisted(self):
        """
        Verify that access to pages is deinied that are not whitelisted nor
        part of an UI app.
        """
        with self.settings(URLS_PERMISSION_WHITELIST=[]):
            response = self.client.get(self.welcome_page_url)
            self.assertEqual(response.status_code, 403)

    def test_welcome_page_access_granted_if_whitelisted(self):
        """
        Verify that access to pages is deinied that are not whitelisted nor
        part of an UI app.
        """
        with self.settings(URLS_PERMISSION_WHITELIST=self.urls_whitelist):
            response = self.client.get(self.welcome_page_url)
            self.assertEqual(response.status_code, 200)

    def test_page_customization_values_in_context(self):
        """
        Test that the values to customize the emp are loaded correctly from
        settings and added to the page context.
        """
        expected_context_keys = [
            "PAGE_TITLE",
            "MANIFEST_JSON_STATIC",
            "FAVICON_ICO_STATIC",
            "TOPBAR_LOGO_STATIC",
            "TOPBAR_NAME_SHORT",
            "TOPBAR_NAME_LONG",
        ]

        with self.settings(URLS_PERMISSION_WHITELIST=self.urls_whitelist):
            expected_context_value = "test-context-stuff"

            for expected_context_key in expected_context_keys:
                settings_override = {
                    expected_context_key: expected_context_value,
                }
                with self.settings(**settings_override):
                    response = self.client.get(self.welcome_page_url)
                    self.assertEqual(response.status_code, 200)

                    self.assertIn(expected_context_key, response.context)
                    test_content = response.context[expected_context_key]
                    if "_STATIC" in expected_context_key:
                        # Static setting options will be parsed to static
                        # address by the view.
                        expected_context_value = static(expected_context_value)
                    self.assertEqual(
                        test_content,
                        expected_context_value
                    )


class TestEMP403View(TestCase):
    @classmethod
    def setUpTestData(cls):
        # This is an url to a page which does not exist.
        page_slug_na = "test-page-na"
        cls.page_na_url = (
            "/" + app_url_prefix + "/" +page_slug_na + "/"
        )

    def test_correct_template_used(self):
        response = self.client.get(self.page_na_url)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, 'emp_main/403.html')

