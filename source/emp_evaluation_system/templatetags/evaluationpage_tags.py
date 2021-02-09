"""
    Template tags that support building SystemEvaluationPages.
"""

from django import template
from django.utils import timezone

register = template.Library()

@register.simple_tag
def using_metrics(comparison_graph_data_sets):
    output = []
    for dataset in comparison_graph_data_sets:
        output.append(bool(dataset.use_metric))
    return output

@register.simple_tag
def get_datapoints_or_formulas(comparison_graph_data_sets):
    output = []
    for dataset in comparison_graph_data_sets:
        if (dataset.use_metric):
            output.append(dataset.metric.formula)
        else:
            output.append(dataset.datapoint.id)
    return output
