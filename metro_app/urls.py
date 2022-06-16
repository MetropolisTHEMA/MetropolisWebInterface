from django.urls import path
from .views import (create_project, delete_nodes, delete_edges, delete_roads_types,
                    delete_zones, project_details, update_project,
                    delete_project, index, visualization,
                    edges_point_geojson, fetch_task,
                    )
from metro_app.vehicle.views import (upload_vehicle, add_vehicle,
                                     update_vehicle, delete_vehicle,
                                     create_vehicle_set, vehicle_set_details,
                                     update_vehicle_set, delete_vehicle_set,
                                     vehicle_table)
from metro_app.preferences.views import (add_preferences, upload_preferences,
                                         update_preferences, delete_preferences,
                                         list_of_preferences,
                                         )
from metro_app.population.views import (add_population, update_population,
                                        delete_population, population_details,
                                        create_population_segment,
                                        update_population_segment,
                                        delete_population_segment,
                                        population_segment_details,
                                        list_of_populations,
                                        )
from metro_app.network.views import (create_network, update_network,
                                     list_of_networks, network_details,
                                     upload_zone_node_relation,
                                     zone_node_relation_table,)
from metro_app.road_network.views import (
                                          create_road_network, update_road_network,
                                          road_network_details, delete_road_network,
                                          list_of_road_networks, upload_road_type,
                                          create_roadtype,edges_table, nodes_table,
                                          road_type_table,
                                        )
from metro_app.zone_set.views import (list_of_zonesets, upload_zone,
                                      zoneset_details, create_zoneset,
                                      update_zoneset, delete_zoneset,
                                      zones_table,
                                      )
from metro_app.od_matrix.views import (list_of_od_matrix, upoload_od_pair,
                                        create_od_matrix, od_matrix_details,
                                        update_od_matrix, delete_od_matrix,
                                        od_pair_table, delete_od_pair)
from metro_app.agent.views import (add_agent, upload_agent, agent_table,   
                                   generate_agents_input, delete_agents)
from metro_app.parameters.views import (set_parameters, upload_parameters,
                                        list_of_parameters,)
from metro_app.run.views import (create_run, update_run, run_details,
                                 delete_run, generate_run_input,
                                 list_of_runs, start_run
                                 )
from .networks import (upload_edge, upload_node)
from .metrosim import upload_edges_results


