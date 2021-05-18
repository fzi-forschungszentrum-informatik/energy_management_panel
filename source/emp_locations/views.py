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

        # Add config for the widget_detail pages.
        for widget in location_widgets:
            widget.detail = widget.get_addition_object().get_detail()
            if widget.detail.is_active:
                widget.has_detail = True

        context["location"] = location_object
        context["location_widgets"] = location_widgets

        return context
