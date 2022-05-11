"""emp_main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from importlib import import_module

from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.views.generic import RedirectView

from .views import EMPBaseView
from .api import api

ROOT_PATH = settings.ROOT_PATH

# This is the root for all API endpoints. This information is used
# here and there, especially in consumers.py and tests.
API_ROOT_PATH = "api/"


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "", RedirectView.as_view(url=settings.HOME_PAGE_URL, permanent=False),
    ),
    path(
        "welcome/",
        EMPBaseView.as_view(template_name="./emp_main/welcome.html"),
        name="emp_main.welcome",
    ),
    # These are the URLS for REST API.
    # path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(API_ROOT_PATH, api.urls),
]

# Add url paths for the emp apps.
for emp_app in settings.EMP_APPS:
    # Compute the path for the urls of the module, but only if the
    # app_url_prefix has been defined.
    app_config = import_module(emp_app + ".apps")
    if not hasattr(app_config, "app_url_prefix"):
        continue
    if not app_config.app_url_prefix:
        continue
    # Add a trailing slash if it isn't existing yet.
    app_url_prefix = app_config.app_url_prefix
    if app_url_prefix[-1] != "/":
        app_url_prefix += "/"
    # Add urls of the app to urlpatterns.
    app_path = path(app_url_prefix, include(emp_app + ".urls"))
    urlpatterns.append(app_path)

urlpatterns = [path(ROOT_PATH, include(urlpatterns))] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

handler403 = "emp_main.views.emp_403_handler"
