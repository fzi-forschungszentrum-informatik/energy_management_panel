from django.apps import AppConfig

from collections import OrderedDict

from django.contrib.auth import get_user_model

class EmpEvaluationSystemConfig(AppConfig):
    name = 'emp_evaluation_system'

# The first part of the url, that is used to identify the pages
# belongig to this app. No leading or trailing slashes, they will
# be added where needed by the functions using this string.
app_url_prefix = "evaluation_system"

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
    pages_user = get_objects_for_user(user, "emp_evaluation_system.view_evaluationsystempage")
    pages_anon = get_objects_for_user(anon, "emp_evaluation_system.view_evaluationsystempage")
    pages_all = pages_user.union(pages_anon)

    # Be sure to use slugs here for url components.
    # Also ensure that any user gets a copy of the pages the AU gets and
    # that inactive users get not more permissions then the AU.
    app_pages = OrderedDict()
    for page_obj in pages_all:
        app_pages[page_obj.page_name] = page_obj.get_absolute_url()
    app_nav_content["EMP Evaluation System"] = app_pages

    return  app_nav_content

