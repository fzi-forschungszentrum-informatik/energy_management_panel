from django.db import models


class DemoAppPage(models.Model):
    """
    A simple example for model based pages for an EMP UI app.
    """

    page_name = models.CharField(
        max_length=18,
        help_text=(
            "The name of the page as displayed in the nav bar. Should not "
            "exceed 18 chars, as the string will be wider then the available "
            "space in the navbar."
            )
        )
    page_slug = models.SlugField(
        unique=True,
        help_text=(
            "The name of the page used in the URL of it. Must be unique "
            "as two pages of this app cannot have the same url."
        )
    )
    page_content = models.TextField(
        help_text=(
            "This is an example for some Content of the page that can be "
            "configured dynamically, i.e. by using Django's admin."
        )
    )
    PAGE_BACKGROUD_COLOR_CHOICES = [
        ("transparent", "transparent"),
        ("yellow", "yellow"),
        ("red", "red"),
    ]
    page_background_color = models.CharField(
        max_length=11,
        choices=PAGE_BACKGROUD_COLOR_CHOICES,
        default=PAGE_BACKGROUD_COLOR_CHOICES[0][0],
        help_text=(
            "Allows configuring the background color of the page."
        )
    )
