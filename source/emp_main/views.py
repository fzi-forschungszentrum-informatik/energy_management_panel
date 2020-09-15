from collections import OrderedDict

from django.conf import settings
from django.utils.text import slugify
from django.views.generic import TemplateView
from django.templatetags.static import static

from emp_main.apps import EmpUiAppsCache

class EMPBaseView(TemplateView):
    """
    Like the normal TemplateView but automatically extends the context with
    all data required for all pages, that is, for the base.html template.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["PAGE_TITLE"] = settings.PAGE_TITLE
        context["MANIFEST_JSON_STATIC"] = static(settings.MANIFEST_JSON_STATIC)
        context["FAVICON_ICO_STATIC"] = static(settings.FAVICON_ICO_STATIC)
        context["TOPBAR_LOGO_STATIC"] = static(settings.TOPBAR_LOGO_STATIC)
        context["TOPBAR_NAME_SHORT"] = settings.TOPBAR_NAME_SHORT
        context["TOPBAR_NAME_LONG"] = settings.TOPBAR_NAME_LONG

        user = self.request.user
        apps_cache = EmpUiAppsCache.get_instance()
        nav_content = apps_cache.get_apps_nav_content_for_user(user)
        context["emp_apps_nav_content"] = nav_content

        return context
