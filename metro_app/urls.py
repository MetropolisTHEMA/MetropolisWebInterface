from django.urls import path
from .views import (create_project, create_network, create_roadtype,
                    project_details, update_network, update_project,
                    delete_project, network_details, index,
                    delete_network, visualization)

from .networks import (upload_edge, upload_node, upload_road, upload_csv)

urlpatterns = [
    path('', index, name='home'),
    path('project/', create_project, name='create_project'),
    path('project/<str:pk>/', project_details, name='project_details'),
    path('update_project/<str:pk>/', update_project, name='update_project'),
    path('delete_project/<str:pk>/', delete_project, name='delete_project'),
    path('network/<str:pk>/', create_network, name='create_network'),
    path('update_network/<str:pk>/', update_network, name='update_network'),
    path('delete_network/<str:pk>/', delete_network, name='delete_network'),
    path('network/<str:pk>/roadtype/', create_roadtype, name='roadtype'),
    path('network/<str:pk>/details/', network_details, name='network_details'),
    path('network/<str:pk>/upload_node/', upload_node, name='upload_node'),
    path('network/<str:pk>/upload_edge/', upload_edge, name='upload_edge'),
    path('visualization/<str:pk>/', visualization, name='network_visualization'
         ),
    path('network/<str:pk>/upload_road/', upload_road, name='upload_road'),
    path('csv/', upload_csv, name='upload_csv')
]
