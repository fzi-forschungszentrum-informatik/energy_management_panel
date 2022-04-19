from unittest.mock import MagicMock

from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from emp_main.apps import EmpAppsCache


class TestUpdateUserPermissions(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username="u1", password="p1")
        cls.anon = User.get_anonymous()

    def test_login_triggers_update_user_permissions(self):
        """
        Login should trigger an update to user permissions to propagate DB changes.
        """
        # Overload the get_instance method with mock so we can test if it
        # has been called.
        apps_cache = EmpAppsCache.get_instance()
        apps_cache.update_for_user = MagicMock()

        client = Client()
        login_success = client.login(username="u1", password="p1")
        self.assertTrue(login_success)

        # Verify that the permissions have been updated for the normal
        # and anon user.
        apps_cache.update_for_user.assert_any_call(user=self.anon)
        apps_cache.update_for_user.assert_any_call(user=self.user)

        # Undo the mock overload. EmpAppsCache is designed to live in the
        # background beyond the lifetime of the instances created from it.
        # Hence ensure that the overloaded method does not survive.
        del apps_cache
        del EmpAppsCache._instance
        EmpAppsCache()
