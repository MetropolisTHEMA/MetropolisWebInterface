from django.urls import path, include
from .views import (edge_list, edge_detail, edges_of_a_network,edges_results)
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('edges/', edge_list),
    path('edges/<int:pk>/', edge_detail),
    path('network/<int:pk>/edges/', edges_of_a_network),
    path('metrosim/edges_results/', edges_results),
    ]

"""

from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    path('edges/', views.EdgeList.as_view()),
    path('edges/<int:pk>/', views.EdgeDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
"""
