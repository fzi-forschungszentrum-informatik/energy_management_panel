"""
Template tags that support the handling of datapoints in pages.
"""
import json

from django import template
from django.utils.html import format_html, escapejs

register = template.Library()

@register.simple_tag
def dp_field_value(datapoint, field_name, field_collector=None):
    """
    Returns a field value of a datapoint incl. an class label that allows
    dynamic updateing of the value via websocket.
    """
    if not hasattr(datapoint, field_name):
        field_value = "Error! Datapoint has no field name \"%s\"" % field_name
    else:
        field_value = getattr(datapoint, field_name)
       
    if (field_name == "last_value") and (getattr(datapoint, "data_format") == "discrete_numeric"):
            field_value = bool(field_value)

    if not hasattr(datapoint, "id"):
        emsg = "Datapoint %s has no id." % datapoint
        raise ValueError(emsg)

    class_label = 'dp%s__%s' % (datapoint.id, field_name)
    field_html = format_html(
        "<span class={}>{}</span>",
        class_label,
        field_value
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
