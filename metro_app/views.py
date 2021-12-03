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
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import (ProjectForm, RoadTypeForm, RoadNetworkForm, ZoneSetForm,
                    ODMatrixForm)
from .models import (Node, Edge, Project, RoadNetwork, RoadType, ZoneSet,
                     Zone, ODMatrix, ODPair, BackgroundTask)
from .networks import make_network_visualization, get_network_directory
from .tables import (EdgeTable, NodeTable, RoadTypeTable, ZoneTable,
                     ODPairTable)
from .filters import (EdgeFilter, NodeFilter, RoadTypeFilter, ZoneFilter,
                      ODPairFilter)

import os
from pyproj import CRS
from pyproj.exceptions import CRSError
from django_tables2 import RequestConfig
from django_q.tasks import async_task, result, fetch, Task
# import json


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
            project.save()
            return redirect('home')

    form = ProjectForm()
    return render(request, 'views/form.html', {'form': form})


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
    tasks = project.backgroundtask_set.order_by('-start_date')[:5]

    context = {
        'project': project,
        'roadnetworks': roadnetworks,
        'total_roadnetworks': total_roadnetworks,
        'zonesets': zonesets,
        'total_zonesets': total_zonesets,
        'od_matrix': od_matrix,
        'total_od_matrix': total_od_matrix,
        'tasks': tasks,
    }

    return render(request, 'views/project_details.html', context)

# ........................................................................... #
#                      VIEW OF CREATING A ROADNETWORK                         #
# ............................................................................#


def create_network(request, pk):
    """A roadnetwork depends on a project. It
     must be created inside the project"""

    current_project = Project.objects.get(id=pk)
    form = RoadNetworkForm(initial={'project': current_project})
    if request.method == 'POST':
        srid = int(request.POST.get('srid'))
        try:
            CRS.from_user_input(srid)
        except CRSError:
            messages.warning(request, 'Invalid Coordinates Reference System')
            return redirect('create_network', current_project.pk)
        else:
            network = RoadNetwork(project=current_project)
            form = RoadNetworkForm(request.POST, instance=network)
            if form.is_valid():
                form.save()
                return redirect('project_details', current_project.pk)

    context = {'form': form}
    return render(request, 'views/form.html', context)


def network_details(request, pk):

    roadnetwork = RoadNetwork.objects.get(id=pk)
    total_nodes = Node.objects.select_related(
        'network)').filter(network_id=pk).count()
    total_edges = Edge.objects.select_related(
        'network').filter(network_id=pk).count()
    tasks = roadnetwork.backgroundtask_set.order_by('-start_date')[:5]

    context = {
        'roadnetwork': roadnetwork,
        'total_nodes': total_nodes,
        'total_edges': total_edges,
        'tasks': tasks,
    }

    return render(request, 'views/details.html', context)


def update_network(request, pk):
    roadnetwork = RoadNetwork.objects.get(id=pk)
    form = RoadNetworkForm(instance=roadnetwork)
    if request.method == 'POST':
        form = RoadNetworkForm(request.POST, instance=roadnetwork)
        srid = int(request.POST.get('srid'))
        try:
            CRS.from_user_input(srid)
        except CRSError:
            messages.warning(request, 'Invalid Coordinates Reference System')
            return redirect('update_network', roadnetwork.pk)
        else:
            if form.is_valid():
                form.save()
                return redirect('project_details', roadnetwork.project.pk)

    context = {
        'form': form,
        'parent_template': 'base.html',
        }
    return render(request, 'update.html', context)


def delete_network(request, pk):
    network_to_delete = RoadNetwork.objects.get(id=pk)
    if request.method == 'POST':
        network_to_delete.delete()
        return redirect('project_details', network_to_delete.project.pk)

    context = {'network_to_delete': network_to_delete}
    return render(request, 'delete.html', context)


def visualization(request, pk):
    roadnetwork = RoadNetwork.objects.get(id=pk)
    total_nodes = Node.objects.select_related(
        'network)').filter(network_id=pk).count()
    total_edges = Edge.objects.select_related(
        'network').filter(network_id=pk).count()
    context = {"roadnetwork": roadnetwork,
               }
    directory = get_network_directory(roadnetwork)
    data_full_path = os.path.join(directory, "edges.geojson")
    if not os.path.exists(data_full_path):
        make_network_visualization(pk)

    if total_edges == 0 or total_nodes == 0:
        messages.warning(request, "Edges are not uploaded !")
        return redirect('network_details', roadnetwork.pk)
    else:
        return render(request, 'index-visualization.html', context)


