from django.urls import path
from .views import (create_project, create_network, create_roadtype,
                    project_details, update_network, update_project,
                    delete_project, network_details, index,
                    delete_network, visualization, edges_point_geojson,
                    edges_table, nodes_table, road_type_table)

from .networks import (upload_edge, upload_node, upload_road_type)
from .metrosim import upload_edges_results

urlpatterns = [
    path('', index, name='home'),
    path('project/', create_project, name='create_project'),
    path('project/<str:pk>/', project_details, name='project_details'),
    path('update_project/<str:pk>/', update_project, name='update_project'),
    path('delete_project/<str:pk>/', delete_project, name='delete_project'),
    path('network/project/<str:pk>/', create_network, name='create_network'),
    path('update_network/<str:pk>/', update_network, name='update_network'),
    path('delete_network/<str:pk>/', delete_network, name='delete_network'),
    path('network/<str:pk>/roadtype/', create_roadtype, name='roadtype'),
    path('network/<str:pk>/details/', network_details, name='network_details'),
    path('network/<str:pk>/upload_node/', upload_node, name='upload_node'),
    path('network/<str:pk>/upload_edge/', upload_edge, name='upload_edge'),
    path('visualization/network/<str:pk>/', visualization,
         name='network_visualization'),
    path('network/<str:pk>/upload_road/', upload_road_type, name='upload_road'
         ),
    path('network/<str:pk>/edges.geojson/', edges_point_geojson),
    path('metrosim/<str:pk>/upload_edges_results/', upload_edges_results),
    path('table/network/<str:pk>/edges/', edges_table, name='edges'),
    path('table/network/<str:pk>/nodes/', nodes_table, name='nodes'),
    path('table/network/<str:pk>/roadtype/', road_type_table,
         name='roadtable'),
]
