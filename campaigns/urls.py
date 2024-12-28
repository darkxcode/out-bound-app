from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Add your home view
    # Add other URL patterns as needed
] 