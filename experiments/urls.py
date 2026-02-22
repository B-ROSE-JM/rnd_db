from django.urls import path
from . import views

app_name = 'experiments'

urlpatterns = [
    path('', views.experiment_list, name='list'),
    path('add/', views.experiment_add, name='add'),
    path('compare/', views.experiment_compare, name='compare'),
    path('<int:pk>/edit/', views.experiment_edit, name='edit'),
    path('<int:pk>/delete/', views.experiment_delete, name='delete'),
]
