import logging

from django import forms
from django.contrib.auth import authenticate

logger = logging.getLogger(__name__)


class AuthenticationForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(strip=False, widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username is not None and password:
            self.user = authenticate(self.request, username=username, password=password)
        if self.user is None:
            logger.debug("Authentication failed for username=%s", username)
            raise forms.ValidationError("Invalid email/password combination.")
        logger.debug("Authentication successful for username=%s", username)
        return self.cleaned_data

    def get_user(self):
        return self.user
