from django.urls import path
from .views import *
from .networks import upload_node


urlpatterns=[
    path('', index, name ='home'),
    path('upload/', upload_node, name='upload_node'),
    path('project/', create_project, name='create_project'),
    path('roadnetwork/', create_roadnetwork, name='create_roadnetwork')
]
