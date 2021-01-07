from django.shortcuts import get_object_or_404

from emp_main.views import EMPBaseView
from .models import EvaluationSystemPage

class EvaluationSystemPageView(EMPBaseView):
    """
    A simple example for a view that appends the context with page specific
    data used only by the demo UI app pages.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_slug = self.kwargs["page_slug"]
        page_object = get_object_or_404(EvaluationSystemPage, page_slug=page_slug)

        context["page_name"] = page_object.page_name
        context["has_report_generation"] = page_object.has_report_generation
        context["pagelements"] = page_object.pageelement_set.all
        
        context["test"] = "test"
    


        

        return context
