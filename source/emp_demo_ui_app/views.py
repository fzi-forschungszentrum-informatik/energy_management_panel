from django.shortcuts import get_object_or_404

from emp_main.views import EMPBaseView
from .models import DemoAppPage

class DemoUIPageView(EMPBaseView):
    """
    A simple example for a view that appends the context with page specific
    data used only by the demo UI app pages.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_slug = self.kwargs["page_slug"]
        page_object = get_object_or_404(DemoAppPage, page_slug=page_slug)

        context["page_background_color"] = page_object.page_background_color
        context["page_content"] = page_object.page_content
        context["demo_datapoint"] = page_object.demo_datapoint

        return context