# ........................................................................... #
#                      VIEW OF CREATING A ROAD TYPE                           #
# ............................................................................#


def create_roadtype(request, pk):
    """A roadtype depends on a project. It
     must be created inside the roadnetwork"""

    current_network = RoadNetwork.objects.get(id=pk)
    form = RoadTypeForm(initial={'roadnetwork': current_network})
    if request.method == 'POST':
        road_type = RoadType(network=current_network)
        form = RoadTypeForm(request.POST, instance=road_type)
        if form.is_valid():
            form.save()
            return redirect('home')

    return render(request, 'views/form.html', {'form': form})

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


def edges_table(request, pk):
    """
    This function is for displaying database Edges table in front end UI.
    Users can sort, filter and paginate through pages
    """
    roadnetwork = RoadNetwork.objects.get(id=pk)
    edges = Edge.objects.select_related().filter(network=roadnetwork)
    filter = EdgeFilter(request.GET, queryset=edges)
    table = EdgeTable(filter.qs)
    RequestConfig(request).configure(table)  # For sorting table column
    table.paginate(page=request.GET.get("page", 1), per_page=15)

    current_path = request.get_full_path()
    network_attribute = current_path.split("/")[4]

    context = {
        "table": table,
        "filter": filter,
        "roadnetwork": roadnetwork,
        "network_attribute": network_attribute
               }
    return render(request, 'views/edges_table.html', context)


def nodes_table(request, pk):
    """
    This function is for displaying database Node table in front end UI.
    Users can sort, filter and paginate through pages
    """
    roadnetwork = RoadNetwork.objects.get(id=pk)
    nodes = Node.objects.select_related().filter(network=roadnetwork)
    filter = NodeFilter(request.GET, queryset=nodes)
    table = NodeTable(filter.qs)
    RequestConfig(request).configure(table)
    # table.paginate(page=request.Get.get("page", 1), per_page=15)

    current_path = request.get_full_path()
    network_attribute = current_path.split("/")[4]

    context = {
        "table": table,
        "filter": filter,
        "roadnetwork": roadnetwork,
        "network_attribute": network_attribute
    }
    return render(request, 'views/edges_table.html', context)


def road_type_table(request, pk):
    """
    This function is for displaying database RoadType table in front end UI.
    Users can sort, filter and paginate through pages
    """
    roadnetwork = RoadNetwork.objects.get(id=pk)
    roadtype = RoadType.objects.select_related().filter(network=roadnetwork)
    filter = RoadTypeFilter(request.GET, queryset=roadtype)
    table = RoadTypeTable(filter.qs)
    RequestConfig(request).configure(table)
    # table.paginate(page=request.Get.get("page", 1), per_page=15)

    current_path = request.get_full_path()
    network_attribute = current_path.split("/")[4]

    context = {
        "table": table,
        "filter": filter,
        "roadnetwork": roadnetwork,
        "network_attribute": network_attribute
    }
    return render(request, 'views/edges_table.html', context)


def create_zoneset(request, pk):
    """A roadnetwork depends on a project. It
     must be created inside the project"""

    current_project = Project.objects.get(id=pk)
    form = ZoneSetForm(initial={'project': current_project})
    if request.method == 'POST':
        srid = int(request.POST.get('srid'))
        try:
            CRS.from_user_input(srid)
        except CRSError:
            messages.warning(request, 'Invalid Coordinates Reference System')
            return redirect('create_network', current_project.pk)
        else:
            zoneset = ZoneSet(project=current_project)
            form = ZoneSetForm(request.POST, instance=zoneset)
            if form.is_valid():
                form.save()
                return redirect('project_details', current_project.pk)

    context = {'form': form}
    return render(request, 'views/form.html', context)


def zoneset_details(request, pk):

    zoneset = ZoneSet.objects.get(id=pk)
    context = {
        'zoneset': zoneset,
    }
    return render(request, 'views/details.html', context)


