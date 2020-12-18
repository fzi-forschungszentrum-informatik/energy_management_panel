from django.urls import include, path
from rest_framework import routers
from rest_framework.schemas import get_schema_view
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .views import DatapointViewSet, DatapointValueViewSet

router = routers.DefaultRouter()
# We do this so the root page gets polulated.
router.register(r'datapoint', DatapointViewSet, basename="datapoint")
selected_urls = []
for url in router.urls:
    if "datapoint/(?P" in url.pattern.describe():
        continue
    selected_urls.append(url)

urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema")),
    path(
        "datapoint/<int:dp_id>/",
        DatapointViewSet.as_view({
            "get": "retrieve",
        })
    ),
    path(
        "datapoint/<int:dp_id>/value/",
        DatapointValueViewSet.as_view({
            "get": "list",
            "post": "create",
        })
    ),
    path(
        "datapoint/<int:dp_id>/value/<int:timestamp>/",
        DatapointValueViewSet.as_view({
            "get": "retrieve",
            "put": "update",
            "delete": "destroy",
        })
    ),

    path("", include(selected_urls))  # Add API root view.
]
print(router.urls)
