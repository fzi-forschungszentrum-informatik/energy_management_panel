from django.test import TestCase
from django.db.utils import IntegrityError

from ..models import DemoAppPage

class TestDemoAppPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Create one object of the DemoAppPage for the tests.
        """
        cls.expected_page_name = "Test Page 1"
        cls.expected_page_slug = "test-page-1"
        cls.expected_page_content = "Test content string."
        # This should be default.
        cls.expected_background_color = "transparent"

        DemoAppPage.objects.create(
            page_name = cls.expected_page_name,
            page_slug = cls.expected_page_slug,
            page_content = cls.expected_page_content
        )

        cls.test_app_page = DemoAppPage.objects.get(id=1)

    def test_field_page_name_exists(self):
        """
        This field is required as entry in the nav bar.
        """
        self.assertEqual(self.test_app_page.page_name, self.expected_page_name)

    def test_field_page_name_not_too_long(self):
        """
        The page name will overflow the navbar border if longer then 18 chars.
        """
        max_length = self.test_app_page._meta.get_field('page_name').max_length
        self.assertGreaterEqual(18, max_length)

    def test_field_page_slug_exists(self):
        """
        This field is required to generate the urls of the pages.
        """
        self.assertEqual(self.test_app_page.page_slug, self.expected_page_slug)

    def test_field_page_slug_is_unique(self):
        """
        page_slug is used as part of the page URL and must be unique thus.
        """
        with self.assertRaises(IntegrityError):
            DemoAppPage.objects.create(
                page_name = "Unique page name",
                page_slug = self.expected_page_slug,
                page_content = "Unique content",
            )

    def test_field_page_content_exists(self):
        """
        This field is required as it is expected by the DemoUIPageView.
        """
        self.assertEqual(
            self.test_app_page.page_content,
            self.expected_page_content
        )

    def test_field_page_background_color_exists(self):
        """
        This field is required as it is expected by the DemoUIPageView.
        """
        self.assertEqual(
            self.test_app_page.page_background_color,
            self.expected_background_color
        )
