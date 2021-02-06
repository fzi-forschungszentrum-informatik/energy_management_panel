"""
    Template tags that support building SystemEvaluationPages.
"""

from django import template
from django.utils import timezone
import logging



register = template.Library()
@register.filter
def datetime_as_timestamp(date):
    """
        Returns the datetimes timestamp
    """
    return date.timestamp()

@register.filter
def now_as_timestamp():
    """
        Returns the datetimes timestamp
    """
    return timezone.now().timestamp()