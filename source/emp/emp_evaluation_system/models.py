import os

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from multiselectfield import MultiSelectField


from emp_main import settings
from emp_main.models import Datapoint

from .apps import app_url_prefix

import re, datetime

class EvaluationSystemPage(models.Model):

    """
    Basic model for evaluation systems web pages. This pages will be configured in djangos admin panel.
    Use this model to create overview, dashboard, or comparison pages.
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

    page_is_comparison_page = models.BooleanField(
        default = False,
        help_text = (
            "If this is checked, the page will transform into a optimization comparison page. "
            "Therefore the page consists of two algorithm select boxes and an additional comparison graph. "
            "Also the configured page will be rendered twice. Once for the first, once for the second selected algorithm."
        )
    )

    has_scroll_to_top_button = models.BooleanField(
        default = True,
         help_text = (
            "If checked the 'scroll top' button in the bottom right corner of the page will be visible "
            "providing the possibility scroll to the top of the page with one click."
        )
    )

    description = models.TextField(
        blank = True,
        default = "",
        help_text = (
            "Provide a description for this page to help other admin users to understand its purpose."
        )
    )

    def get_absolute_url(self):
        url = "/" + app_url_prefix + "/" + self.page_slug + "/"
        return url

    def __str__(self):
        if self.page_name is not None:
            return (str(self.id) + " - " + self.page_name)
        else:
            return str(self.id)

class PageElement(models.Model):
    """
    This model can used be in two states: container or presentation.
    If a UIElementContainer is used as container it consists of other UIElements (with arbitrary recursion).
    As UIElement it is used to visualize data.
    """

    ELEMENT_TYPE_CHOISES = [
        ("none","Choose elements type"),
        ("container","Container"),
        ("element", "Element")
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
    Container used to structure the UI.
    Consists of one to many UIElements that are rendered inside a bootstrap card as container.
    Use different containers to present different data.
    Containers may have a dropdown to provide extra functionality.
    """

    container_has_title = models.BooleanField(
        default = False,
        help_text = (
            "If checked the containers title will be visible in its header. "
            "Use short and describing titles to guide the user. "
        )
    )

    container_title = models.CharField(
        max_length = 64,
        help_text = (
            "The containers title as displaied in the containers header. "
            "Only visible if 'has_title' is checked. "
        )
    )

    container_has_dropdown = models.BooleanField(
        default = False,
        help_text = ( 
            "If checked the referenced dropdown linkes will be shown as a dropdown menu in the top right corner of the containers header. "
            "Use the dropdown menu to provide less important functionality in relation to containers data."
        )
    )

    container_dropdown_links = models.ManyToManyField(
        EvaluationSystemPage,
        blank = True,
        help_text = (
            "Choose the pages linked in the dropdown here."
        )
    )

    page_element = models.ForeignKey(
        PageElement,
        default = None,
        on_delete = models.CASCADE,
    )
    

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
        blank=True,
        null=True
    )

    container_element = models.ForeignKey(
        UIElementContainer,
        default = None,
        on_delete = models.CASCADE,
        blank=True,
        null=True
    )

class Metric(models.Model):

    """
        A Metric object represents a formula on one to may Datapoints.
        The formula may be specified as a String. 
        Later on the String will be parsed, the linked datapoint values requested, and a Metric result calculated.
        At the frontend only results will be presented.
    """
    
    name = models.CharField(
        max_length = 128,
        blank = False,
        default = None,
        null = True,
        help_text = (
            "The metric's name. It will appear as data description in the frontend."
        )
    )

    unit = models.CharField(
        max_length = 64,
        blank = False,
        default = "$",
        help_text = (
            "The unit of the metrics result."
        )
    )

    formula = models.CharField(
        max_length = 256,
        blank = False,
        null = True,
        default = None,
        help_text = (
            "Describe the metrics formula as the following: use basic mathematic specail characters like '+', '-', '*', '/', '(' and ')'. "
            "Aslo you may use numbers in integer or floating point format. " 
            "As variable you can link a datapoint using dp_* with * as data point id."
            "The last value of this datapoint will be used as value."
            "Do NOT use whitespaces!"
        )
    )

    description = models.TextField(
        default = None,
        null = True,
        help_text = (
            "Provide a description for other users. This description will only be shwon in admin panel context."
        )
    )
    
    def __str__(self):
        if self.name is not None:
            return (str(self.id) + " - " + self.name)
        else:
            return str(self.id)

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

    use_metric = models.BooleanField(
        default = False,
        blank = False,
        help_text = (
            "Check this if you want to use a Metric object instead of a Datapoint object."
        )
    )

    datapoint = models.ForeignKey(
        Datapoint,
        on_delete = models.SET_NULL,
        default = None,
        blank = True,
        null = True,
        help_text = (
            "Choose the Datapoint represented by this."
        )
    )

    metric = models.ForeignKey(
        Metric,
        on_delete = models.SET_NULL,
        default = None,
        blank = True,
        null = True,
        help_text = (
            "Choose the Metric represented by this."
        )
    )

    

