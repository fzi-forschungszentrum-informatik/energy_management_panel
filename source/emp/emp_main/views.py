import json
import logging
from collections import OrderedDict

from django.conf import settings
from django.utils.text import slugify
from django.views.generic import TemplateView
from django.templatetags.static import static
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from rest_framework.response import Response

from emp_main.apps import EmpAppsCache
from emp_main.models import Datapoint
from emp_main.models import DatapointValue
from emp_main.models import DatapointSchedule
from emp_main.models import DatapointSetpoint
from ems_utils.message_format.views import DatapointViewSetTemplate
from ems_utils.message_format.views import DatapointValueViewSetTemplate
from ems_utils.message_format.views import DatapointScheduleViewSetTemplate
from ems_utils.message_format.views import DatapointSetpointViewSetTemplate
from .serializers import DatapointSerializer
from .filters import DatapointFilter, DatapointValueFilter
from .filters import DatapointSetpointFilter, DatapointScheduleFilter

logger = logging.getLogger(__name__)


class EMPBaseView(TemplateView):
    """
    Like the normal TemplateView but automatically extends the context with
    all data required for all pages, that is, for the base.html template.
    """
    def check_permissions_for_url(self, user):
        """
        Check if the user has permissions to access the requested url.

        Arguments:
        ----------
        user: Django user object
            The user for which permissions should be checked.

        Raises:
        -------
        PermissionDenied:
            If the user has no permissions to access the URL.
        """
        apps_cache = EmpAppsCache.get_instance()

        requested_url = self.request.path_info
        if requested_url not in settings.URLS_PERMISSION_WHITELIST:
            allowed_urls = apps_cache.get_allowed_urls_for_user(user)
            if requested_url not in allowed_urls:
                logger.info(
                    "EMPBaseView blocked request by user %s to access page %s. "
                    "Allowed pages are:\n%s",
                    *(
                        user,
                        requested_url,
                        json.dumps(sorted(allowed_urls), indent=2)
                    )
                )
                raise PermissionDenied

    def get_context_data(self, **kwargs):

        # Replace the django default anon user with the Guardian version,
        # as these are not identical and we thus retrieve incorrect page
        # permissions for the django anon user.
        user = self.request.user
        if user.is_anonymous:
            user = get_user_model().get_anonymous()

        # Check permissions first.
        self.check_permissions_for_url(user=user)

        # Add page customization for template to context.
        context = super().get_context_data(**kwargs)
        context["PAGE_TITLE"] = settings.PAGE_TITLE
        context["MANIFEST_JSON_STATIC"] = static(settings.MANIFEST_JSON_STATIC)
        context["FAVICON_ICO_STATIC"] = static(settings.FAVICON_ICO_STATIC)
        context["TOPBAR_LOGO_STATIC"] = static(settings.TOPBAR_LOGO_STATIC)
        context["TOPBAR_NAME_SHORT"] = settings.TOPBAR_NAME_SHORT
        context["TOPBAR_NAME_LONG"] = settings.TOPBAR_NAME_LONG
        context["LOGIN_PAGE_URL"] = settings.LOGIN_PAGE_URL
        context["LOGOUT_PAGE_URL"] = settings.LOGOUT_PAGE_URL

        # This will be populated by the dp_field_value teblate tags.
        # It allows storing which datapoints field exist on the page and
        # can thus be updated automatically.
        context["field_collector"] = {}

        # Load the user specific objects into context
        apps_cache = EmpAppsCache.get_instance()
        nav_content = apps_cache.get_apps_nav_content_for_user(user)
        context["emp_apps_nav_content"] = nav_content

        logger.debug(
            "EMPBaseView loaded for user=%s",
            user
        )

        return context


class EMP403View(EMPBaseView):
    """
    This allows us to still display the nav and title bar, to allow users
    to navigate back to safety more easy.
    """
    template_name = "emp_main/403.html"

    def check_permissions_for_url(self, *args, **kwargs):
        """
        Disable permission checking while delivering 403, as the page has
        already been identified as permission denied. Checking again would
        prevent the delivery of the 403 page.
        """
        pass

def emp_403_handler(*args, **kwargs):
    """
    This is a wrapper around the class based view, as django cannot directly
    call the class based EMP403View.
    """
    emp_403_view = EMP403View.as_view()
    response = emp_403_view(*args, **kwargs)
    # Change the status code as the BaseView returns a 200 response.
    response.status_code = 403
    return response


class DatapointViewSet(DatapointViewSetTemplate):
    # TODO: Verify permissions of user.
    __doc__ = DatapointViewSetTemplate.__doc__
    datapoint_model = Datapoint
    queryset = Datapoint.objects.all()
    serializer_class = DatapointSerializer
    filterset_class = DatapointFilter


class DatapointValueViewSet(DatapointValueViewSetTemplate):
    # TODO: Verify permissions of user.
    # TODO: Create method should push to origin.
    __doc__ = DatapointValue.__doc__.strip()
    model = DatapointValue
    datapoint_model = Datapoint
    queryset = DatapointValue.objects.all()
    # TODO: Set to True after switching from push to pulling the messages.
    create_for_actuators_only = False
    filterset_class = DatapointValueFilter

class DatapointLastValueViewSet(DatapointValueViewSetTemplate):
    # TODO: Verify permissions of user.
    # TODO: Create method should push to origin.
    __doc__ = DatapointValue.__doc__.strip()
    model = DatapointValue
    datapoint_model = Datapoint
    queryset = DatapointValue.objects.all()
    # TODO: Set to True after switching from push to pulling the messages.
    create_for_actuators_only = False
    filterset_class = DatapointValueFilter

    def retrieve(self, request, dp_id):
        datapoint = get_object_or_404(self.datapoint_model, id=dp_id)
        object = self.queryset.filter(datapoint=datapoint).last()
        serializer = self.serializer_class(object)
        return Response(serializer.data)

class DatapointScheduleViewSet(DatapointScheduleViewSetTemplate):
    # TODO: Verify permissions of user.
    # TODO: Create method should push to origin.
    __doc__ = DatapointSchedule.__doc__.strip()
    model = DatapointSchedule
    datapoint_model = Datapoint
    queryset = DatapointSchedule.objects.all()
    # TODO: Set to True after switching from push to pulling the messages.
    create_for_actuators_only = False


class DatapointSetpointViewSet(DatapointSetpointViewSetTemplate):
    # TODO: Verify permissions of user.
    # TODO: Create method should push to origin.
    __doc__ = DatapointSetpoint.__doc__.strip()
    model = DatapointSetpoint
    datapoint_model = Datapoint
    queryset = DatapointSetpoint.objects.all()
    # TODO: Set to True after switching from push to pulling the messages.
    create_for_actuators_only = False
