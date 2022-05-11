from django.urls import path

from .views import EMPEnergyFlowView

urlpatterns = [
    path(
        "<slug:energyflow_slug>/",
        EMPEnergyFlowView.as_view(),
        name="emp_energy_flow.emp_energy_flow",
    )
]