class Card(models.Model):
    """
    The Card model is one of Presentation models types.
    Its a rectangular bootstrap card, containing an image, a data title, presented in monochrome design.
    As additional decoration elements a border on the left or at the bottom are available.
    To add extra information use the tooltips. 
    For additional fuctionality use the card as button.

    Use this presentation type to visualize simple data. 
    """
    CARD_COLOR_CHOICES = [
        ("primary", "primary"),
        ("secondary", "secondary"),
        ("success", "success"),
        ("warning", "warning"),
        ("danger", "danger"),       
    ]

    card_color = models.CharField(
        max_length= 10,
        choices = CARD_COLOR_CHOICES,
        default = CARD_COLOR_CHOICES[0][0],
        help_text = (
            "Allows configuring the color scheme of the card. "
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
            "Allows configuring the decoration of the card. "
        )
    )

    card_is_button = models.BooleanField(
        default = False,
        help_text = (
            "If checkt the card can be used as button using the referenced link. "
            "With hover effects the card is made recognizable as button. "
            "Use cards as button to link additional information pages or function."
        )
    )

    card_button_link = models.ForeignKey(
        EvaluationSystemPage,
        on_delete = models.CASCADE,
        null = True,
        default = None,
        blank = True,
        help_text = (
            "On button click the page set here will be called."
        )
    )

    card_has_tooltip = models.BooleanField(
        default = False,
        help_text = (
            "If checkt the card shows a tooltip providing your custom tooltip text. "
            "Use the tooltips to provide additional information."
        )
    )

    card_tooltip_text = models.TextField(
        blank = True,
        help_text = (
            "Provide the cards tooltip text here. "
            "It can have any length but have in mind noone likes reading massive tooltips."
        )
    )

    presentation = models.ForeignKey(
        Presentation,
        default = None,
        on_delete = models.CASCADE,
    )
    
    CARD_ICON_CHOICES = [
        ("none", "none"),
        ("cog", "cog"),
        ("clock", "clock"),  
        ("dollar-sign", "dollar-sign"),   
        ("sun", "sun"),
        ("bolt", "bolt"),
        ("chart-line", "chart-line"),
        ("battery-full", "battery-full"),
        ("battery-empty", "battery-empty"),
        ("clipboard-list", "clipboard-list"),
        ("tachometer-alt ", " tachometer-alt "),
        ("couch", "couch"),
        ("plug", "plug"),
        ("charging-station", "charging-station"),
        ("server", "server")  ,  
    ]

    card_icon = models.CharField(
        max_length = 64,
        choices = CARD_ICON_CHOICES,
        default = CARD_ICON_CHOICES[0][0],
        help_text = (
            "Allows configuring the icon of the card."
        )
    )


