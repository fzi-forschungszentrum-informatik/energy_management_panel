#!/usr/bin/env python3
"""
"""

from django.shortcuts import get_object_or_404

from emp_main.views import EMPBaseView
from emp_main.models import ProductRun
from .models import ExternalPage


class ExternalPageView(EMPBaseView):
    """
    A simple example for a view that appends the context with page specific
    data used only by the demo UI app pages.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        group_slug = self.kwargs["group_slug"]
        page_slug = self.kwargs["page_slug"]
        page_obj = get_object_or_404(
            ExternalPage, slug=page_slug, group__slug=group_slug
        )

        context["page"] = page_obj

        # ID of latest product run, a number often required by
        # Grafana dasboards that show the latest state of something.
        if page_obj.product_for_run is not None:
            latest_product_run = ProductRun.objects.filter(
                _product=page_obj.product_for_run
            ).last()
            context["var_productrun"] = str(latest_product_run.id)
        else:
            context["var_productrun"] = ""

        return context
