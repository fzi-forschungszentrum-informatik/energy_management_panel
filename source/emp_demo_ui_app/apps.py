from collections import OrderedDict

from django.apps import AppConfig


class EmpDemoUiAppConfig(AppConfig):
    """
    This is partly Django default functionality, extended with some EMP
    specific code.
    """
    name = 'emp_demo_ui_app'

    # The first part of the url, that is used to identify the pages
    # belongig to this app. No leading or trailing slashes, they will
    # be added where needed by the functions using this string.
    app_url_prefix = "demoapp"


def get_app_nav_content_for_user(user):
    """
    Return a list of all page names and urls that this user has access to.

    This is a staticmethod as we want to call it without creating an
    instance of the Config class, e.g. as the later would also involve
    the ready() function, that may include potentially expensive
    operations.

    Parameters
    ----------
    user : django.contrib.auth.model.User
        The user for which the the available pages should be computed.

    Returns
    -------
    OrderedDict
        as {"name of nav group": {"name of page 1": "url of page 1", ...}}
    """

    def mk_full_url(url):
        return "/" + EmpDemoUiAppConfig.app_url_prefix + "/" + url + "/"

    # These are ordered dicts, in case the ordering of the nav items
    # is important, then it can be defined here explictly.
    app_nav_content = OrderedDict()

    # Be sure to use slugs here for url components.
    # Also ensure that any user gets a copy of the pages the AU gets and
    # that inactive users get not more permissions then the AU.
    app_pages = OrderedDict()
    app_pages["Demo Page 1"] = mk_full_url("page-1")
    app_pages["Demo Page 2"] = mk_full_url("page-2")

    app_nav_content["Demo UI App"] = app_pages

    return  app_nav_content

