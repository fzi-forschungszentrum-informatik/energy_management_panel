#!/usr/bin/env python3
"""
"""
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class ExternalPageGroup(models.Model):
    """
    Defines a collapsible group in the Navbar.
    """

    name = models.CharField(
        max_length=20,
        help_text=(
            "The name of the group as displayed in the nav bar. Should not "
            "exceed 20 chars, as the string will be wider then the available "
            "space in the navbar."
        ),
    )
    slug = models.SlugField(
        unique=True,
        help_text=(
            "The name of the group used in the URL of it. Must be unique "
            "as two group of this app cannot have the same url."
        ),
    )

    def __str__(self):
        if self.name is not None:
            return str(self.id) + " - " + self.name
        else:
            return str(self.id)


class ExternalPage(models.Model):
    """
    This is one page entry under a group.
    """

    group = models.ForeignKey(ExternalPageGroup, on_delete=models.CASCADE,)
    name = models.CharField(
        max_length=18,
        help_text=(
            "The name of the page as displayed in the nav bar. Should not "
            "exceed 18 chars, as the string will be wider then the available "
            "space in the navbar."
        ),
    )
    slug = models.SlugField(
        unique=True,
        help_text=(
            "The name of the page used in the URL of it. Must be unique "
            "as two pages of this app cannot have the same url."
        ),
    )
    src = models.URLField(
        blank=True,
        null=False,
        max_length=1024,
        help_text=(
            "The URL of the external page that should be loaded in the frame."
        ),
    )
    grafana_dashboard_url = models.CharField(
        blank=True,
        null=False,
        max_length=50,
        help_text=(
            "The relative part of the Grafana dashboard URL. E.g. for "
            "`http://localhost:8000/emp/grafana/d/WcLAqq_nk/"
            "test-dashboard?orgId=1`. it would be:"
            "d/WcLAqq_nk/test-dashboard?orgId=1"
        ),
    )

    def clean(self):
        """
        Check that only `src` or `grafana_dashboard_id` can be set.
        """
        super().clean()
        if self.src and self.grafana_dashboard_url:
            raise ValidationError(
                "Only one of `src` and `grafana_dashboard_url` can be set."
            )
        if not self.src and not self.grafana_dashboard_url:
            raise ValidationError(
                "Either one of `src` and `grafana_dashboard_url` must be set."
            )

    def get_absolute_url(self):
        u = reverse(
            "emp_external_page.external_page",
            kwargs={"group_slug": self.group.slug, "page_slug": self.slug},
        )
        return u
