from collections import OrderedDict

from django.apps import AppConfig


class EmpLocationsConfig(AppConfig):
    """
    This is partly Django default functionality, extended with some EMP
    specific code.
    """
    name = 'emp_locations'


# The first part of the url, that is used to identify the pages
# belongig to this app. No leading or trailing slashes, they will
# be added where needed by the functions using this string.
app_url_prefix = "location"


def get_app_nav_content_for_user(user):
    """
    Return a list of all page names and urls that this user has access to.

    Allow all locations for now for development.

    Parameters
    ----------
    user : django.contrib.auth.model.User
        The user for which the the available pages should be computed.

    Returns
    -------
    app_nav_content: OrderedDict
        as {"name of nav group": {"name of page 1": "url of page 1", ...}}
    """
    from .models import Location

    # These are ordered dicts, in case the ordering of the nav items
    # is important, then it can be defined here explictly.
    app_nav_content = OrderedDict()

    locations_all = Location.objects.all()

    # Be sure to use slugs here for url components.
    # Also ensure that any user gets a copy of the pages the AU gets and
    # that inactive users get not more permissions then the AU.
    app_pages = OrderedDict()
    for location_obj in locations_all:
        app_pages[location_obj.name] = location_obj.get_absolute_url()
    app_nav_content["Locations"] = app_pages

    return  app_nav_content

def get_permitted_datapoint_ids_for_user(user):
    """
    Returns a list of all ids of datapoints the user has access to.

    This currently returns all Datapoints to simplify development. This
    should be changed later.

    Parameters
    ----------
    user : django.contrib.auth.model.User
        The user for which the the permitted datapoints should be computed.

    Returns
    -------
    datapoint_ids: set
        as e.g. {1, 23, 49}
    """
    from emp_main.models import Datapoint

    all_datapoints = Datapoint.objects.all()
    datapoint_ids = set()
    for datapoint in all_datapoints:
        datapoint_ids.add(datapoint.id)
    return datapoint_ids
