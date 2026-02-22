from django.urls import path
from . import views

app_name = 'formulations'

urlpatterns = [
    path('', views.formulation_list, name='list'),
    path('add/', views.formulation_add, name='add'),
    path('<int:pk>/edit/', views.formulation_edit, name='edit'),
]
