from django.test import TestCase
from django.contrib.auth import get_user_model

from ..apps import EmpAppsCache

class TestEmpAppsCache(TestCase):
    """
    TODO: Extend this.
    """

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username="u1", password="p1")
        cls.anon = User.get_anonymous()

    def setUp(self):
        """
        Reset the apps cache before every test.
        """
        del EmpAppsCache._instance
        self.apps_cache = EmpAppsCache()

    def test_empty_apps_cache_for_tests(self):
        """
        Some of the tests below might rely on an empty cache, confirm that the
        empty mechanism works.
        """
        self.assertFalse(self.apps_cache.apps_nav_content)
        self.assertFalse(self.apps_cache.allowed_urls)
        self.assertFalse(self.apps_cache.allowed_datapoints)

