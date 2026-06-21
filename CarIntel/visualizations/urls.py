from django.urls import path
from . import views

app_name = 'visualizations'

urlpatterns = [
    path('charts/', views.charts_dashboard, name='charts_dashboard'),
]
