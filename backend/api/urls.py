"""
URL configuration for the API app.
"""
from django.urls import path
from .views import GenerateTrainingPlanView, ExtractInBodyDataView, health_check, api_info

urlpatterns = [
    path('', api_info, name='api-info'),
    path('health/', health_check, name='health-check'),
    path('generate/', GenerateTrainingPlanView.as_view(), name='generate-training-plan'),
    path('extract-inbody/', ExtractInBodyDataView.as_view(), name='extract-inbody'),
]
