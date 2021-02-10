from django.shortcuts import get_object_or_404

from emp_main.views import EMPBaseView
from emp_main.settings import EMP_EVALUATION_PAGE_UPDATE_INTERVAL
from .models import EvaluationSystemPage, Algorithm
class EvaluationSystemPageView(EMPBaseView):
    """
    View for EvaluationSystemPages.
    Setting up the context.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_slug = self.kwargs["page_slug"]
        page_object = get_object_or_404(EvaluationSystemPage, page_slug=page_slug)

        # Put important page date into context here
        context["page_name"] = page_object.page_name
        context["is_comparison_page"] = page_object.page_is_comparison_page
        context["pagelements"] = page_object.pageelement_set.all
        context["has_scroll_to_top_button"] = page_object.has_scroll_to_top_button      
        context["update_interval"] = EMP_EVALUATION_PAGE_UPDATE_INTERVAL

        # If the page object is used as a comparison page, all Algorithm objects will be put into context.
        # They can be choosen in comparison pages dropdowns at the top of the paqge.
        if page_object.page_is_comparison_page:
            context["algorithms"] = Algorithm.objects.all()
            context["comparison_graphs"] = page_object.comparisongraph_set.all

        return context