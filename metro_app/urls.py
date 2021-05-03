from django.urls import path
from .views import *
from .networks import *


urlpatterns=[
    path('', index, name ='home'),
    path('upload_node/', upload_node, name='upload_node'),
    path('upload_edge/', upload_edge, name='upload_edge'),
    path('project/', create_project, name='create_project'),
    path('roadnetwork/', create_roadnetwork, name='create_roadnetwork'),
    path('roadtype/', create_roadtype, name='create_roadtype'),
    path('visualization/', network_visualization, name='network_visualization'),
    path('task/', test_async_view, name='test_async_view'),
    path('task/<slug:task_id>/', test_task_status, name='test_task_status'),
]
