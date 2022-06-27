from django.db import models
from django.urls import reverse

from emp_main.models import Datapoint

COLOR_CHOICES = [
    ("elec", "Electricity"),
    ("heat", "Heat"),
    ("cold", "Cold"),
    ("ngas", "Natural Gas"),
]


class EnergyFlow(models.Model):
    """
    One EnergyFlow corresponds to one page in the EMP.
    """

    name = models.CharField(
        max_length=18,
        help_text=(
            "The name of the Energy Flow, will be displayed in the Nav menu."
        ),
    )
    slug = models.SlugField(
        unique=True,
        help_text=(
            "The name of the energy flow page used in the URL of it. Must be "
            "unique as two pages of this app cannot have the same url."
        ),
    )
    is_active = models.BooleanField(
        default=True, help_text=("Will not display Energy Flow if False.")
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        u = reverse(
            "emp_energy_flow.emp_energy_flow",
            kwargs={"energyflow_slug": self.slug},
        )
        return u


class Widget(models.Model):

    energyflow = models.ForeignKey(
        EnergyFlow,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text=(
            "The EnergyFlow page the widget belongs to. Not displayed if null."
        ),
    )

    name = models.CharField(
        max_length=100,
        help_text=(
            "The Name of the Widget displayed in the header of the card. "
        ),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=("Will not display widget and corresponding flows if False."),
    )
    icon_url = models.CharField(
        max_length=200,
        help_text=(
            "The (relative) URL of the the icon to display for the card. "
        ),
    )
    grid_position_left = models.PositiveIntegerField(
        help_text=(
            "The left coordinate of the card in the grid (grid-row-start)"
        ),
    )
    grid_position_right = models.PositiveIntegerField(
        help_text=(
            "The right coordinate of the card in the grid (grid-row-end)"
        ),
    )
    grid_position_top = models.PositiveIntegerField(
        help_text=(
            "The top position of the card in the grid (grid-column-start)"
        ),
    )
    grid_position_bottom = models.PositiveIntegerField(
        help_text=(
            "The bottom position of the card in the grid (grid-column-end)"
        ),
    )
    datapoint1 = models.ForeignKey(
        Datapoint,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="datapoint1",
        help_text=(
            "The first datapoint corresponding to the value that is displayed "
            "in the Energy Flow Page."
        ),
    )
    datapoint1_label = models.CharField(
        max_length=50,
        default="",
        blank=True,
        help_text=(
            "The label that is displayed in the Energy Flow Page to "
            "describe the first datapoint."
        ),
    )
    datapoint1_color = models.CharField(
        max_length=4,
        default="heat",
        choices=COLOR_CHOICES,
        help_text=(
            "The color schema used to display the value of the first datapoint "
            "in the progress bar."
        ),
    )
    datapoint1_show_progressbar = models.BooleanField(
        default=True,
        help_text=("Will not display the progressbar for datapoint if False."),
    )
    datapoint1_progressbar_reverse = models.BooleanField(
        default=False,
        help_text=(
            "Will display the progressbar load reversed if True. This is e.g. "
            "usefull for a cold storage, that is full when close to min_value."
        ),
    )
    datapoint2 = models.ForeignKey(
        Datapoint,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="datapoint2",
        help_text=(
            "The second datapoint corresponding to the value that is displayed "
            "in the Energy Flow Page."
        ),
    )
    datapoint2_label = models.CharField(
        max_length=50,
        default="",
        blank=True,
        help_text=(
            "The label that is displayed in the Energy Flow Page to "
            "describe the second datapoint."
        ),
    )
    datapoint2_color = models.CharField(
        max_length=4,
        default="heat",
        choices=COLOR_CHOICES,
        help_text=(
            "The color schema used to display the value in the progress bar."
        ),
    )
    datapoint2_show_progressbar = models.BooleanField(
        default=True,
        help_text=("Will not display the progressbar for datapoint if False."),
    )
    datapoint2_progressbar_reverse = models.BooleanField(
        default=False,
        help_text=(
            "Will display the progressbar load reversed if True. This is e.g. "
            "usefull for a cold storage, that is full when close to min_value."
        ),
    )

    def __str__(self):
        return self.name


class Flow(models.Model):

    energyflow = models.ForeignKey(
        EnergyFlow,
        on_delete=models.CASCADE,
        null=True,
        help_text=(
            "The EnergyFlow page the Flow belongs to. Not displayed if null."
        ),
    )

    flow_color = models.CharField(
        max_length=4,
        choices=COLOR_CHOICES,
        default="heat",
        help_text=("The color schema used for the flow."),
    )

    origin_device = models.ForeignKey(
        Widget,
        on_delete=models.CASCADE,
        related_name="origin_widget",
        help_text=("The widget the energy flow starts (for a positive sign)."),
    )

    target_device = models.ForeignKey(
        Widget,
        on_delete=models.CASCADE,
        related_name="target_widget",
        help_text=("The widget the energy flow ends (for a positive sign)."),
    )

    value_datapoint = models.ForeignKey(
        Datapoint,
        null=True,
        default=None,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=(
            "The datapoint which value is used to compute the movement speed."
        ),
    )
