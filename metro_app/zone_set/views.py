from django.shortcuts import render, redirect
from django.contrib.gis.geos import Polygon
from django.contrib import messages
from metro_app.models import (Zone, ZoneSet, Project, BackgroundTask,)
from metro_app.forms import ZoneFileForm, ZoneSetForm
from metro_app.filters import ZoneFilter
from metro_app.tables import ZoneTable
from django_tables2 import RequestConfig
from metro_app.hooks import str_hook
from django_q.tasks import async_task
from pyproj import CRS
from pyproj.exceptions import CRSError
import json


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

def zoneset_details(request, pk):
    zoneset = ZoneSet.objects.get(id=pk)
    tasks = zoneset.backgroundtask_set.order_by('-start_date')[:5]
    context = {
        'zoneset': zoneset,
        'tasks': tasks,
    }
    return render(request, 'details.html', context)

def create_zoneset(request, pk):
    """A zoneset depends on a project. It
     must be created inside the project"""

    current_project = Project.objects.get(id=pk)
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
                messages.success(request, "Zone set successfully created")
                return redirect('zoneset_details', zoneset.pk)

    form = ZoneSetForm(initial={'project': current_project})
    context = {
        'project': current_project,
        'form': form
    }
    return render(request, 'form.html', context)

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
                return redirect('list_of_zonesets', zoneset.project.pk)

    context = {
        'form': form,
        'parent_template': 'base.html',
        }
    return render(request, 'update.html', context)

def delete_zoneset(request, pk):
    zoneset_to_delete = ZoneSet.objects.get(id=pk)
    if request.method == 'POST':
        zoneset_to_delete.delete()
        return redirect('list_of_zonesets', zoneset_to_delete.project.pk)

    context = {
        'zoneset_to_delete': zoneset_to_delete
    }
    return render(request, 'delete.html', context)

def async_task_for_zone_set_file(file, zone_set_id):
    list_zone_instance = []
    zoneset = ZoneSet.objects.get(id=zone_set_id)
    if file.name.endswith('.csv'):
        file = file.read().decode('utf-8').splitlines()
        objects = csv.DictReader(file)
        for row in datafile:
            try:
                lon, lat = row['x'], row['y']
            except KeyError:
                    return "Wrong file uploaded!"
            else:
                zone_instance = Zone(
                    zone_id=row['id'],
                    centroid=fromstr(f'POINT({lon} {lat})', srid=4326),
                    geometry=None,
                    radius=row.get('radius', 0.00),
                    name=row.get('name', 'No name'),
                    zone_set=zoneset
                )
                list_zone_instance.append(zone_instance)
        if list_zone_instance :
            try:
                Zone.objects.bulk_create(list_zone_instance)
            except Exception:
                return "There is a problem with your file"
            else:
                return "Zone file has been successfully imported !"
        else:
            return "No data uploaded"

    elif file.name.endswith('.geojson'):
        objects = json.load(file)
        for object in objects['features']:
            properties = object['properties']
            geometry = object['geometry']
            radius = properties.get('radius', 0.00)
            zone_id = properties['id']
            name = properties.get('name', 'No name')
            coordinates = geometry['coordinates']
            # geometry = GEOSGeometry(Polygon(coordinates, srid=4326))
            # geometry = Polygon(  [tuple(l) for l in coordinates[0]], srid=4326)
            if geometry['type'] == 'Polygon':
                geometry = Polygon(coordinates[0], srid=4326)
                centroid = geometry.centroid
            elif geometry['type'] == 'Point':
                centroid = fromstr(
                    f'POINT({coordinates[0]} {coordinates[1]})',srid=4326)
                geometry = None
            else:
                return "Wrong file uploaded!"

            zone_instance = Zone(
                zone_id=zone_id,
                    centroid=centroid,
                    geometry=geometry,
                    radius=radius,
                    name=name,
                    zone_set=zoneset)
            list_zone_instance.append(zone_instance)

        if list_zone_instance :
            try:
                Zone.objects.bulk_create(list_zone_instance)
            except Exception:
                return "There is a problem with your file"
            else:
                return "Zone file has been successfully imported !"
        else:
            return "No data uploaded"
    else:
        return "Unknown file format. File extension must be csv or geojson"


def upload_zone(request, pk):
    template = "zone_set/zone.html"
    zoneset = ZoneSet.objects.get(id=pk)
    zone = zoneset.zone_set.all()
    if zone.exists():
        messages.warning(request, "Zone already contains data")
        return redirect('zoneset_details', pk)
    if request.method == 'POST':
        # File must be included when creating the form
        form = ZoneFileForm(request.POST, request.FILES)
        if form.is_valid():
            # hey, if form is valid, get me back the data from the input form
            my_file = request.FILES['my_file']  # get by name
            async_task_for_zone_set_file(my_file, pk)
            task_id = async_task(async_task_for_zone_set_file,my_file, pk)
            description = "Importing Zone"
            db_task = BackgroundTask(
                project=zoneset.project,
                id=task_id,
                description=description,
                zoneset_set=zoneset
            )
            db_task.save()
            messages.success(request, "Task successfully started")
            return redirect('zoneset_details', pk)
    else:
        form = ZoneFileForm()
        return render(request, template, {'form': form})

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
    # table.paginate(page=request.GET.get("page", 1), per_page=15)

    current_path = request.get_full_path()
    network_attribute = current_path.split("/")[4]

    context = {
        "table": table,
        "filter": filter,
        'zoneset': zoneset,
        "network_attribute": network_attribute
    }
    return render(request, 'table/table.html', context)