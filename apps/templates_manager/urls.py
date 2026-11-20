from django.urls import path
from . import views

urlpatterns = [
    path('templates/', views.templates_list_view, name='templates'),
]
