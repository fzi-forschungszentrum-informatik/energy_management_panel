#!/usr/bin/env python3
"""
"""
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
        max_length=1024,
        help_text=(
            "The URL of the external page that should be loaded in the frame."
        ),
    )

    def get_absolute_url(self):
        u = reverse(
            "emp_external_page.external_page",
            kwargs={"group_slug": self.group.slug, "page_slug": self.slug},
        )
        return u
