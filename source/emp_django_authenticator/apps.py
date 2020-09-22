from django.apps import AppConfig


class EmpDjangoAuthenticatorConfig(AppConfig):
    name = 'emp_django_authenticator'

# The first part of the url, that is used to identify the pages
# belongig to this app. No leading or trailing slashes, they will
# be added where needed by the functions using this string.
app_url_prefix = "auth"

"""
All users must have access to login/logout pages. However, these pages are
special because they have a dedicated spot in the navbar. It is hence not
necessary to provide a get_app_nav_content_for_user function. However,
the corresponding URLs must be whitelisted in
settings.URLS_PERMISSION_WHITELIST
"""
#def get_app_nav_content_for_user(user):
#    pass