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

        # This is a detail object for demo_datapoint, that is used to configure
        # the default detail_with_tabs template.
        if page_object.page_has_detail:
            class Detail():
                pass
            detail = Detail()
            # This must be a unique id, is used to wire up buttons and modal.
            detail.html_id = "dp_{}_detail".format(
                page_object.demo_datapoint.id
            )

            # The demo_detail.html template uses this attribute as title:
            detail.title = "A demo detail"

            # Activate the tabs with custom information and metadata details
            # about the datapoints.
            detail.has_custom_tab = True
            detail.has_datapoint_tab = True
            detail.datapoints_for_tab = [page_object.demo_datapoint]
            context["detail"] = detail

        return context
