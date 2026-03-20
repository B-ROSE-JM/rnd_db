from django.urls import path
from . import views

app_name = 'mm'

urlpatterns = [
    path('', views.mm_list, name='list'),
    path('add/', views.mm_add, name='add'),
    path('<int:pk>/edit/', views.mm_edit, name='edit'),
    path('batch-import/', views.mm_batch_import, name='batch_import'),
    path('batch-delete/', views.mm_batch_delete, name='batch_delete'),
]
