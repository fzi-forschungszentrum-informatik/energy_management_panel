from django.db import models

from .apps import app_url_prefix

class EvaluationSystemPage(models.Model):

    """
    Basic model for evaluation systems web pages. This pages will be configured in djangos admin panel.
    Use the UIElementContainers to provide a structure on the page.
    Use this model to create overview and dashboard pages.
    Beside these pages there are special preconfigured pages, that are (semi-)hard coded (e.g.: Login page, system log page...)
    """

    page_name = models.CharField(
        max_length = 18,
        help_text = (
            "The name of the page as displayed in the nav bar. Should not "
            "exceed 18 chars, as the string will be wider then the available "
            "space in the navbar."
        )
    )
    
    page_slug = models.SlugField(
        unique=True,
        help_text = (
            "The name of the page used in the URL of it. Must be unique "
            "as two pages of this app cannot have the same url."
        )
    ) 

    has_report_generation = models.BooleanField(
        default = False,
        help_text = (
            "If checked the 'create report' button in the top right corner of the page will be visible"
            "providing the possibility to generate a report out of pages data."
        )
    )

    def get_absolute_url(self):
        url = "/" + app_url_prefix + "/" + self.page_slug + "/"
        return url



class UIElementContainer(models.Model):

    """
    Container used to model and structure the UI.
    Consists of one to many UIElements that are rendered inside a bootstrap card as container.
    Use different containers to present different data.
    Containers may have a dropdown to provide extra functionality.
    """

    container_name = models.CharField(
        max_lenght = 64,
        help_text = (
            "The name of the container as displayed in cross references"
            "Max length is 64 characters due to comprehensibility of the name."
        )
    )

    container_slug = models.SlugField(
        unique = True,
        help_text = (
            "The name of the container used to cross reference it in pages. Must be unique."
        )
    )

    container_has_Title = models.BooleanField(
        default = False,
        help_text = (
            "If checked the containers title will be visible in its header."
            "Use short and describing titles to guide the user."
        )
    )

    container_title = models.CharField(
        max_length = 64,
        help_text = (
            "The containers title as displaied in the containers header."
            "Only visible if 'has_title' is checked."
        )
    )

    container_has_dropdown = models.BooleanField(
        default = False,
        help_text = ( 
            "If checked the referenced dropdown linkes will be shown as a dropdown menu in the top right corner of the containers header."
            "Use the dropdown menu to provide less important functionality in relation to containers data."
        )
    )

    #TODO Implement dropdown links choise

class UIElement(models.Model):
    """
    UIElements models are used to map data to a data presentation.
    UIElements may be in- or outside a UIElementContainer.
    """
    element_name = models.CharField(
        max_length = 64,
        help_text = (
            "The UIElements name as displayed in cross references." 
        )
    )

    element_slug = models.SlugField(
        unique = True,
        help_text = (
            "The name of the UI element used to cross reference it in containers or pages. Must be unique."
        )
    )

class Presentation(models.Model):
    pass

class Card(Presentation):

    CARD_COLOR_CHOICES = [
        ("primary", "primary"),
        ("secondary", "warning"),
        ("success", "success"),
        ("warning", "warning"),
        ("danger", "danger"),       
    ]

    card_color = models.CharField(
        max_length= 10,
        choices = CARD_COLOR_CHOICES,
        default = CARD_COLOR_CHOICES[0][0],
        help_text = (
            "Allows configuring the color scheme of the card."
        )
    )

    CARD_DECORATION_CHOICES = [
        ("none", "none"),
        ("left", "left"),
        ("bottom", "bottom"),     
    ]

    card_decoration = models.CharField(
        max_length = 6,
        choices = CARD_DECORATION_CHOICES,
        default = CARD_DECORATION_CHOICES[0][0],
        help_text = (
            "Allows configuring the decoration of the card."
        )
    )

    card_is_button = models.BooleanField(
        default = False,
        help_text = (
            "If checkt the card can be used as button using the referenced link."
            "With hover effects the card is made recognizable as button."
            "Use cards as button to link additional information pages or function."
        )
    )

    #TODO implement card button link choise

    card_has_tooltip = models.BooleanField(
        default = False,
        help_text = (
            "If checkt the card shows a tooltip providing your custom tooltip text."
            "Use the tooltips to provide additional information."
        )
    )

    card_tooltip_text = models.TextField(
        help_text = (
            "Provide the cards tooltip text here."
            "It can have any length but have in mind noone likes reading massive tooltips."
        )
    )


class Chart(Presentation):

    chart_show_title = models.BooleanField(
        default = False,
        help_text = (
            "If checked the chart will show a customizable title in its header."
        )
    )

    chart_title = models.CharField(
        max_length = 64,
        help_text = (
            "Provide a short and describing chart title here."
        )
    )

    CHART_TYPE_CHOICES = [
        ("area", "area"),
        ("bar", "bar"),
        ("donut", "donut"), 
        #TODO add spider chart    
    ]

    chart_type = models.CharField(
        max_length = 6,
        choices = CHART_TYPE_CHOICES,
        default = CHART_TYPE_CHOICES[0][0],
        help_text = (
            "Allows configuring the chart type."
        )
    )

    #TODO implement color set choce
    #TODO implement data set picker

class Image(models.Model):
    pass
    #TODO Think about a image picker posibility for fa icons