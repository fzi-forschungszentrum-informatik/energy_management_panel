from collections import OrderedDict

from django.apps import AppConfig


class EmpEnergyFlow(AppConfig):
    """
    This is partly Django default functionality, extended with some EMP
    specific code.
    """

    name = "emp_energy_flow"


# The first part of the url, that is used to identify the pages
# belongig to this app. No leading or trailing slashes, they will
# be added where needed by the functions using this string.
app_url_prefix = "energyflow"


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

    # Get the pages the user has access too.
    pages_user = get_objects_for_user(user, "emp_energy_flow.view_energyflow")
    pages_user = pages_user.filter(is_active=True).order_by("name")

    # Be sure to use slugs here for url components.
    # Also ensure that any user gets a copy of the pages the AU gets and
    # that inactive users get not more permissions then the AU.
    app_pages = OrderedDict()
    for page_obj in pages_user:
        app_pages[page_obj.name] = page_obj.get_absolute_url()
    app_nav_content["Energy Flow"] = app_pages

    return app_nav_content


def get_permitted_datapoint_ids_for_user(user):
    """
    Returns a list of all ids of datapoints the user has access to.

    TODO: Restrict here.

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
    from .models import EnergyFlow, Widget

    datapoint_ids = set()
    for widget in Widget.objects.all():
        if not widget.is_active or widget.energyflow is None:
            continue
        if widget.datapoint1 is not None:
            datapoint_ids.add(widget.datapoint1.id)
        if widget.datapoint2 is not None:
            datapoint_ids.add(widget.datapoint2.id)

    return datapoint_ids
