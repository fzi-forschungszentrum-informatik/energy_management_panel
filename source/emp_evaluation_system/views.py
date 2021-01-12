from django.shortcuts import get_object_or_404

from emp_main.views import EMPBaseView
from emp_main.settings import EMP_EVALUATION_PAGE_UPDATE_INTERVAL
from .models import EvaluationSystemPage
class EvaluationSystemPageView(EMPBaseView):
    """
    View for EvaluationSystemPages.
    Setting up the context.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_slug = self.kwargs["page_slug"]
        page_object = get_object_or_404(EvaluationSystemPage, page_slug=page_slug)

        context["page_name"] = page_object.page_name
        context["has_report_generation"] = page_object.has_report_generation
        context["pagelements"] = page_object.pageelement_set.all
        context["has_scroll_to_top_button"] = page_object.has_scroll_to_top_button      
        context["update_interval"] = EMP_EVALUATION_PAGE_UPDATE_INTERVAL


        return context