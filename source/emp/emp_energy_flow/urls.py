from django.urls import path, include

from .views import EMPEnergyFlowView

urlpatterns = [
    path(
        "<slug:energyflow_slug>/",
        EMPEnergyFlowView.as_view(),
    )
]
