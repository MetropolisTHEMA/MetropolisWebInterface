from metro_app.models import (Project, RoadNetwork, ZoneSet,
                              ODMatrix, Preferences, Population,
                              Run, Node, Edge, RoadType, BackgroundTask,
                              )
from metro_app.forms import (RoadNetworkForm, RoadTypeForm,
                             RoadTypeFileForm,
                            )
from metro_app.filters import (EdgeFilter, NodeFilter, RoadTypeFilter)
from metro_app.tables import (EdgeTable, NodeTable, RoadTypeTable)
from django_tables2 import RequestConfig
from django.shortcuts import render, redirect
from pyproj import CRS
from pyproj.exceptions import CRSError
from django.contrib import messages
import csv
from django_q.tasks import async_task
from metro_app.hooks import str_hook
from django.db import IntegrityError

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

# ........................................................................... #
#                      VIEW OF CREATING A ROAD TYPE                           #
# ............................................................................#

def create_roadtype(request, pk):
    """A roadtype depends on a project. It
     must be created inside the roadnetwork"""

    current_roadnetwork = RoadNetwork.objects.get(id=pk)
    form = RoadTypeForm(initial={'roadnetwork': current_roadnetwork})
    if request.method == 'POST':
        road_type = RoadType(network=current_roadnetwork)
        form = RoadTypeForm(request.POST, instance=road_type)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {
        'form': form,
        'roadnetwork': current_roadnetwork,
    }
    return render(request, 'form.html', context)

CONGESTION_TYPES = {
    'freeflow': RoadType.FREEFLOW,
    'free-flow': RoadType.FREEFLOW,
    'free flow': RoadType.FREEFLOW,
    'bottleneck': RoadType.BOTTLENECK,
    'logdensity': RoadType.LOGDENSITY,
    'log-density': RoadType.LOGDENSITY,
    'log density': RoadType.LOGDENSITY,
    'bpr': RoadType.BPR,
    'linear': RoadType.LINEAR,
}

def read_road_type_file(file, road_network_id):
    roadnetwork = RoadNetwork.objects.get(id=road_network_id)
    if file.name.endswith('.csv'):
        data = file.read().decode('utf-8').splitlines()
        data = csv.DictReader(data, delimiter=',')
        list_roadtype_instance = []
        for row in data:  # each row is dictionary
            row = {k: None if not v else v for k, v in row.items()}
            try:
                road_type_id = row['id']
                name = row['name']
                congestion = congestion=CONGESTION_TYPES[row['congestion'].lower()]
            except KeyError:
                return "There is a problem with the file field. Or a Wrong file imported !"
            else:
                roadtype = RoadType(
                    road_type_id=road_type_id,
                    name=name,
                    congestion=congestion,
                    default_speed=row.get('default_speed', None),
                    default_lanes=row.get('default_lanes', None),
                    default_outflow=row.get('default_outflow', None),
                    default_param1=row.get('default_param1', None),
                    default_param2=row.get('default_param2', None),
                    default_param3=row.get('default_param3', None),
                    color=row.get('color', None),
                    network=roadnetwork
                )
                list_roadtype_instance.append(roadtype)
        if list_roadtype_instance:
            try:
                RoadType.objects.bulk_create(list_roadtype_instance)
            except ValueError:
                return "There is a problem Id field. It shouldn't a string."
            except IntegrityError:
                return "There is a problem Id field. It shouldn't be empty."
            else:
                return "Your road type file has been successfully imported !"
        else:
            return "No data uploaded"
    else:
        return "You file does not respect Metropolis format guidelines."

def upload_road_type(request, pk):
    template = "road_network/roadtype.html"
    roadnetwork = RoadNetwork.objects.get(id=pk)
    roadtypes = RoadType.objects.select_related(
        'network').filter(network_id=pk)

    if roadtypes.exists():
        messages.warning(request, "Fail ! Network contains \
                            already road type data.")
        return redirect('road_network_details', roadnetwork.pk)

    if request.method == 'POST':
        form = RoadTypeFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['my_file']
            task_id = async_task(read_road_type_file, file, pk, hook=str_hook)
            description = "Importing Roads Type"
            db_task = BackgroundTask(
                project=roadnetwork.project,
                id=task_id,
                description=description,
                road_network=roadnetwork
            )
            db_task.save()
            messages.success(request, "Task successfully started")
            return redirect('road_network_details', pk)
        else:
            messages.error(request, 'You file does not respect Metropolisormat guidelines')
            return render(request, template, {'form': form})
                
            """ if datafile.name.endswith('.csv'):
                datafile = datafile.read().decode('utf-8').splitlines()
                datafile = csv.DictReader(datafile, delimiter=',')
                for row in datafile:  # each row is dictionary
                    row = {k: None if not v else v for k, v in row.items()}
                    try:
                        road_type_id = row['id']
                        name = row['name']
                    except KeyError:
                        message = "There is a problem with either id or name. \
                                  Id filed shouldn't be string.\
                                  Name field shouldn't be empty."
                        messages.warning(request, message)
                        return redirect('upload_road', roadnetwork.pk)

                    else:
                        roadtype = RoadType(
                            road_type_id=road_type_id,
                            name=name,
                            congestion=CONGESTION_TYPES[
                                       row['congestion'].lower()],
                            default_speed=row.get('default_speed', None),
                            default_lanes=row.get('default_lanes', None),
                            default_outflow=row.get('default_outflow', None),
                            default_param1=row.get('default_param1', None),
                            default_param2=row.get('default_param2', None),
                            default_param3=row.get('default_param3', None),
                            color=row.get('color', None),
                            network=roadnetwork)
                        list_roadtype_instance.append(roadtype)
                if list_roadtype_instance:
                    try:
                        RoadType.objects.bulk_create(list_roadtype_instance)
                    except ValueError:
                        message = "There is a problem Id field. \
                                    It shouldn't a string."
                        messages.warning(request, message)
                        return redirect('upload_road', roadnetwork.pk)
                    except IntegrityError:
                        message = "There is a problem Id field. \
                                    It shouldn't be empty."
                        messages.warning(request, message)
                        return redirect('upload_road', roadnetwork.pk)
                    else:
                        messages.success(request, 'Your road type file has been \
                                          successfully imported !')
                        return redirect('road_network_details', roadnetwork.pk)
                else:
                    messages.warning(request, 'No data uploaded')
                    return redirect('upload_road_type', roadnetwork.pk)
            else:
                messages.error(request, 'You file does not respect Metropolis \
                                format guidelines')
                return render(request, template, {'form': form})"""
    else:
        form = RoadTypeFileForm()
        return render(request, template, {'form': form})

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
    return render(request, 'table/table.html', context)

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
    return render(request, 'table/table.html', context)

def road_type_table(request, pk):
    """
    This function is for displaying database RoadType table in front end UI.
    Users can sort, filter and paginate through pages
    """
    roadnetwork = RoadNetwork.objects.get(id=pk)
    roadtype = RoadType.objects.select_related().filter(network=roadnetwork)
    my_filter = RoadTypeFilter(request.GET, queryset=roadtype)
    table = RoadTypeTable(my_filter.qs)
    RequestConfig(request).configure(table)
    # table.paginate(page=request.Get.get("page", 1), per_page=15)

    current_path = request.get_full_path()
    network_attribute = current_path.split("/")[4]

    context = {
        "table": table,
        "filter": my_filter,
        "roadnetwork": roadnetwork,
        "network_attribute": network_attribute
    }
    return render(request, 'table/table.html', context)


