from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import EMPLoginView

urlpatterns = [
    path("login/", EMPLoginView.as_view()),
    path("logout/", LogoutView.as_view()),
]