urlpatterns = [
     path('', index, name='home'),
     path('project/<str:pk>/list_of_road_networks/', list_of_road_networks,
          name='list_of_road_networks'),
     path('project/<str:pk>/list_of_zonesets/', list_of_zonesets,
          name='list_of_zonesets'),
     path('project/<str:pk>/list_of_od_matrix/', list_of_od_matrix,
          name='list_of_od_matrix'),
     path('project/<str:pk>/list_of_preferences/', list_of_preferences,
          name='list_of_preferences'),
     path('project/<str:pk>/list_of_populations/', list_of_populations,
          name='list_of_populations'),
     path('project/<str:pk>/list_of_networks/', list_of_networks,
          name='list_of_networks'),
     path('project/<str:pk>/list_of_populations/', list_of_populations,
          name='list_of_populations'),
     path('project/<str:pk>/list_of_runs/', list_of_runs,
          name='list_of_runs'),
     path('roadnetwork/<str:pk>/delete/nodes', delete_nodes, name='delete_nodes'),
     path('roadnetwork/<str:pk>/delete/edges', delete_edges, name='delete_edges'),
     path('roadnetwork/<str:pk>/delete/road_types', delete_roads_types,
          name='delete_roads_types'),
     path('zoneset/<str:pk>/delete/zones', delete_zones,
          name='delete_zones'),
     path('create_project/', create_project, name='create_project'),
     path('project/<str:pk>/details/', project_details, name='project_details'),
     path('update_project/<str:pk>/', update_project, name='update_project'),
     path('delete_project/<str:pk>/', delete_project, name='delete_project'),
     path('project/<str:pk>/create/roadnetwork/', create_road_network,
          name='create_road_network'),
     path('roadnetwork/<str:pk>/update/', update_road_network, name='update_road_network'),
     path('roadnetwork/<str:pk>/delete', delete_road_network, name='delete_road_network'),
     path('roadnetwork/<str:pk>/roadtype/', create_roadtype, name='roadtype'),
     path('roadnetwork/<str:pk>/details/', road_network_details, name='road_network_details'),
     path('roadnetwork/<str:pk>/upload_node/', upload_node, name='upload_node'),
     path('roadnetwork/<str:pk>/upload_edge/', upload_edge, name='upload_edge'),
     path('visualization/roadnetwork/<str:pk>/', visualization,
          name='network_visualization'),
     path('roadnetwork/<str:pk>/upload_road_type/', upload_road_type, name='upload_road_type'
          ),
     path('roadnetwork/<str:pk>/edges.geojson/', edges_point_geojson),
     path('metrosim/roadnetwork/<str:pk>/upload_edges_results/',
          upload_edges_results),
     path('table/road_network/<str:pk>/edges/', edges_table, name='edges'),
     path('table/road_network/<str:pk>/nodes/', nodes_table, name='nodes'),
     path('table/road_network/<str:pk>/roadtype/', road_type_table,
          name='roadtable'),
     path('zoneset/project/<str:pk>/', create_zoneset, name='create_zoneset'),
     path('zoneset/<str:pk>/details/', zoneset_details, name='zoneset_details'),
     path('update_zoneset/<str:pk>/', update_zoneset, name='update_zoneset'),
     path('delete_zoneset/<str:pk>/', delete_zoneset, name='delete_zoneset'),
     path('zone/<str:pk>/upload_zone/', upload_zone, name='upload_zone'),
     path('table/zoneset/<str:pk>/zones/', zones_table, name='zones'),
     path('odmatrix/project/<str:pk>/', create_od_matrix,
          name='create_od_matrix'),
     path('odmatrix/<str:pk>/details/', od_matrix_details,
          name='od_matrix_details'),
     path('update_odmatrix/<str:pk>/', update_od_matrix,
          name='update_od_matrix'),
     path('delete_od_matrix/<str:pk>/', delete_od_matrix,
          name='delete_od_matrix'),
     path('odmatrix/<str:pk>/upoload_od_pair/', upoload_od_pair,
          name='upoload_od_pair'),
     path('table/odmatrix/<str:pk>/odpair/', od_pair_table,
          name='od_pair'),
     path('odmatrix/<str:pk>/delete_od_pair/', delete_od_pair,
          name='delete_od_pair'),
     path('task/<uuid:task_id>/', fetch_task, name='fetch_task'),
     path('vehicle/project/<str:pk>/upload_vehicle', upload_vehicle,
          name='upload_vehicle'),
     path('vehicle/project/<str:pk>/add_vehicle', add_vehicle,
          name='add_vehicle'),
     path('update_vehicle/<str:pk>/', update_vehicle, name='update_vehicle'),
     path('delete_vehicle/<str:pk>/', delete_vehicle, name='delete_vehicle'),
     path('table/project/<str:pk>/vehicle/', vehicle_table,
          name='vehicle_table'),
     path('preferences/project/<str:pk>/', add_preferences,
          name='add_preferences'),
     path('project/<str:pk>/upload_preferences/', upload_preferences,
          name='upload_preferences'),
     path('update_preferences/<str:pk>', update_preferences,
          name='update_preferences'),
     path('delete_preferences/<str:pk>/', delete_preferences,
          name='delete_preferences'),
     path('population/project/<str:pk>/', add_population,
          name='add_population'),
     path('population/<str:pk>/update', update_population,
          name='update_population'),
     path('population/<str:pk>/delete', delete_population,
          name='delete_population'),
     path('population/<str:pk>/details/', population_details,
          name='population_details'),
     path('project/<str:pk>/create_network/', create_network,
          name='create_network'),
     path('network/<str:pk>/update/', update_network,
          name='update_network'),
     path('network/<str:pk>/details/', network_details,
          name='network_details'), 
     path('network/<str:pk>/upload_zone_node_relation',
          upload_zone_node_relation, name='upload_zone_node_relation'),
     path('population/<str:pk>/create_segment/', create_population_segment,
          name='create_population_segment'),
     path('update_psegment/<str:pk>/', update_population_segment,
          name='update_population_segment'),
     path('delete_psegment/<str:pk>/', delete_population_segment,
          name='delete_population_segment'),
     path('psegment/<str:pk>/details/', population_segment_details,
          name='population_segment_details'),
     path('population/<str:pk>/add_agent', add_agent, name='add_agent'),
     path('population/<str:pk>/upload_agent/', upload_agent,
          name='upload_agent'),
     path('population/<str:pk>/delete_agents/', delete_agents,
          name='delete_agents'),
     path('parameterset/project/<str:pk>/', set_parameters,
          name='set_parameters'),
     path('parameterset/<str:pk>/upload_parameters/', upload_parameters,
          name='upload_parameters'),
     path('project/<str:pk>/list_of_parameters/', list_of_parameters,
          name='list_of_parameters'),
     path('project/<str:pk>/create_run/', create_run,
          name='create_run'),
     path('run/<str:pk>/details/', run_details,
          name='run_details'),
     path('run/<str:pk>/update/', update_run,
          name='update_run'),
     path('run/<str:pk>/delete', delete_run,
          name='delete_run'),
     path('population/<str:pk>/generate_agent/', generate_agents_input,
          name='generate_agent'),
     path('run/<str:pk>/generate_run_input/', generate_run_input,
          name='generate_run_input'),
     path('run/<str:pk>/start_run/', start_run, name='start_run'),
     path('table/population/<str:pk>/agent/', agent_table,
          name='agent_table'),
     path('table/network/<str:pk>/zone_node_relation/', zone_node_relation_table,
          name='zone_node_relation_table'),
]
