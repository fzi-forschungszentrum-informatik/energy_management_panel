from collections import OrderedDict

from django.apps import AppConfig
from django.contrib.auth import get_user_model


class EmpDemoUiAppConfig(AppConfig):
    """
    This is partly Django default functionality, extended with some EMP
    specific code.
    """

    name = "emp_demo_ui_app"


# The first part of the url, that is used to identify the pages
# belongig to this app. No leading or trailing slashes, they will
# be added where needed by the functions using this string.
app_url_prefix = "demo"


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
    app_nav_content: OrderedDict
        as {"name of nav group": {"name of page 1": "url of page 1", ...}}
    """
    # This import must be here as it cannot succeed until all apps are loaded.
    from guardian.shortcuts import get_objects_for_user

    # These are ordered dicts, in case the ordering of the nav items
    # is important, then it can be defined here explictly.
    app_nav_content = OrderedDict()

    # Get the anonymous user object.
    anon = get_user_model().get_anonymous()

    # Get the pages for the user and extend these with the pages the
    # anonymous user has access to.
    pages_user = get_objects_for_user(user, "emp_demo_ui_app.view_demoapppage")
    pages_anon = get_objects_for_user(anon, "emp_demo_ui_app.view_demoapppage")
    pages_all = pages_user.union(pages_anon).order_by("page_name")

    # Be sure to use slugs here for url components.
    # Also ensure that any user gets a copy of the pages the AU gets and
    # that inactive users get not more permissions then the AU.
    app_pages = OrderedDict()
    for page_obj in pages_all:
        app_pages[page_obj.page_name] = page_obj.get_absolute_url()
    app_nav_content["Demo UI App"] = app_pages

    return app_nav_content


def get_permitted_datapoint_ids_for_user(user):
    """
    Returns a list of all ids of datapoints the user has access to.

    This is a staticmethod as we want to call it without creating an
    instance of the Config class, e.g. as the later would also involve
    the ready() function, that may include potentially expensive
    operations.

    Parameters
    ----------
    user : django.contrib.auth.model.User
        The user for which the the permitted datapoints should be computed.

    Returns
    -------
    datapoint_ids: set
        as e.g. {1, 23, 49}
    """
    # This import must be here as it cannot succeed until all apps are loaded.
    from guardian.shortcuts import get_objects_for_user

    # Get the anonymous user object.
    anon = get_user_model().get_anonymous()

    # Get the pages for the user and extend these with the pages the
    # anonymous user has access to.
    pages_user = get_objects_for_user(user, "emp_demo_ui_app.view_demoapppage")
    pages_anon = get_objects_for_user(anon, "emp_demo_ui_app.view_demoapppage")
    pages_all = pages_user.union(pages_anon)

    datapoint_ids = set()
    for page in pages_all:
        if page.demo_datapoint is not None:
            datapoint_ids.add(page.demo_datapoint.id)
    return datapoint_ids
