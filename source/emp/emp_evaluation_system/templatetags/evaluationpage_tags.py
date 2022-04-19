"""
    Template tags that support building SystemEvaluationPages.
"""

from django import template
from django.utils import timezone

register = template.Library()


@register.simple_tag
def using_metrics(comparison_graph_data_sets):
    """
     Takes an array of ComparisonGraphDataSets.
     Returns an array of boolean values that state if each of the data sets uses a metric or not.
    """
    output = []
    for dataset in comparison_graph_data_sets:
        output.append(bool(dataset.use_metric))
    return output

@register.simple_tag
def get_datapoints_or_formulas(comparison_graph_data_sets):
    """
        Takes an array of ComparisonGraphDataSets.
        These data sets use either a datapoint link or a metric.
        Returns an array of Strings that hold either the linked datapoint's id or the linked matrics formula as String representation. 
    """
    output = []
    for dataset in comparison_graph_data_sets:
        if (dataset.use_metric):
            output.append(dataset.metric.formula)
        else:
            output.append(dataset.datapoint.id)
    return output
