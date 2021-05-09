from django.urls import path
from .views import *
from .networks import *


urlpatterns=[
    path('', index, name ='home'),
    path('project/', create_project, name ='create_project'),
    path('project/<str:pk>/', project_details, name = 'project_details'),
    path('network/<str:pk>/', create_network, name = 'create_network'),
    path('update_network/<str:pk>/', update_network, name = 'update_network'),
    path('delete_network/<str:pk>/', delete_network, name = 'delete_network'),
    path('network/<str:pk>/roadtype/', create_roadtype, name = 'roadtype'),
    path('network/<str:pk>/details/', network_details, name = 'network_details'),
    path('network/<str:pk>/upload_node/', upload_node, name ='upload_node'),
    path('network/<str:pk>/upload_edge/', upload_edge, name ='upload_edge'),
    path('visualization/<str:pk>/', read_from_postgres, name='network_visualization'),
]
