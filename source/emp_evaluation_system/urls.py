"""
For the evaluation system it is sufficient to provide all pages with a single view.
The only necessary parameter is thereby the page_slug (e.g. the "dashboard"
in http://localhost:8000/evaluation_system/dashboard/) which is used to retrieve the page
specific content from the DB.
"""
from django.urls import path

from .views import EvaluationSystemPageView

# Since the pages are build generic there is only one page template.
# This template builds a generic page out of admin specified data and multiple other templates.
urlpatterns = [
    path(
        "<slug:page_slug>/",
        EvaluationSystemPageView.as_view(
            template_name="./emp_evaluation_system/evaluationSystemPage.html"
        ),
    ),
]