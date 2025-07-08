from django.urls import path
from . import views
    
app_name = 'calories'

urlpatterns = [
    path('log/', views.DailyLogView.as_view(), name='daily_log'),
    path('log/<int:pk>/delete/', views.DailyLogDeleteView.as_view(), name='daily_log_delete'),
    path('foods/', views.FoodListView.as_view(), name='food_list'),
    path('foods/add/', views.FoodCreateView.as_view(), name='food_add'),
    path('foods/<int:pk>/edit/', views.FoodUpdateView.as_view(), name='food_edit'),
    path('foods/<int:pk>/delete/', views.FoodDeleteView.as_view(), name='food_delete'),
]