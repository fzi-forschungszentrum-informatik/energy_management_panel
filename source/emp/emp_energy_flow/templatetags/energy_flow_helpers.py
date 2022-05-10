from django import template

from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def compute_progressbar_fill(datapoint, datapoint_progressbar_reverse):
    """
    Computes the progress bar fill e.g. as 90% based on min and max values.
    """
    if hasattr(datapoint, "last_value_message"):
        last_value = float(datapoint.last_value_message.value)
    else:
        last_value = 0
    min_value = datapoint.min_value
    max_value = datapoint.max_value
    filled = (last_value - min_value) / (max_value - min_value)
    if datapoint_progressbar_reverse:
        filled = 1 - filled
    filled_percent = round(filled * 100)
    filled_formated = format_html("{}%", str(filled_percent))
    return filled_formated
