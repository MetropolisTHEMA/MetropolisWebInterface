from metro_app.models import (Project, RoadNetwork, ZoneSet,
                              ODMatrix, Preferences, Population,
                              Run, Node, Edge,
                              )
from metro_app.forms import (RoadNetworkForm, )
from django.shortcuts import render, redirect
from pyproj import CRS
from pyproj.exceptions import CRSError
from django.contrib import messages

# ........................................................................... #
#                      VIEW OF CREATING A ROADNETWORK                         #
# ............................................................................#


def create_road_network(request, pk):
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
            roadnetwork = RoadNetwork(project=current_project)
            form = RoadNetworkForm(request.POST, instance=roadnetwork)
            if form.is_valid():
                form.save()
                messages.success(request, "road network successfully created")
                return redirect('road_network_details', roadnetwork.pk)

    context = {
        'form': form,
        'project': current_project,
    }
    return render(request, 'form.html', context)


def road_network_details(request, pk):

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
    return render(request, 'details.html', context)


def update_road_network(request, pk):
    roadnetwork = RoadNetwork.objects.get(id=pk)
    form = RoadNetworkForm(instance=roadnetwork)
    if request.method == 'POST':
        form = RoadNetworkForm(request.POST, instance=roadnetwork)
        srid = int(request.POST.get('srid'))
        try:
            CRS.from_user_input(srid)
        except CRSError:
            messages.warning(request, 'Invalid Coordinates Reference System')
            return redirect('update_road_network', roadnetwork.pk)
        else:
            if form.is_valid():
                form.save()
                return redirect('list_of_road_networks', roadnetwork.project.pk)

    context = {
        'form': form,
        'parent_template': 'base.html',
        }
    return render(request, 'update.html', context)


def delete_road_network(request, pk):
    roadnetwork = RoadNetwork.objects.get(id=pk)
    if request.method == 'POST':
        roadnetwork.delete()
        return redirect('list_of_road_networks', roadnetwork.project.pk)

    context = {
        'road_network_to_delete': roadnetwork
    }
    return render(request, 'delete.html', context)


def list_of_road_networks(request, pk):
    current_project = Project.objects.get(id=pk)
    roadnetworks = RoadNetwork.objects.filter(project=current_project)
    total_roadnetworks = roadnetworks.count()
    context = {
        'current_project': current_project,
        'roadnetworks': roadnetworks,
        'total_roadnetworks': total_roadnetworks,

    }
    return render(request, 'list.html', context)


def list_of_zonesets(request, pk):
    current_project = Project.objects.get(id=pk)
    zonesets = ZoneSet.objects.filter(project=current_project)
    total_zonesets = zonesets.count()
    context = {
        'current_project': current_project,
        'zonesets': zonesets,
        'total_zonesets': total_zonesets,

    }
    return render(request, 'list.html', context)


def list_of_od_matrix(request, pk):
    current_project = Project.objects.get(id=pk)
    od_matrix = ODMatrix.objects.filter(project=current_project)
    total_od_matrix = od_matrix.count()
    context = {
        'current_project': current_project,
        'od_matrix': od_matrix,
        'total_od_matrix': total_od_matrix,

    }
    return render(request, 'list.html', context)


def list_of_preferences(request, pk):
    current_project = Project.objects.get(id=pk)
    preferences = Preferences.objects.filter(project=current_project)
    total_preferences = preferences.count()
    context = {
        'current_project': current_project,
        'preferences': preferences,
        'total_preferences': total_preferences,

    }
    return render(request, 'list.html', context)


def list_of_populations(request, pk):
    current_project = Project.objects.get(id=pk)
    populations = Population.objects.filter(project=current_project)
    total_populations = populations.count()
    context = {
        'current_project': current_project,
        'populations': populations,
        'total_populations': total_populations,

    }
    return render(request, 'list.html', context)

def list_of_runs(request, pk):
    current_project = Project.objects.get(id=pk)
    runs = Run.objects.filter(project=current_project)
    total_runs = runs.count()
    context = {
        'current_project': current_project,
        'runs': runs,
        'total_runs': total_runs,

    }
    return render(request, 'list.html', context)