class Chart(models.Model):

    """
    The Chart model is the second type of the presentation model.
    It consists of its own title and one chart representing one or more set of data.
    """
    chart_has_title = models.BooleanField(
        default = False,
        help_text = (
            "If checked the chart will show a customizable title in its header."
        )
    )

    chart_title = models.CharField(
        max_length = 64,
        help_text = (
            "Provide a short and describing chart title here."
        ),
        blank = True
    )

    CHART_TYPE_CHOICES = [
        ("area", "area"),
        ("bar", "bar"), 
    ]

    chart_type = models.CharField(
        max_length = 6,
        choices = CHART_TYPE_CHOICES,
        default = CHART_TYPE_CHOICES[0][0],
        help_text = (
            "Allows configuring the chart type."
        )
    )


    CHART_DATA_SET_CHOISES = (
        ("history", "history"),
        ("forecast", "forecast"),
        ("schedule", "schedule"),
        ("setpoints", "setpoints")
    )

    chart_data_sets = MultiSelectField(
        choices=CHART_DATA_SET_CHOISES,
        max_choices=3,
        max_length=64,
        default = None,
        null = True,
        help_text = (
            "Select one to three of these options to select which data sets will be shown in the chart."
        )
    )

    CHART_DATA_INTERVAL_CHOISES = (
        ("hourly", "hourly"),
        ("daily", "daily"),
        ("weekly", "weekly"),
        ("monthly", "monthly"),
    )

    chart_data_interval = MultiSelectField(
        choices=CHART_DATA_INTERVAL_CHOISES,
        max_choices=5,
        max_length=128,
        default = None,
        null = True,
        help_text = (
            "Select one to five of these options to select which data intervals will be available in the chart."
        )
    )

    presentation = models.ForeignKey(
        Presentation,
        default = None,
        on_delete = models.CASCADE,
    )

class Algorithm(models.Model):

    """
        The Algorithm model represents a building energy management optimization algorithm.
        As a representation this model is only used to define user choises.
        All Algorithm objects created will be shown the users at the comparion page. Users may choose two Algortihms to copmare.
        To compare Algorithms, their data needs to be simulated. Therefore, a backend simulatin process needs to be started.
        The backend_identifier represents the backend algorithm name. The start and end_time represent the time interval of the simulation.
    """

    name = models.CharField(
        max_length = 128,
        blank = False,
        help_text = (
            "The name of the algorithm. Shown in admin page overview and at the frontend algorithm coparison page."
        )
    )

    backend_identifier = models.SlugField(
        max_length = 64,
        blank = False,
        help_text = (
            "The identifier is used to call the simulation API. Therefore, it has to be the exact same as the algorithm identifier at the backend!"
        )
    )

    description = models.TextField(
        blank = True,
        null = True,
        default = None,
        help_text = (
            "Give a description for other users. Will only be shown in admin context."
        )
    )
    
class ComparisonGraph(models.Model):

    """
        This model represents a simulation and algorithm comparison grah.
        These graphs can only be used in EvaluationSystemPages that are comparison pages.
        Every comparison graph is build in at the page end.
        Comparison graphs take data from two simulated algorithms and compare them in a maximum of three predefined matrics or values. 
    """
    CHART_TYPE_CHOICES = [
        ("area", "area"),
        ("bar", "bar"), 
    ]

    type = models.CharField(
        max_length = 6,
        choices = CHART_TYPE_CHOICES,
        default = CHART_TYPE_CHOICES[0][0],
        help_text = (
            "Allows configuring the chart type."
        )
    )

    has_title = models.BooleanField(
        help_text = (
            "If checked the charts title will be shwon."
        )
    )

    chart_title = models.CharField(
        max_length = 64,
        help_text = (
            "Provide a short and describing chart title here."
        ),
        blank = True
    )

    
    page = models.ForeignKey(
        EvaluationSystemPage,
        default = None,
        on_delete = models.CASCADE
    )
    
class ComparisonGraphDataset(models.Model):
    """
        Each comparion graph consists of up to three comarison graph data sets.
        These data sets are defined in this model.
        A data set is either a metric or a datapoint.
    """
  
    use_metric = models.BooleanField(
        default = False,
        blank = False,
        help_text = (
            "Check this if you want to use a Metric object instead of a Datapoint object."
        )
    )

    datapoint = models.ForeignKey(
        Datapoint,
        on_delete = models.SET_NULL,
        default = None,
        blank = True,
        null = True,
        help_text = (
            "Choose the Datapoint represented by this."
        )
    )

    metric = models.ForeignKey(
        Metric,
        on_delete = models.SET_NULL,
        default = None,
        blank = True,
        null = True,
        help_text = (
            "Choose the Metric represented by this."
        )
    )

    comparison_graph = models.ForeignKey(
        ComparisonGraph,
        default = None,
        on_delete = models.CASCADE
    )