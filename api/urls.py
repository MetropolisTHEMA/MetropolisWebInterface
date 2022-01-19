from django.urls import path, include
from .views import (edge_list, edge_detail,
                    edges_of_a_network,
                    single_edge_instance_of_a_network,
                    get_lanes_field_attribute,
                    get_length_field_attribute,
                    get_speed_field_attribute,
                    get_field_from_edges_results,
                    )
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('edges/', edge_list),
    path('edges/<int:pk>/', edge_detail),
    path('network/<int:pk>/edges/', edges_of_a_network),
    path('network/<int:pk>/edge_id/<int:id>',
         single_edge_instance_of_a_network),
    path('network/<int:pk>/edges/lanes/',
         get_lanes_field_attribute),
    path('network/<int:pk>/edges/length/',
         get_length_field_attribute),
    path('network/<int:pk>/edges/speed/',
         get_speed_field_attribute),
    path('run/<str:pk>/edges_results/<str:field>', get_field_from_edges_results),
    
    ]

"""from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    path('edges/', views.EdgeList.as_view()),
    path('edges/<int:pk>/', views.EdgeDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)"""
