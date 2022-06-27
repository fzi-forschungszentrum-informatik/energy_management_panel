"""
Template tags that support the handling of datapoints in pages.
"""
import json

from django import template
from django.utils.html import format_html, escapejs

register = template.Library()


@register.simple_tag
def dp_field_value(
    datapoint, field_name, field_collector=None,
):
    """
    Returns a field value of a datapoint incl. an class label that allows
    dynamic updateing of the value via websocket.
    """
    # Allows to fetch values from a nested model too.
    field_name_parts = field_name.split(".")
    field_name_this_model = field_name_parts[0]
    related_field_name = ".".join(field_name_parts[1:])

    if not hasattr(datapoint, field_name_this_model):
        field_value = (
            'Error! Datapoint has no field name "%s"' % field_name_this_model
        )
    elif related_field_name:
        field_value = getattr(
            getattr(datapoint, field_name_this_model), related_field_name
        )
    else:
        field_value = getattr(datapoint, field_name_this_model)

    # For any usual number this limits the number to 9 characters.
    # E.g. '-1.23e+07'
    if isinstance(field_value, float):
        if field_value >= 10000.0 or field_value <= -10000.0:
            field_value = "{:.2e}".format(field_value)
        else:
            field_value = "{:.2f}".format(field_value)

    if not hasattr(datapoint, "id"):
        emsg = "Datapoint %s has no id." % datapoint
        raise ValueError(emsg)

    class_label = "dp%s__%s" % (datapoint.id, field_name)
    field_html = format_html(
        "<span class={}>{}</span>", class_label, field_value
    )

    if field_collector is not None:
        if datapoint.id not in field_collector:
            field_collector[datapoint.id] = set()
        field_collector[datapoint.id].add(class_label)

    return field_html


@register.simple_tag
def dp_update_map(field_collector, escape_to_js=True):
    """
    Computes a mapping from datapoint ids to field class_labels as JSON.
    """
    # Transform sets to lists as sets are not transformable to JSON.
    for dp_id in field_collector:
        field_collector[dp_id] = list(field_collector[dp_id])

    update_map = json.dumps(field_collector)
    if escape_to_js:
        update_map = escapejs(update_map)

    return update_map
