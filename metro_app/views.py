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

from django.shortcuts import render, redirect
from django.http import HttpResponse
# from django.contrib import messages
from django.contrib.auth.models import User
from .forms import ProjectForm, RoadTypeForm, RoadNetworkForm
from .models import Node, Edge, Project, RoadNetwork, RoadType
from .networks import make_network_visualization
import os
from django.conf import settings
import json

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
    return render(request, 'views/project.html', {'form': form})


def update_project(request, pk):
    project = Project.objects.get(id=pk)
    form = ProjectForm(instance=project)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form, 'project': project}
    return render(request, 'update_project.html', context)


def delete_project(request, pk):
    project_to_delete = Project.objects.get(id=pk)
    if request.method == 'POST':
        project_to_delete.delete()
        return redirect('home')

    context = {'project_to_delete': project_to_delete}
    return render(request, 'delete_project.html', context)


def project_details(request, pk):
    project = Project.objects.get(id=pk)
    roadnetworks = project.roadnetwork_set.all()
    total_roadnetworks = roadnetworks.count()

    context = {
        'project': project,
        'roadnetworks': roadnetworks,
        'total_roadnetworks': total_roadnetworks
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
        network = RoadNetwork(project=current_project)
        form = RoadNetworkForm(request.POST, instance=network)
        if form.is_valid():
            form.save()
            return redirect('project_details', current_project.pk)

    context = {'form': form}
    return render(request, 'views/roadnetwork_form.html', context)


def network_details(request, pk):

    roadnetwork = RoadNetwork.objects.get(id=pk)
    total_nodes = Node.objects.filter(network_id=pk).count()
    total_edges = Edge.objects.filter(network_id=pk).count()

    context = {
        'roadnetwork': roadnetwork,
        'total_nodes': total_nodes,
        'total_edges': total_edges
    }

    return render(request, 'views/network_details.html', context)


def update_network(request, pk):
    roadnetwork = RoadNetwork.objects.get(id=pk)
    form = RoadNetworkForm(instance=roadnetwork)
    if request.method == 'POST':
        form = RoadNetworkForm(request.POST, instance=roadnetwork)
        if form.is_valid():
            form.save()
            return redirect('project_details', roadnetwork.project.pk)

    context = {'form': form}
    return render(request, 'update_network.html', context)


def delete_network(request, pk):
    network_to_delete = RoadNetwork.objects.get(id=pk)
    if request.method == 'POST':
        network_to_delete.delete()
        return redirect('project_details', network_to_delete.project.pk)

    context = {'network_to_delete': network_to_delete}
    return render(request, 'delete_network.html', context)


def visualization(request, pk):
    template = 'visualization/index-visualization.html'
    roadnetwork = RoadNetwork.objects.get(id=pk)
    context = {"roadnetwork": roadnetwork,
               }
    """directory = os.path.join(
        settings.TEMPLATES[0]['DIRS'][0],
            'visualization') +"/"+ roadnetwork.name
    template_full_path = directory + "/map.html"
    if os.path.exists(template_full_path):
        context.update({'template': template_full_path})
        #return render(request, str(template_full_path), context)
        return render(request, template, context)
    else:
        make_network_visualization(pk)
        template_full_path = directory + "/map.html"
        context.update({'template': template_full_path})
        #return render(request, str(template_full_path), context)
        return render(request, template, context)"""
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

    return render(request, 'views/roadtype.html', {'form': form})

# ........................................................................... #
#             VIEW OF RETURNIGNG EDGES GeoJSON FILE                           #
# ............................................................................#

def edges_point_geojson(request):
    with open("/home/andiaye/Bureau/metroweb/Metropolis/templates/visualization/Circular City/edges.geojson") as edges:
        #edges = json.load(edges)
        #edges=json.dumps(edges)
        return HttpResponse(edges, content_type="application/json")
