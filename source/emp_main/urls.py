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
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.views.generic import RedirectView

from .views import EMPBaseView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", RedirectView.as_view(url=settings.HOME_PAGE_URL, permanent=False)),
    path("welcome/", EMPBaseView.as_view(template_name="./emp_main/welcome.html")),
    # TODO: Find some configurable default here.
    path("demo/", include('emp_demo_ui_app.urls'))
]

handler403 = 'emp_main.views.emp_403_handler'
