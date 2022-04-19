import logging
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in

from .apps import EmpAppsCache

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def update_user_permissions(sender, **kwargs):
    """
    Update the content of EMPUIAppsCache for the user logging in.

    This allows updated user specific permissions, like per object level
    permissions of pages to take effect. Also update the AnonymousUser,
    as an update for this users permissions can never be triggered by an
    login, and some user permissions may be computed additionally to those
    of the AnonymousUser.

    Updating on Login is expected to be much more efficient then updateing
    after every change even if the user isn't active or to compute the full
    set of permissions for every page call.
    """
    user = kwargs["user"]
    logger.debug("Signal update_user_permissions called for user %s", user)

    anon = get_user_model().get_anonymous()

    apps_cache = EmpAppsCache.get_instance()
    apps_cache.update_for_user(user=anon)
    apps_cache.update_for_user(user=user)