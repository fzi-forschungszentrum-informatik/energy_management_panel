import json
from math import log

from django.http import Http404
from django.utils.html import escapejs
from django.shortcuts import get_object_or_404

from emp_main.views import EMPBaseView
from .models import EnergyFlow, Widget, Flow


class EMPEnergyFlowView(EMPBaseView):

    template_name = "holl_emp_energy_flow/energy_flow.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        energyflow_slug = self.kwargs["energyflow_slug"]

        # Load the objects belonging to the requested page (active only)
        energyflow = get_object_or_404(EnergyFlow, slug=energyflow_slug,)
        if not energyflow.is_active:
            raise Http404()
        widgets = Widget.objects.filter(energyflow=energyflow, is_active=True,)
        flows = Flow.objects.filter(
            energyflow=energyflow,
            origin_device__is_active=True,
            target_device__is_active=True,
        )

        # Compute the required number of rows and columns. css
        # grid coordinates are referenced until the grid line before they end.
        # See also: https://www.w3schools.com/css/css_grid_item.asp
        n_cols = max(widgets.values_list("grid_position_right"))[0] - 1
        n_rows = max(widgets.values_list("grid_position_bottom"))[0] - 1

        # Compute the grid areas, normal (wide) layout on large screens
        # and a 90° degree rotated version on small screens.
        def compute_widget_area_id(widget):
            """
            Returns a unique id used within the energy-flow-plot to place the
            widgets in the grid.
            """
            return "widget_area_" + str(widget.id)

        areas_big = [["." for k in range(n_cols)] for j in range(n_rows)]
        areas_small = [["." for k in range(n_rows)] for j in range(n_cols)]
        # areas_small = [["." for k in range(n_rows)] for j in range(n_cols)]
        for widget in widgets:
            widget.area_id = compute_widget_area_id(widget)
            for i in range(
                widget.grid_position_top, widget.grid_position_bottom
            ):
                for j in range(
                    widget.grid_position_left, widget.grid_position_right
                ):
                    areas_big[i - 1][j - 1] = widget.area_id
                    areas_small[j - 1][i - 1] = widget.area_id
        areas_small = "\n".join(
            ['"' + " ".join(row) + '"' for row in areas_small]
        )
        areas_big = "\n".join(['"' + " ".join(row) + '"' for row in areas_big])

        # Prepare the flow objects for the template.
        for flow in flows:
            flow.html_id = "flow_" + str(flow.id)
            flow.origin_area_id = compute_widget_area_id(flow.origin_device)
            flow.target_area_id = compute_widget_area_id(flow.target_device)

            # Compute the direction of the flows based on the grid coordinates.
            # This works only for direct connections in x, y direction.
            # Yields errors for diagonal flows.
            td = flow.target_device
            od = flow.origin_device
            if od.grid_position_bottom > td.grid_position_bottom:
                flow.direction = "up"
            elif od.grid_position_top < td.grid_position_top:
                flow.direction = "down"
            elif od.grid_position_left < td.grid_position_left:
                flow.direction = "right"
            elif od.grid_position_right > td.grid_position_right:
                flow.direction = "left"

            # Also compute initial values for the flow animation.
            flow.moving_stopped = "stopped"
            if hasattr(flow.value_datapoint, "last_value_message"):
                last_value = float(
                    flow.value_datapoint.last_value_message.value
                )
            else:
                last_value = 0

            if last_value != 0:
                flow.moving_stopped = "moving"
            # Quick and dirty implementation of animation_freq in
            # energy_flow.html
            energy = last_value
            if energy < 0.1:
                energy = 1e-10
            flow.time = 1 / min(0.6 * log(1 + energy - 0.05) + 0.05, 4)

        # Store min/max values of the datapoints, these are need to
        # update the progressbar elements.
        min_max_by_datapoint_id = {}
        for widget in widgets:
            for datapoint_attr_name in ["datapoint1", "datapoint2"]:
                if hasattr(widget, datapoint_attr_name):
                    datapoint = getattr(widget, datapoint_attr_name)
                    if datapoint is None:
                        continue
                    min_max_by_datapoint_id[datapoint.id] = [
                        datapoint.min_value,
                        datapoint.max_value,
                    ]

        context["widgets"] = widgets
        context["flows"] = flows
        context["n_rows"] = n_rows
        context["n_columns"] = n_cols
        context["areas_small"] = areas_small
        context["areas_big"] = areas_big
        context["min_max_by_datapoint_id"] = escapejs(
            json.dumps(min_max_by_datapoint_id)
        )
        context["flow_cells"] = range(5)

        return context
