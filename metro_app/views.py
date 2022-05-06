"""
Initial Django Project Set Up
=============================
* First of all install Pyton 3 (Python 3.x). This project will not work
prorperly under python 3 version.
* Then install Django. Notice : Don't install Django within your whole os.
Create your project folder and
  install it in.
* Virtual Environments are an indispensable part of « They are an isolated
container containing all the
  software dependencies for a given project. This is important because by
  default software like Python and
  Django is installed in the same directory. This causes a problem when you
  want to work on multiple projects
  on the same computer. What if ProjectA uses Django 3.1 but ProjectB from
  last year is still on Django 2.2?
  Without virtual environments this becomes very difficult; with virtual
   environments it’s no problem at all
* Create your new Django project and app. Two folders will be created;
 one containg the app files and the other
  the whole project folder.The most important file is setting.py included
   in the project folder. Within this
  file, we will set up our postgresql database.

PostgreSQL
----------
* Install postgres by following the instruction and open it one finish.
So you have a PostgreSQL server ready and  waiting nexw connections.
* Create your project database by psql command line or by using pgAdmin
(install it). The second option is very
  easy and useful.
* Postgres PgAdmin allows you to create all kinds of PostgreSQL database server
objects. These objects can be  databases, schemas, tables, users ... It can
also be used to execute SQL queries.

Settings file
-------------
* By default Django specifies sqlite3 as the database engine, gives it the name
 db.sqlite3, and places it at BASE_DIR
  which means in our project-level directory (top directory of our project
  which contains config, manage.py, Pipfile,
  Pipfile.lock).
* To switch ower to PostgreSQL, we will update the ENGINE configuration.
PostgreSQL requires a NAME, USER, PASSWORD,
  HOST and PORT. All these variables must be in capital letter.

::

    DATABASES = {
         'default': {
         'ENGINE': 'django.db.backends.postgresql',
         'NAME': 'database name created early',
         'USER': 'user name',
         'PASSWORD':'yourpassword',
         'HOST': 'localhost',  # can be your aws host service.
         'PORT': 5432 # default port. Free to choose another one.
        }
    }

* Postgres being a different software and Django being a different software,
  so how do they connect to each otehr?

To answer to this quesstion to need to install a connector.

psycopg2
--------
Psycopg is, the most popular database adapter for Python programming langage.
« If you’d like to learn more about how Psycopg works here is a link to a full
 description on the official site. https://www.psycopg.org/docs/index.html

Git
---
Git is the version control system of choice these days and we’ll use it in this
project. First add a new Git file with git init,
then check the status of changes, add updates, and include a commit message.

* git init
* git status
* git add -A
* git commit -m 'your message'

GitHub
------
It's a good habit to create a remote repository of our code for each project.
This way you have a backup in case anything happens
to your computer and more importantly, it allows for collaboration with other
software developers. Popular choices include GitHub,
Bitbucket, and GitLab. When you’re learning web development, it’s best to stick
to private rather than public repositories so you
don’t inadvertently post critical information such as passwords online.
To link you local development to your git remote repository, and push, type
the following command :

git remote add orign https://github.com/aba2s/Metropolis.git
git push -u origin main


Sphinx
------
We will come back to this section later.

Django Views Modules
====================
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.template import loader
from .forms import (ProjectForm, RoadTypeForm, RoadNetworkForm, ZoneSetForm,
                    ODMatrixForm)
from .models import (Node, Edge, Project, RoadNetwork, RoadType, ZoneSet,
                     Zone, ODMatrix, ODPair, Vehicle, Preferences, Population,
                     Network, PopulationSegment, ParameterSet, Run,
                     BackgroundTask)
from .networks import make_network_visualization, get_network_directory
from .tables import (EdgeTable, NodeTable, RoadTypeTable, ZoneTable,
                     ODPairTable)
from .filters import (EdgeFilter, NodeFilter, RoadTypeFilter, ZoneFilter,
                      ODPairFilter)

import os
from pyproj import CRS
from pyproj.exceptions import CRSError
from django_tables2 import RequestConfig
import json
from django_q.tasks import async_task, result, fetch, Task


# Create your views here.
def index(request):
    projects = Project.objects.all()
    roadnetworks = RoadNetwork.objects.all()
    users = User.objects.all()

    total_projects = projects.count()
    total_roadnetworks = roadnetworks.count()
    total_users = users.count()

    context = {
        'projects': projects,
        'roadnetworks': roadnetworks,
        'users': users,
        'total_projects': total_projects,
        'total_roadnetworks': total_roadnetworks,
        'total_users': total_users
    }
    return render(request, 'dashboard.html', context)


def delete_nodes(request, pk):
    roadnetwork = RoadNetwork.objects.get(id=pk)
    nodes = Node.objects.filter(network=roadnetwork)
    if request.method == 'POST':
        nodes.delete()
        messages.success(request, 'Nodes types deleted!')
        return redirect('road_network_details', pk)

    context = {
        'roadnetwork': roadnetwork,
        'nodes_to_delete': nodes
    }
    return render(request, 'delete.html', context)


def delete_roads_types(request, pk):
    roadnetwork = RoadNetwork.objects.get(id=pk)
    roads_types = RoadType.objects.filter(network=roadnetwork)
    if request.method == 'POST':
        roads_types.delete()
        messages.success(request, 'Roads types deleted!')
        return redirect('road_network_details', pk)

    context = {
        'roadnetwork': roadnetwork,
        'roads_types_to_delete': roads_types
    }
    return render(request, 'delete.html', context)

def delete_zones(request, pk):
    zoneset = ZoneSet.objects.get(id=pk)
    zones = Zone.objects.filter(zone_set=zoneset)
    if request.method == 'POST':
        zones.delete()
        messages.success(request, "Zones successfully deleted")
        return redirect('zoneset_details', zoneset.pk)
    
    context = {
        'zoneset': zoneset,
        'zones_to_delete': zones
    }
    return render(request, 'delete.html', context)

# ............................................................................#
#                   VIEW OF SAVING A PROJECT IN THE DATABASE                  #
# ............................................................................#


def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            # Set the project owner to the user who made the request.
            project.owner = request.user
            try:
                project.save()
            except Exception as e:
                messages.error(request, e)
                return redirect('create_project')
            else:
                msg = "Project <{}> successfully created".format(project.name)
                messages.success(request, msg)
                return redirect('home')

    form = ProjectForm()
    context = {
        'form': form,
    }
    return render(request, 'form.html', context)


def update_project(request, pk):
    project = Project.objects.get(id=pk)
    form = ProjectForm(instance=project)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {
        'form': form,
        'project': project,
        'parent_template': 'index.html',
        }
    return render(request, 'update.html', context)


def delete_project(request, pk):
    project_to_delete = Project.objects.get(id=pk)
    if request.method == 'POST':
        project_to_delete.delete()
        return redirect('home')

    context = {
        'project_to_delete': project_to_delete
    }
    return render(request, 'delete.html', context)


def project_details(request, pk):
    project = Project.objects.get(id=pk)
    roadnetworks = project.roadnetwork_set.all()
    total_roadnetworks = roadnetworks.count()
    zonesets = project.zoneset_set.all()
    total_zonesets = zonesets.count()
    od_matrix = project.odmatrix_set.all()
    total_od_matrix = od_matrix.count()
    vehicles = Vehicle.objects.filter(project=project)
    preferences = Preferences.objects.filter(project=project)
    populations = Population.objects.filter(project=project)
    networks = Network.objects.filter(project=project)
    parametersets = ParameterSet.objects.filter(project=project)
    runs = Run.objects.filter(project=project)
    tasks = project.backgroundtask_set.order_by('-start_date')[:5]

    is_od_matrix_disabled = not zonesets
    is_preferences_disabled = not vehicles
    is_network_disabled = not populations or not roadnetworks
    is_population_disabled = not preferences or not od_matrix
    is_run_disabled = not populations or not networks or not parametersets

    context = {
        'project': project,
        'roadnetworks': roadnetworks,
        'total_roadnetworks': total_roadnetworks,
        'zonesets': zonesets,
        'total_zonesets': total_zonesets,
        'od_matrix': od_matrix,
        'total_od_matrix': total_od_matrix,
        'vehicles': vehicles,
        'preferences': preferences,
        'populations': populations,
        'parametersets': parametersets,
        'networks': networks,
        'runs': runs,
        'tasks': tasks,
        
        # boolean fields
        'is_od_matrix_disabled': is_od_matrix_disabled,
        'is_preferences_disabled': is_preferences_disabled,
        'is_network_disabled': is_network_disabled,
        'is_population_disabled': is_population_disabled,
        'is_run_disabled': is_run_disabled,
    }

    return render(request, 'project/workflow.html', context)

def visualization(request, pk):
    roadnetwork = RoadNetwork.objects.get(id=pk)
    total_nodes = Node.objects.select_related(
        'network)').filter(network_id=pk).count()
    total_edges = Edge.objects.select_related(
        'network').filter(network_id=pk).count()

    if total_edges == 0 or total_nodes == 0:
        messages.warning(request, "Edges are not uploaded !")
        return redirect('road_network_details', roadnetwork.pk)

    directory = get_network_directory(roadnetwork)
    data_full_path = os.path.join(directory, "edges.geojson")
    if not os.path.exists(data_full_path):
        make_network_visualization(pk)
    with open(data_full_path, "r") as f:
        file_js = json.load(f)

    context = {"roadnetwork": roadnetwork,
               "geojson": file_js
               }
    return render(request, 'index-visualization.html', context)



# ........................................................................... #
#             VIEW OF RETURNIGNG EDGES GeoJSON FILE                           #
# ............................................................................#


def edges_point_geojson(request, pk):
    """"
    This module display a saved edge file as an api in order to be
    able to us it as a javascript variable and map it
    """
    roadnetwork = RoadNetwork.objects.get(id=pk)
    directory = get_network_directory(roadnetwork)
    filename = os.path.join(directory, "edges.geojson")
    with open(filename) as edges:
        # edges = json.load(edges)
        # edges=json.dumps(edges)
        return HttpResponse(edges, content_type="application/json")

def fetch_task(request, task_id):
    task = get_object_or_404(BackgroundTask, pk=task_id)
    template = loader.get_template('background_task/task.html')
    html = template.render({"task": task}, request)
    data = {
        "finished": task.status != task.INPROGRESS,
        "html": html,
    }
    return JsonResponse(data)
