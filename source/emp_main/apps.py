import logging
from collections import OrderedDict
from importlib import import_module

from django.contrib import auth
from django.conf import settings
from django.apps import AppConfig
from django.utils.text import slugify

logger = logging.getLogger(__name__)


class EmpMainConfig(AppConfig):
    name = 'emp_main'

    def ready(self):
        EmpUiAppsCache()


class EmpUiAppsCache():
    """
    A cache for the user specfic objects per EMP UI apps.

    This caches the navbar content for each user, as well as the urls and
    datapoints the respective user has permissions for. Computing these values
    is potentially expensive as it may result in multiple dynamic imports and
    database lookups. Hence we update these values only when triggered.
    """

    def __new__(cls, *args, **kwargs):
        """
        Ensure singleton, i.e. only one instance is created.
        """
        if not hasattr(cls, "_instance"):
            # This magically calls __init__ with the correct arguements too.
            cls._instance = object.__new__(cls)
        else:
            logger.warning(
                "EMPAppsCache is aldready running. Use "
                "get_instance method to retrieve the running instance."
            )
        return cls._instance

    @classmethod
    def get_instance(cls):
        """
        Return the running instance of the class.

        Returns:
        --------
        instance: EMPAppsCache instance
            The running instance of the class. Is none of not running yet.
        """
        if hasattr(cls, "_instance"):
            instance = cls._instance
        else:
            instance = None
        return instance

    def __init__(self):
        """
        Create all shared objects of the class
        """
        logger.info("Starting EMPAppsCache.")

        # These store the user specific objects. apps_nav_content stores the
        # data required to populate the user specific nav bar. allowed_urls is
        # used to check whether the user has the right to open a page.
        # allowed_datapoints is used to check whether the user is allowed to
        # receive the values of a specific datapoint.
        self.apps_nav_content = {}
        self.allowed_urls = {}
        self.allowed_datapoints = {}

    def update_for_user(self, user=None):
        """
        Update all user specifc objects per EMP app.

        Parameters
        ----------
        user : django.contrib.auth.model.User, optional
            The user for which the updates will be computed. Will compute
            for all users if None.

        Returns
        -------
        None.
        """
        # Update for all known users if no user is specfied.
        if user is None:
            user_model = auth.get_user_model()
            users = list(user_model.objects.all())
            # Also update for the AnonymousUser (not returned by the query).
            users += [auth.models.AnonymousUser()]
            for user in users:
                self.update_for_user(user)
            return

        # Erase all previous user specific objects.
        self.apps_nav_content[user] = OrderedDict()
        self.allowed_urls[user] = set()
        self.allowed_datapoints[user] = set()

        # Iterate over all UI apps of the EMP to compute all required data.
        for emp_app in settings.EMP_APPS:
            app_config = import_module(emp_app + ".apps")


            # Compute the nav group name, pages and urls for this user.
            # Extend with an id that is used for collapsing the subnav.
            app_nav_content = app_config.get_app_nav_content_for_user(user)
            for app_nav_name, app_nav_pages in app_nav_content.items():
                # Add the emp_app string to ensure the id is unique.
                app_nav_id = slugify(emp_app + app_nav_name)
                app_nav_content_new = {
                    "app_nav_id": app_nav_id,
                    "app_nav_pages": app_nav_pages,
                }
                self.apps_nav_content[user][app_nav_name] = app_nav_content_new

                # Also store all allowed urls for this user, by assuming he/she
                # is only permitted to access those urls that are part of the
                # navbar.
                self.allowed_urls[user].update(app_nav_pages.values())

            # Finally also update the permitted datapoints.
            # TODO.

    def get_apps_nav_content_for_user(self, user):
        """
        Returns the apps_nav_content for this user.

        Will take it from cache or trigger recomputation if not in cache.

        Parameters
        ----------
        user : django.contrib.auth.model.User, optional
            The user for which the updates will be computed. Will compute
            for all users if None.

        Returns
        -------
        OrderedDict
            as: {
                "name of nav group": {
                    "app_nav_id": String,
                    "app_nav_pages": {
                        "name of page 1": "url of page 1",
                        ...
                    }
                }}
        """
        if not user in self.apps_nav_content:
            self.update_for_user(user)
        return self.apps_nav_content[user]

    def get_allowed_urls_for_user(self, user):
        """
        Returns the allowed_urls for this user.

        Will take it from cache or trigger recomputation if not in cache.

        Parameters
        ----------
        user : django.contrib.auth.model.User, optional
            The user for which the updates will be computed. Will compute
            for all users if None.

        Returns
        -------
        Set
            Of all urls (relative parts only) the user has permissions to
            access.
        """
        if not user in self.allowed_urls:
            self.update_for_user(user)
        return self.allowed_urls[user]

    def get_allowed_datapoints_for_user(self, user):
        """
        Returns the allowed_datapoints for this user.

        Will take it from cache or trigger recomputation if not in cache.

        Parameters
        ----------
        user : django.contrib.auth.model.User, optional
            The user for which the updates will be computed. Will compute
            for all users if None.

        Returns
        -------
        Set
            Of all Datapoints the user has permissions to access.
        """
        if not user in self.allowed_datapoints:
            self.update_for_user(user)
        return self.allowed_datapoints[user]
