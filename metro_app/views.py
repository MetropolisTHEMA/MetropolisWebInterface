"""
Initial Django Project Set Up
=============================
* First of all install Pyton 3 (Python 3.x). This project will not work prorperly under python 3 version.
* Then install Django. Notice : Don't install Django within your whole os. Create your project folder and
  install it in.
* Virtual Environments are an indispensable part of « They are an isolated container containing all the
  software dependencies for a given project. This is important because by default software like Python and
  Django is installed in the same directory. This causes a problem when you want to work on multiple projects
  on the same computer. What if ProjectA uses Django 3.1 but ProjectB from last year is still on Django 2.2?
  Without virtual environments this becomes very difficult; with virtual environments it’s no problem at all
* Create your new Django project and app. Two folders will be created; one containg the app files and the other
  the whole project folder.The most important file is setting.py included in the project folder. Within this
  file, we will set up our postgresql database.

PostgreSQL
----------
* Install postgres by following the instruction and open it one finish. So you hzve a PostgreSQL server ready and
  waiting nexw connections.
* Create your project database by psql command line or by using pgAdmin (install it). The second option is very
  easy and useful.
* Postgres PgAdmin allows you to create all kinds of PostgreSQL database server objects. These objects can be
  databases, schemas, tables, users ... It can also be used to execute SQL queries.

Settings file
-------------
* By default Django specifies sqlite3 as the database engine, gives it the name db.sqlite3, and places it at BASE_DIR
  which means in our project-level directory (top directory of our project which contains config, manage.py, Pipfile,
  Pipfile.lock).
* To switch ower to PostgreSQL, we will update the ENGINE configuration. PostgreSQL requires a NAME, USER, PASSWORD,
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


* Postgres being a different software and Django being a different software, so how do they connect to each otehr?

To answer to this quesstion to need to install a connector.

psycopg2
--------
Psycopg is, the most popular database adapter for Python programming langage. « If you’d like to learn more about
how Psycopg works here is a link to a fuller description on the official site. https://www.psycopg.org/docs/index.html

Git
---
Git is the version control system of choice these days and we’ll use it in this project. First add a new Git file with git init,
then check the status of changes, add updates, and include a commit message.

* git init
* git status
* git add -A
* git commit -m 'your message'

GitHub
------
It's a good habit to create a remote repository of our code for each project. This way you have a backup in case anything happens
to your computer and more importantly, it allows for collaboration with other software developers. Popular choices include GitHub,
Bitbucket, and GitLab. When you’re learning web development, it’s best to stick to private rather than public repositories so you
don’t inadvertently post critical information such as passwords online.
To link you local development to your git remote repository, and push, type the following command :

git remote add orign https://github.com/aba2s/Metropolis.git
git push -u origin main


Sphinx
------
We will come back to this section later.

Django Views Modules
====================
"""

from django.shortcuts import render, redirect
from django.contrib import messages
import django_rq

from .forms import *
from .models import *
from .tasks import *

# Create your views here.
def index(request):
    """
    Describes the data presented to the user.
    request : user request
    """
    return render(request, 'base.html')


#.............................................................................#
#                   VIEW OF SAVING A PROJECT IN THE DATABASE                  #
#.............................................................................#

def create_project(request):
    if request.method=='POST':
        form=ProjectForm(request.POST)
        if form.is_valid():
           form.save()
           return redirect('home')

    form =ProjectForm()
    return render(request, 'project.html', {'form': form})


# ........................................................................... #
#                      VIEW OF CREATING A ROADNETWORK                         #
#............................................................................ #

def create_roadnetwork(request):
    # If this is a post request, we need to process the form data.
    if request.method == 'POST':
        # Let create a form instance from POST data
        form = RoadNetworkForm(request.POST)
        # Check wether the form is valid
        if form.is_valid():
            # let's save a new created roadnetwork object from the form's data
            form.save()
            return redirect('home')

    form = RoadNetworkForm()
    return render(request, 'roadnetwork.html', {'form': form})

# ........................................................................... #
#                      VIEW OF CREATING A ROAD TYPE                         #
#............................................................................ #

def create_roadtype(request):
    # If this is a post request, we need to process the form data.
    if request.method == 'POST':
        # Let create a form instance from POST data
        form = RoadTypeForm(request.POST)
        # Check wether the form is valid
        if form.is_valid():
            # let's save a new created roadtype object from the form's data
            form.save()
            return redirect('home')

    form = RoadTypeForm()
    return render(request, 'roadtype.html', {'form': form})


"""
def upload_node(request):
    template = "upload.html"

    form = NodeForm()
    if request.method == 'POST':
        csv_file = request.FILES['my_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a .csv file.')

        data_set = csv_file.read().decode('utf-8')
        io_string = io.StringIO(data_set)
        next(io_string)
        for column in csv.reader(io_string, delimiter=','):
            _, created = Node.objects.update_or_create(
                node_id=column[0],
                name=column[1],
                location=column[2],
                network_id=column[3],
            )
    elif request.method == 'GET':
        # DO something in GET call
        # message error
        pass

    context = {
        'nodes': Node.objects.all()
    }

    return render(request, template, {'form':form})
"""

def test_async_view(request):
    job = test_task.delay(30)
    return render(request, 'task_success.html', {'job': job})

def test_async_sim_view(request):
    job = test_task_simulation.delay(60)
    return render(request, 'task_success.html', {'job': job})

def test_task_status(request, job_id):
    job = django_rq.get_queue().fetch_job(job_id)
    if not job:
        job = django_rq.get_queue('simulations').fetch_job(job_id)
    return render(request, 'task_status.html', {'job': job})
