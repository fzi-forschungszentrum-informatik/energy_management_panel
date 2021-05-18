from django.shortcuts import get_object_or_404

from emp_main.views import EMPBaseView
from .models import Location, Widget

class LocationView(EMPBaseView):
    """
    Fetch all widgets that belong to a page.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        location_slug = self.kwargs["location_slug"]
        location_object = get_object_or_404(
            Location, slug=location_slug
        )

        # Get all widgets for this location
        location_widgets = Widget.objects.filter(location=location_object)
        #location_widgets = Widget.objects.filter(id=1)

        # Add config for the widget_detail pages.
        class Detail():
            pass
        for widget in location_widgets:
            widget.has_detail = False
            widget.detail = Detail()
            widget.detail.html_id = "widget_detail_" + str(widget.id)
            widget.detail.has_custom_tab = True
            widget.detail.has_plot_tab = False
            widget.detail.has_datapoint_tab = True

        context["location_name"] = location_object.name
        context["location_widgets"] = location_widgets

        return context
