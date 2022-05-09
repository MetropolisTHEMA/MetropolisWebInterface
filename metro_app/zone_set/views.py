from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.gis.geos import GEOSGeometry, Polygon, fromstr
from django.contrib import messages
from django.conf import settings
from metro_app.models import (Zone, ZoneSet, Project, BackgroundTask,)
from metro_app.forms import ZoneFileForm, ZoneSetForm
from metro_app.filters import ZoneFilter
from metro_app.tables import ZoneTable
from django_tables2 import RequestConfig
from metro_app.hooks import str_hook
from django_q.tasks import async_task
import uuid
import os
import numpy as np
import pandas as pd
import geopandas as gpd
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

def async_task_for_zone_set_file(zoneset, filepath):
    dtype = {'id': int, 'x': float, 'y': float}
    # Read file with GeoPandas.
    try:
        gdf = gpd.read_file(filepath, dtype=dtype)
        gdf['id'] = gdf['id'].astype(int)
    except Exception as e:
        try:
            df = pd.read_csv(filepath, dtype=dtype)
            df['geometry'] = None
            gdf = gpd.GeoDataFrame(df)
            del df
        except Exception as e1:
            return 'Cannot read file.\n\nError message:\n{}'.format(e1)

    # Check that column id is here.
    if not 'id' in gdf.columns:
        return (
            'Cannot import file.\n\nError message:\nThe following field '
            'is mandatory: id'
        )

    if len(gdf) and gdf.geom_type.isnull().all():
        # The edges have no geometry (the file is probably as CSV).
        # We create the geometries from the x and y coordinates.
        if not 'x' in gdf.columns or not 'y' in gdf.columns:
            return (
                'Cannot import file.\n\nError message:\nThe following fields'
                ' are mandatory: x, y'
            )
        try:
            gdf['geometry'] = gdf.apply(
                lambda row: geom.Point(
                    [float(row['x']), float(row['y'])])
                , axis=1)
        except ValueError:
            return (
                'Cannot import file.\n\nError message:\nInvalid values in '
                'column x or y'
            )

    message = ''
    invalids = ~gdf.geom_type.isin(('Point', 'Polygon'))
    if invalids.any():
        #  The any() function is used to check whether any element is True, potentially over an axis
        # Returns False unless there at least one element within a series or along a Dataframe axis 
        # that is True or equivalent (e.g. non-zero or non-empty).
        message += (
            'Discarding {} invalid geometries (only Points and Polygons are '
            'allowed).\n'
        ).format(invalids.sum())
        gdf = gdf.loc[~invalids]

    if not len(gdf):
        message += 'No valid node to import.\n'
        return message

    if gdf['id'].nunique() != len(gdf):
        counts = gdf['id'].value_counts()
        duplicates = counts.loc[counts > 1].index.astype(str)
        message += (
            'Duplicate ids (only the last one is imported): {}\n'
        ).format(', '.join(duplicates))
        gdf = gdf.groupby('id').last()
    else:
        gdf.set_index('id', inplace=True)

    gdf['is_polygon'] = gdf.geom_type == 'Polygon'

    gdf['gis-geometry'] = gdf['geometry'].apply(lambda g: GEOSGeometry(str(g)))
    gdf['centroid'] = gdf.geometry.centroid
    gdf['gis-centroid'] = gdf['centroid'].apply(lambda g: GEOSGeometry(str(g)))
    
    zones_to_import = list()
    invalid_zones = list()

    def handle_nan(value):
        if value and np.isnan(value):
            return None
        else:
            return value

    for zone_id, row in gdf.iterrows():
        try:
            zone = Zone(
                zone_id=zone_id,
                zone_set=zoneset,
                centroid=row['gis-centroid'],
                geometry=row['gis-geometry'] if row['is_polygon'] else None,
                radius=row.get('radius', 0.00),
                name=row.get('name', ''),
            )
        except Exception as e:
            invalid_zones.append(str(zone_id))
        else:
            zones_to_import.append(zone)
    if invalid_zones:
        message += (
            'The following zones could not be imported correctly: {}\n'
        ).format(', '.join(invalid_zones))

    if not zones_to_import:
        message += 'No zone were imported.\n'
        return message

    # Create the zones in bulk.
    try:
        Zone.objects.bulk_create(zones_to_import)
    except Exception as e:
        message += (
            'Failed to import zones.\n\nError message:\n{}'
        ).format(e)
        return message

    message += 'Successfully imported {} zones.'.format(
        len(zones_to_import))
    return message

def upload_node(request, pk):
    template = "networks/node.html"
    roadnetwork = get_object_or_404(RoadNetwork, pk=pk)
    if Node.objects.filter(network_id=pk).exists():
        messages.warning(request, "The road network already contains nodes.")
        return redirect('road_network_details', roadnetwork.pk)
    if BackgroundTask.objects.filter(
            road_network=roadnetwork, status=BackgroundTask.INPROGRESS
    ).exists():
        messages.warning(
            request, "A task is in progress for this road network.")
        return redirect('road_network_details', roadnetwork.pk)

    if request.method == 'POST':
        # We need to include the files when creating the form
        form = NodeForm(request.POST, request.FILES)
        if form.is_valid():
            # Getting data from the fielfield input
            datafile = request.FILES['my_file']

            # Save file on disk (we cannot send large files as arguments of
            # async tasks).
            filename = '{}-{}'.format(uuid.uuid4(), datafile.name)
            filepath = os.path.join(settings.MEDIA_ROOT, filename)
            with open(filepath, 'wb') as f:
                f.write(datafile.read())
            task_id = async_task(upload_node_func, roadnetwork, filepath,
                                 hook=str_hook)
            description = 'Importing nodes'
            db_task = BackgroundTask(project=roadnetwork.project, id=task_id,
                                     description=description,
                                     road_network=roadnetwork)
            db_task.save()
            messages.success(request, "Task successfully started.")
        else:
            messages.error(
                request, "Invalid request. Did you upload the file correctly?")
        return redirect('road_network_details', roadnetwork.pk)
    else:
        form = NodeForm()
        return render(request, template, {'form': form})


def upload_zone(request, pk):
    template = "zone_set/zone.html"
    zoneset = get_object_or_404(ZoneSet, pk=pk)
    if zoneset.zone_set.all().exists():
        messages.warning(request, "The zone set already contains data")
        return redirect('zoneset_details', pk)
    if BackgroundTask.objects.filter(
            zoneset_set=zoneset, status=BackgroundTask.INPROGRESS
    ).exists():
        messages.warning(
            request, "A task is in progress for this zone set.")
        return redirect('zoneset_details', pk)

    if request.method == 'POST':
        # File must be included when creating the form
        form = ZoneFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Getting data from the fielfield input
            datafile = request.FILES['my_file']

            # Save file on disk (we cannot send large files as arguments of
            # async tasks).
            filename = '{}-{}'.format(uuid.uuid4(), datafile.name)
            filepath = os.path.join(settings.MEDIA_ROOT, filename)
            with open(filepath, 'wb') as f:
                f.write(datafile.read())
            task_id = async_task(async_task_for_zone_set_file, zoneset,
                                 filepath, hook=str_hook)
            description = "Importing zones"
            db_task = BackgroundTask(
                project=zoneset.project,
                id=task_id,
                description=description,
                zoneset_set=zoneset
            )
            db_task.save()
            messages.success(request, "Task successfully started")
        else:
            messages.error(
                request, "Invalid request. Did you upload the file correctly?")
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
