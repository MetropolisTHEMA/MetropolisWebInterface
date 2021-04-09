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

git remote add orign https://github.com/aba2s/Metropolis.git
git push -u origin main
Sphinx
------
We will come back to this section later.

Django Views Modules
====================
"""

from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    """
    Describes the data presented to the user.

    request : user request
    """
    return render(request, 'index.html')
    #return HttpResponse('Welcome to metroplis app')
