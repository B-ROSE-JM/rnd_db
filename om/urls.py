from django.urls import path
from . import views

app_name = 'om'

urlpatterns = [
    path('', views.om_list, name='list'),
    path('add/', views.om_add, name='add'),
    path('<int:pk>/edit/', views.om_edit, name='edit'),
    path('batch-import/', views.om_batch_import, name='batch_import'),
    path('batch-delete/', views.om_batch_delete, name='batch_delete'),
]
