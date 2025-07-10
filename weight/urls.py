from django.urls import path
from . import views

app_name = "weight"

urlpatterns = [
    path("", views.WeightTrackerView.as_view(), name="tracker"),
    path("chart-data/", views.ChartDataView.as_view(), name="chart_data"),
    path("<int:pk>/editar/", views.WeightEntryEditView.as_view(), name="entry_edit"),
    path(
        "<int:pk>/excluir/", views.WeightEntryDeleteView.as_view(), name="entry_delete"
    ),
]
