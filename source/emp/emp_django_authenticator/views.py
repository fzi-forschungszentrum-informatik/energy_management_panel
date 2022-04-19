from django.contrib.auth.views import LoginView

from emp_main.views import EMPBaseView
from .forms import AuthenticationForm


class EMPLoginView(LoginView, EMPBaseView):

    template_name = "emp_django_authenticator/login.html"
    form_class = AuthenticationForm
    redirect_authenticated_user = False
