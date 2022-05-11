from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import EMPLoginView

urlpatterns = [
    path(
        "login/", EMPLoginView.as_view(), name="emp_django_authenticator.login"
    ),
    path(
        "logout/", LogoutView.as_view(), name="emp_django_authenticator.logout"
    ),
]
