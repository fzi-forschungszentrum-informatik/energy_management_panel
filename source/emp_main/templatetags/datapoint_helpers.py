"""
Template tags that support the handling of datapoints in pages.
"""
from django import template

register = template.Library()

@register.simple_tag
def dp_field_value(datapoint, field_name):
    """
    Returns a field value of a datapoint incl. an class label that allows
    dynamic updateing of the value via websocket.
    """
    if not hasattr(datapoint, field_name):
        field_value = "Error! Datapoint has no field name \"%s\"" % field_name
    else:
        field_value = getattr(datapoint, field_name)

    if not hasattr(datapoint, "id"):
        emsg = "Datapoint %s has no id." % datapoint
        raise ValueError(emsg)

    class_label = '"dp%s__%s"' % (datapoint.id, field_name)
    field_html = "<span class=%s>%s</span>" % (class_label, field_value)
    return field_html