def update_zoneset(request, pk):
    zoneset = ZoneSet.objects.get(id=pk)
    form = ZoneSetForm(instance=zoneset)
    if request.method == 'POST':
        form = ZoneSetForm(request.POST, instance=zoneset)
        srid = int(request.POST.get('srid'))
        try:
            CRS.from_user_input(srid)
        except CRSError:
            messages.warning(request, 'Invalid Coordinates Reference System')
            return redirect('update_zoneset', zoneset.pk)
        else:
            if form.is_valid():
                form.save()
                return redirect('project_details', zoneset.project.pk)

    context = {
        'form': form,
        'parent_template': 'base.html',
        }
    return render(request, 'update.html', context)


def delete_zoneset(request, pk):
    zoneset_to_delete = ZoneSet.objects.get(id=pk)
    if request.method == 'POST':
        zoneset_to_delete.delete()
        return redirect('project_details', zoneset_to_delete.project.pk)

    context = {
        'zoneset_to_delete': zoneset_to_delete
    }
    return render(request, 'delete.html', context)


def zones_table(request, pk):
    """
    This function is for displaying database Edges table in front end UI.
    Users can sort, filter and paginate through pages
    """
    zoneset = ZoneSet.objects.get(id=pk)
    zones = Zone.objects.select_related().filter(zone_set=zoneset)
    filter = ZoneFilter(request.GET, queryset=zones)
    table = ZoneTable(filter.qs)
    RequestConfig(request).configure(table)  # For sorting table column
    table.paginate(page=request.GET.get("page", 1), per_page=15)

    current_path = request.get_full_path()
    network_attribute = current_path.split("/")[4]

    context = {
        "table": table,
        "filter": filter,
        'zoneset': zoneset,
        "network_attribute": network_attribute
    }
    return render(request, 'views/edges_table.html', context)


def create_od_matrix(request, pk):
    """A roadnetwork depends on a project. It
     must be created inside the project"""

    current_project = Project.objects.get(id=pk)
    form = ODMatrixForm(initial={'project': current_project})
    if request.method == 'POST':
        zoneset = ODMatrix(project=current_project)
        form = ODMatrixForm(request.POST, instance=zoneset)
        if form.is_valid():
            form.save()
            return redirect('project_details', current_project.pk)

    context = {'form': form}
    return render(request, 'views/form.html', context)


def od_matrix_details(request, pk):
    od_matrix = ODMatrix.objects.get(id=pk)
    context = {
        'od_matrix': od_matrix,
    }
    return render(request, 'views/details.html', context)


def update_od_matrix(request, pk):
    od_matrix = ODMatrix.objects.get(id=pk)
    form = ODMatrixForm(instance=od_matrix)
    if request.method == 'POST':
        form = ODMatrixForm(request.POST, instance=od_matrix)
        if form.is_valid():
            form.save()
            return redirect('project_details', od_matrix.project.pk)

    context = {
        'form': form,
        'parent_template': 'base.html',
    }
    return render(request, 'update.html', context)


def delete_od_matrix(request, pk):
    od_matrix_to_delete = ODMatrix.objects.get(id=pk)
    if request.method == 'POST':
        od_matrix_to_delete.delete()
        return redirect('project_details', od_matrix_to_delete.project.pk)

    context = {
        'od_matrix_to_delete': od_matrix_to_delete
    }
    return render(request, 'delete.html', context)


def od_pair_table(request, pk):
    """
    This function is for displaying database Edges table in front end UI.
    Users can sort, filter and paginate through pages
    """
    od_matrix = ODMatrix.objects.get(id=pk)
    od_pair = ODPair.objects.select_related().filter(matrix=od_matrix)
    filter = ODPairFilter(request.GET, queryset=od_pair)
    table = ODPairTable(filter.qs)
    RequestConfig(request).configure(table)  # For sorting table column
    table.paginate(page=request.GET.get("page", 1), per_page=15)

    current_path = request.get_full_path()
    network_attribute = current_path.split("/")[4]

    context = {
        "table": table,
        "filter": filter,
        'od_matrix': od_matrix,
        "network_attribute": network_attribute
    }
    return render(request, 'views/edges_table.html', context)
