from django.db import models

from django.contrib.contenttypes.fields import GenericForeignKey

from .apps import app_url_prefix
from django.contrib.contenttypes.models import ContentType



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

class PageElement(models.Model):

    """
    This class can be in two states: container or presentation.
    If a UIElement is used as container it consists of other UIElements (with arbitrary recursion).
    As presentation it is used to visualize data.s
    """

    ELEMENT_TYPE_CHOISES = [
        ("container","container"),
        ("element", "element")
    ]

    element_type = models.CharField(
        max_length = 9,
        choices = ELEMENT_TYPE_CHOISES,
        default = ELEMENT_TYPE_CHOISES[0][0],
        help_text = (
            "Choose the element type."
        )
    )

    page = models.ForeignKey(
        EvaluationSystemPage,
        default = None,
        on_delete = models.CASCADE
    )

class UIElementContainer(models.Model):

    """
    Container used to model and structure the UI.
    Consists of one to many UIElements that are rendered inside a bootstrap card as container.
    Use different containers to present different data.
    Containers may have a dropdown to provide extra functionality.
    """

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

    page_element = models.ForeignKey(
        PageElement,
        default = None,
        on_delete = models.CASCADE
    )
    
    #TODO Implement dropdown links choise

class UIElement(models.Model):

    """
    UIElement model represents a ui element on a page. 
    It consists of data that will be visualized with the help of a presentation object.
    UIElements can be grouped in UIElementContainers or added alone to a page.
    """
    page_element = models.ForeignKey(
        PageElement,
        default = None,
        on_delete = models.CASCADE,
    )

    container_element = models.ForeignKey(
        UIElementContainer,
        default = None,
        on_delete = models.CASCADE,
    )


class Presentation(models.Model):

    """
    The Presentation model is used to link a presentation type (card, chart...) to a UIElement.
    UIElements data will be visualized with Presentations help.
    """
    
    PRESENTATION_TYPE_CHOISES = [
        ("card","card"),
        ("chart", "chart")
    ]

    presentation_type = models.CharField(
        max_length = 5,
        choices = PRESENTATION_TYPE_CHOISES,
        default = PRESENTATION_TYPE_CHOISES[0][0],
        help_text = (
            "Choose the presentation type."
        )
    )

    ui_element = models.ForeignKey(
        UIElement,
        default = None,
        on_delete = models.CASCADE,
    )

class Card(models.Model):
    """
    The Card model is one of Presentation models types.
    Its a rectangular card, containing an image, a data title, presented in  monochrome design.
    As additional design elements a border on the left or at the bottom are available.
    To add extra information use the tooltips. For additional fuctionality use the card as button.

    Use this presentation type to visualize simple data. 
    """
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

    presentation = models.ForeignKey(
        Presentation,
        default = None,
        on_delete = models.CASCADE,
    )


class Chart(models.Model):

    """
    The Chart model is the second type of the presentation model.
    It consists of its own title and one chart representing one or more set of data.
    """
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

    presentation = models.ForeignKey(
        Presentation,
        default = None,
        on_delete = models.CASCADE,
    )


class Image(models.Model):
    pass
    #TODO Think about a image picker posibility for fa icons