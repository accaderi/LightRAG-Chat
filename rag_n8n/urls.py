from django.urls import path
from . import views

urlpatterns = [
    path('api/process/', views.process_data, name='process_data'),
    path('', views.home, name='home')
]
