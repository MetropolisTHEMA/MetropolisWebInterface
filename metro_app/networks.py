from django.http import HttpResponse
from django.contrib import messages
from django.contrib.gis.geos import fromstr
from django.contrib.gis.geos import GEOSGeometry, LineString, Polygon
from django.core.files.storage import default_storage
from shapely import geometry as geom
from django.shortcuts import render, redirect, get_object_or_404
import json
import csv
import uuid
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from shapely.ops import split
from .forms import (NodeForm, EdgeForm,
                    RoadTypeFileForm, ZoneFileForm, ODPairFileForm,)
from .models import (Node, Edge, RoadNetwork, RoadType, ZoneSet, Zone,
                     ODPair, ODMatrix, BackgroundTask)
from .hooks import str_hook
from django.db.utils import IntegrityError
import os
from django.conf import settings
from django_q.tasks import async_task


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


def get_network_directory(roadnetwork):
    return os.path.join(
        settings.BASE_DIR, 'visualization', str(roadnetwork.id))

# ............................................................................#
#                   VIEW OF UPLOADING A PROJECT IN THE DATABASE               #
# ............................................................................#


def upload_road_type(request, pk):
    template = "networks/roadtype.html"
    roadnetwork = RoadNetwork.objects.get(id=pk)
    roadtypes = RoadType.objects.select_related(
        'network').filter(network_id=pk)

    if roadtypes.count() > 0:
        messages.warning(request, "Fail ! Network contains \
                            already road type data.")
        return redirect('network_details', roadnetwork.pk)

    list_roadtype_instance = []
    if request.method == 'POST':
        form = RoadTypeFileForm(request.POST, request.FILES)
        if form.is_valid():
            datafile = request.FILES['my_file']
            if datafile.name.endswith('.csv'):
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
                            default_param1=row.get('default_param1', None),
                            default_param2=row.get('default_param2', None),
                            default_param3=row.get('default_param3', None),
                            color=row.get('color', None),
                            network=roadnetwork)

                    list_roadtype_instance.append(roadtype)
            else:
                messages.error(request, 'You file does not respect Metropolis \
                                format guidelines')
                return render(request, template, {'form': form})
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

            if roadtypes.count() > 0:
                messages.success(request, 'Your road type file has been \
                                 successfully imported !')
            return redirect('network_details', roadnetwork.pk)

    else:
        form = RoadTypeFileForm()
        return render(request, template, {'form': form})


def upload_node_func(roadnetwork, filepath):
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
            return 'Cannot read file.\n\nError message:\n{}'.format(e)

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
        gdf['geometry'] = gdf.apply(
            lambda row: geom.Point([row['x'], row['y']]), axis=1)

    message = ''
    invalids = gdf.geom_type != 'Point'
    if invalids.any():
        message += (
            'Discarding {} invalid geometries (only Points are allowed).\n'
        ).format(invalids.sum())
        gdf = gdf.loc[~invalids]

    if not len(gdf):
        message += 'No valid node to import.\n'
        return message

    if gdf['id'].nunique() != len(gdf):
        counts = gdf['id'].value_counts()
        duplicates = counts.loc[counts > 1].index.astype(str)
        message += (
            'Duplicate node ids (only the last one is imported): {}\n'
        ).format(', '.join(duplicates))
        gdf = gdf.groupby('id').last()
    else:
        gdf.set_index('id', inplace=True)

    gdf['gis-geometry'] = gdf['geometry'].apply(lambda g: GEOSGeometry(str(g)))
    nodes_to_import = list()
    invalid_nodes = list()
    def handle_nan(value):
        if value and np.isnan(value):
            return None
        else:
            return value
    for node_id, row in gdf.iterrows():
        try:
            node = Node(
                node_id=node_id,
                network=roadnetwork,
                location=row['gis-geometry'],
                name=row.get('name', ''),
            )
        except Exception as e:
            invalid_nodes.append(str(node_id))
        else:
            nodes_to_import.append(node)
    if invalid_nodes:
        message += (
            'The following nodes could not be imported correctly: {}\n'
        ).format(', '.join(invalid_nodes))

    if not nodes_to_import:
        message += 'No node were imported.\n'
        return message

    # Create the edges in bulk.
    try:
        Node.objects.bulk_create(nodes_to_import)
    except Exception as e:
        message += (
            'Failed to import nodes.\n\nError message:\n{}'
        ).format(e)
        return message

    message += 'Successfully imported {} nodes.'.format(
        len(nodes_to_import))
    return message


def upload_node(request, pk):
    template = "networks/node.html"
    roadnetwork = get_object_or_404(RoadNetwork, pk=pk)
    if Node.objects.filter(network_id=pk).exists():
        messages.warning(request, "The road network already contains nodes.")
        return redirect('network_details', roadnetwork.pk)
    if BackgroundTask.objects.filter(
            road_network=roadnetwork, status=BackgroundTask.INPROGRESS
    ).exists():
        messages.warning(
            request, "A task is in progress for this road network.")
        return redirect('network_details', roadnetwork.pk)
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
        return redirect('network_details', roadnetwork.pk)
    else:
        form = NodeForm()
        return render(request, template, {'form': form})


def upload_edge_func(roadnetwork, filepath):
    # Read file with GeoPandas.
    dtype = {'id': int, 'source': int, 'target': int, 'road_type': int,
             'length': float}
    try:
        gdf = gpd.read_file(filepath, dtype=dtype)
        for col, typ in dtype.items():
            gdf[col] = gdf[col].astype(typ)
    except Exception as e:
        try:
            df = pd.read_csv(filepath, dtype=dtype)
            df['geometry'] = None
            gdf = gpd.GeoDataFrame(df)
            del df
        except Exception as e1:
            return 'Cannot read file.\n\nError message:\n{}'.format(e)

    # Check that all mandatory keys are here.
    if not all(key in gdf.columns for key in dtype.keys()):
        return (
            'Cannot import file.\n\nError message:\nThe following fields'
            ' are mandatory: {}'
        ).format(', '.join(keys))

    message = ''
    # Merge with source and target nodes.
    nodes = Node.objects.filter(network=roadnetwork).values(
        'id', 'node_id', 'location')
    nodes_df = pd.DataFrame(nodes)
    gdf = gdf.merge(nodes_df, left_on='source', right_on='node_id', how='left',
                    suffixes=('', '_source'))
    gdf.rename(columns={'location': 'location_source'}, inplace=True)
    gdf = gdf.merge(nodes_df, left_on='target', right_on='node_id', how='left',
                    suffixes=('', '_target'))
    gdf.rename(columns={'location': 'location_target'}, inplace=True)
    # Check if some sources or targets are invalid.
    invalids = gdf['id_source'].isnull()
    if invalids.any():
        invalid_source_ids = gdf.loc[invalids, 'source'].unique().astype(str)
        message += 'Invalid source ids: {}\n'.format(
            ', '.join(invalid_source_ids))
        gdf = gdf.loc[~invalids]
    invalids = gdf['id_target'].isnull()
    if invalids.any():
        invalid_target_ids = gdf.loc[invalids, 'target'].unique().astype(str)
        message += 'Invalid target ids: {}\n'.format(
            ', '.join(invalid_target_ids))
        gdf = gdf.loc[~invalids]

    if len(gdf) and gdf.geom_type.isnull().all():
        # The edges have no geometry (the file is probably as CSV).
        # We create the geometries from the nodes.
        message += 'Creating edge geometries from the node coordinates.\n'
        gdf['geometry'] = gdf.apply(
            lambda row: geom.LineString(
                [row['location_source'], row['location_target']]),
            axis=1)

    invalids = gdf.geom_type != 'LineString'
    if invalids.any():
        message += (
            'Discarding {} invalid geometries (only LineStrings are allowed).'
            '\n'
        ).format(invalids.sum())
        gdf = gdf.loc[~invalids]

    if not len(gdf):
        message += 'No valid edge to import.\n'
        return message

    # Merge with road types.
    roadtypes = RoadType.objects.filter(network=roadnetwork).values(
        'id', 'road_type_id')
    roadtype_df = pd.DataFrame(roadtypes)
    gdf = gdf.merge(
        roadtype_df, left_on='road_type', right_on='road_type_id', how='left',
        suffixes=('', '_roadtype'))
    invalid_roadtype_ids = set()
    # Check if some roadtypes are invalid.
    invalids = gdf['road_type_id'].isnull()
    if invalids.any():
        invalid_roadtype_ids = gdf.loc[
            invalids, 'road_type_id'].unique().astype(str)
        message += 'Invalid road type ids: {}\n'.format(
            ', '.join(invalid_roadtype_ids))
        gdf = gdf.loc[~invalids]

    if gdf['id'].nunique() != len(gdf):
        counts = gdf['id'].value_counts()
        duplicates = counts.loc[counts > 1].index.astype(str)
        message += (
            'Duplicate edge ids (only the last one is imported): {}\n'
        ).format(', '.join(duplicates))
        gdf = gdf.groupby('id').last()
    else:
        gdf.set_index('id', inplace=True)

    gdf['gis-geometry'] = gdf['geometry'].apply(lambda g: GEOSGeometry(str(g)))
    edges_to_import = list()
    invalid_edges = list()
    def handle_nan(value):
        if value and np.isnan(value):
            return None
        else:
            return value
    for edge_id, row in gdf.iterrows():
        try:
            edge = Edge(
                edge_id=edge_id,
                network=roadnetwork,
                geometry=row['gis-geometry'],
                length=row['length'],
                road_type_id=row['id_roadtype'],
                source_id=row['id_source'],
                target_id=row['id_target'],
                speed=handle_nan(row.get('speed')),
                lanes=handle_nan(row.get('lanes')),
                name=row.get('name', ''),
                param1=handle_nan(row.get('param1')),
                param2=handle_nan(row.get('param2')),
                param3=handle_nan(row.get('param3')),
            )
        except Exception as e:
            invalid_edges.append(str(edge_id))
        else:
            edges_to_import.append(edge)
    if invalid_edges:
        message += (
            'The following edges could not be imported correctly: {}\n'
        ).format(', '.join(invalid_edges))

    if not edges_to_import:
        message += 'No edge were imported.\n'
        return message

    # Create the edges in bulk.
    try:
        Edge.objects.bulk_create(edges_to_import)
    except Exception as e:
        message += (
            'Failed to import edges.\n\nError message:\n{}'
        ).format(e)
        return message

    message += 'Successfully imported {} edges.'.format(
        len(edges_to_import))
    return message



def upload_edge(request, pk):
    template = "networks/edge.html"
    roadnetwork = get_object_or_404(RoadNetwork, pk=pk)
    if Edge.objects.filter(network_id=pk).exists():
        messages.warning(request, "The road network already contains edges.")
        return redirect('network_details', roadnetwork.pk)
    if (not Node.objects.filter(network_id=pk).exists()
            or not RoadType.objects.filter(network_id=pk).exists()):
        messages.warning(request, "You must import nodes and roadtypes first.")
        return redirect('network_details', roadnetwork.pk)
    if BackgroundTask.objects.filter(
            road_network=roadnetwork, status=BackgroundTask.INPROGRESS
    ).exists():
        messages.warning(
            request, "A task is in progress for this road network.")
        return redirect('network_details', roadnetwork.pk)
    if request.method == 'POST':
        form = EdgeForm(request.POST, request.FILES)
        if form.is_valid():
            datafile = request.FILES['my_file']
            # Save file on disk (we cannot send large files as arguments of
            # async tasks).
            filename = '{}-{}'.format(uuid.uuid4(), datafile.name)
            filepath = os.path.join(settings.MEDIA_ROOT, filename)
            with open(filepath, 'wb') as f:
                f.write(datafile.read())
            task_id = async_task(upload_edge_func, roadnetwork, filepath,
                                 hook=str_hook)
            description = 'Importing edges'
            db_task = BackgroundTask(project=roadnetwork.project, id=task_id,
                                     description=description,
                                     road_network=roadnetwork)
            db_task.save()
            messages.success(request, "Task successfully started.")
        else:
            messages.error(
                request, "Invalid request. Did you upload the file correctly?")
        return redirect('network_details', roadnetwork.pk)
    else:
        form = EdgeForm()
        return render(request, template, {'form': form})


def get_offset_polygon(linestring, width, oneway=True, drive_right=True):
    """Returns a polygon of a given width, representing a road defined by a
    LineString.
    :param linestring: Geometry of the road, in EPSG:3857.
    :param width: Width of the road, in meters.
    :param oneway: If True, the polygon is centered on the linestring. If
       False, the polygon is offset so that there can be two parallel roads.
    :param drive_right: If True, the polygon is offset toward the right, to
       represent right-hand traffic. If False, it is offset toward the left.
       This has no effect if oneway is True.
    :type linestring: shapely.geometry.LineString
    :type width: numeric
    :type oneway: boolean
    :type drive_right: boolean
    :returns: Polygon geometry representing a road.
    :rtype: shapely.geometry.Polygon
    """
    if not oneway:
        # Double the width as the first polygon computed represent the road in
        # both directions.
        width *= 2
    # Compute a polygon from the linestring by increasing its width.
    polygon = linestring.buffer(width, join_style=2, cap_style=2)

    if oneway:
        # The polygon is centered and has the correct width, returns it.
        return polygon
    # Split the polygon in two in the middle (represented by the linestring).
    # splitted_polygons = split(polygon, linestring)
    if drive_right:
        # Returns the right-hand side of the split.
        return split(polygon, linestring)[0]
    else:
        # Returns the left-hand side of the split.
        return split(polygon, linestring)[-1]


def make_network_visualization(road_network_id, node_radius=6, lane_width=6,
                               node_color='lightgray', edge_width_ratio=1,
                               max_lanes=5):
    """Generates an HTML file with the Leaflet.js representation of a network.
    :param road_network_id: Id of the road network to represent.
    :param node_radius: Radius of the nodes of the road network, in meters. It
       is used only if the road network is not simple.
    :param lane_width: Width of a road for each of its lane, in meters. It is
     used only if the road network is not simple.
    :param node_color: HTML color used to display the nodes of the road
       network.
    :param edge_width_ratio: Width of the edges of the road network, as a share
       of node's diameter. It is used only if the road network is simple.
    :param max_lanes: All edges whose number of lanes is greater or equal to
       max_lanes are represented with a width equal to edges_width_ratio *
       node_radius / 2. Edges with a number of lanes smaller than max_lanes
       have a width proportional to their number of lanes.
    :type road_network_id: integer
    :type node_radius: numeric
    :type node_color: str
    :type edge_width_ratio: float
    :type max_lanes: integer
    :returns: Absolute path of the HTML file generated.
    :rtype: str
    """
    roadnetwork = RoadNetwork.objects.get(pk=road_network_id)

    data_crs = "EPSG:{}".format(roadnetwork.srid)
    degree_crs = "EPSG:4326"
    meter_crs = "EPSG:3857"

    # Retrieve all nodes of the road network as a GeoDataFrame.
    nodes = Node.objects.select_related('network').filter(network=roadnetwork)
    columns = ['node_id', 'location']
    values = nodes.values_list(*columns)

    nodes_gdf = gpd.GeoDataFrame.from_records(values, columns=columns)
    # The following line is to OPTIMIZE
    nodes_gdf['location'] = gpd.GeoSeries.from_wkt(
        nodes_gdf['location'].apply(lambda x: x.wkt), crs=data_crs)
    nodes_gdf.set_geometry('location', inplace=True)

    # Retrieve all edges of the road network as a GeoDataFrame.
    edges = Edge.objects.select_related('road_type', 'source',
                                        'target').filter(network=roadnetwork)
    columns = ['edge_id', 'lanes', 'road_type', 'source', 'target', 'geometry']
    values = edges.values_list(*columns)
    edges_df = pd.DataFrame.from_records(values, columns=columns)

    if edges.count() == 0 or nodes.count() == 0:
        return redirect('network_details', roadnetwork.pk)
    else:
        # Retrieve all Road type of a network as DataFrame
        rtypes = RoadType.objects.filter(network=roadnetwork)
        columns = ['id', 'default_lanes', 'color']
        values = rtypes.values_list(*columns)
        rtypes_df = pd.DataFrame.from_records(values, columns=columns)

        if rtypes_df['color'].isna().any():
            # Set a default color from a matplotlib colormap.
            cmap = plt.get_cmap('Set1')
            for key, row in rtypes_df.iterrows():
                if not row['color']:
                    rtypes_df.loc[key, 'color'] = mcolors.to_hex(cmap(key))

        edges_df = edges_df.merge(rtypes_df,
                                  left_on='road_type', right_on='id')
        # Get the number of lanes for edges with NULL values from the default
        # number of lanes of the corresponding road type.
        edges_df.loc[
            edges_df['lanes'].isna(), 'lanes'] = edges_df['default_lanes']
        edges_df.loc[edges_df['lanes'].isna(), 'lanes'] = 1
        edges_df.loc[edges_df['lanes'] <= 0, 'lanes'] = 1

        edges_df['geometry'] = gpd.GeoSeries.from_wkt(
            edges_df['geometry'].apply(lambda x: x.wkt))

        edges_gdf = gpd.GeoDataFrame(edges_df,
                                     geometry='geometry', crs=data_crs)
        # As node radius and edge width are expressed in meters,
        # we need to convert the geometries in a metric projection.
        edges_gdf.to_crs(crs=meter_crs, inplace=True)

        # Discard NULL geometries.
        edges_gdf = edges_gdf.loc[edges_gdf.geometry.length > 0]
        # Adjust the max_lanes value if it is larger than the maximum number of
        # lanes in the edges of the road network.
        max_lanes = min(max_lanes, edges_gdf['lanes'].max())
        # Constrain edge width by bounding the number of lanes of the edges.
        edges_gdf['lanes'] = np.minimum(max_lanes, edges_gdf['lanes'])

        if roadnetwork.simple:
            # The node radius is implied from the characteristics of the
            # network i.e the more widespread the nodes, the larger the radius.
            node_radius = .1 * edges_gdf.geometry.length.min()
            lane_width = node_radius * (edge_width_ratio / 2) / max_lanes

        # The width of the edges is proportional to their number of lanes.
        edges_gdf['width'] = lane_width * edges_gdf['lanes']

        # Identify oneway edges.
        edges_gdf[['source', 'target']] = edges_gdf[
            ['source', 'target']].astype(str)
        edges_gdf['oneway'] = ~(edges_gdf.source + '_' +
                                edges_gdf.target).isin(
                            edges_gdf.target + '_' + edges_gdf.source)

        # Replace the geometry of the edges with an offset polygon of
        # corresponding width. time : +16s
        col_list = ['geometry', 'oneway', 'width']
        edges_gdf['geometry'] = edges_gdf[col_list].apply(
            lambda row: get_offset_polygon(
                linestring=row['geometry'],
                width=row['width'],
                drive_right=True,
                oneway=row['oneway']
            ),
            axis=1,
        )
        edges_gdf = edges_gdf.sort_values(
            by="source", ascending=True, ignore_index=True)

        edges_gdf.drop(
            columns=['source', 'target', 'id', 'road_type', 'lanes',
                     'default_lanes', 'width', 'oneway'], inplace=True)

        # Convert back to the CRS84 projection, required by Folium.
        edges_gdf.to_crs(crs=degree_crs, inplace=True)

        # Create and save edges.geojson file
        directory = get_network_directory(roadnetwork)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        edges_gdf.to_file(
            os.path.join(directory, "edges.geojson"), driver='GeoJSON')


def upload_zone(request, pk):
    template = "networks/zone.html"
    list_zone_instance = []
    zoneset = ZoneSet.objects.get(id=pk)
    if request.method == 'POST':
        # File must be included when creating the form
        form = ZoneFileForm(request.POST, request.FILES)
        if form.is_valid():
            # hey, if form is valid, get me back the data from the input form
            datafile = request.FILES['my_file']  # get by name
            # IF THE FILE UPLOADED IS A GEOJSON EXTENSION
            if datafile.name.endswith('.geojson'):
                objects = json.load(datafile)
                for object in objects['features']:
                    properties = object['properties']
                    geometry = object['geometry']
                    radius = properties.get('radius', 0.00)
                    zone_id = properties['id']
                    name = properties.get('name', 'No name')
                    coordinates = geometry['coordinates']
                    # geometry = GEOSGeometry(Polygon(coordinates,
                    #                                srid=4326))
                    # geometry = Polygon(
                    #    [tuple(l) for l in coordinates[0]], srid=4326)
                    if geometry['type'] == 'Polygon':
                        geometry = Polygon(coordinates[0], srid=4326)
                        centroid = geometry.centroid

                    elif geometry['type'] == 'Point':
                        centroid = fromstr(
                            f'POINT({coordinates[0]} {coordinates[1]})',
                            srid=4326)
                        geometry = None

                    else:
                        message = "Zone don't import the good file!"
                        messages.error(request, message)
                        return redirect('upload_zone', zoneset.pk)

                    zone_instance = Zone(zone_id=zone_id, centroid=centroid,
                                         geometry=geometry, radius=radius,
                                         name=name, zone_set=zoneset)
                    list_zone_instance.append(zone_instance)

                Zone.objects.bulk_create(list_zone_instance)
                return redirect('zoneset_details', zoneset.pk)

            elif datafile.name.endswith('.csv'):
                datafile = datafile.read().decode('utf-8').splitlines()
                datafile = csv.DictReader(datafile)
                for row in datafile:
                    try:
                        lon, lat = row['x'], row['y']
                    except KeyError:
                        message = "Zone don't import the good file!"
                        messages.error(request, message)
                        return redirect('upload_zone', zoneset.pk)
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

                Zone.objects.bulk_create(list_zone_instance)
                if len(list_zone_instance) > 0:
                    message = "Zone file has been successfully imported !"
                    messages.success(request, message)

                return redirect('zoneset_details', zoneset.pk)
        else:
            return HttpResponse('Unknown format')

    else:
        form = ZoneFileForm()
        return render(request, template, {'form': form})


def upoload_od_pair(request, pk):
    template = "networks/od_pair.html"
    od_matrix = ODMatrix.objects.get(id=pk)
    zoneset = od_matrix.zone_set
    zones = Zone.objects.filter(zone_set=zoneset)
    list_od_pair_instance = []
    compteur = 0
    zone_instance_dict = {zone.zone_id: zone for zone in zones}
    if request.method == 'POST':
        form = ODPairFileForm(request.POST, request.FILES)
        if form.is_valid():
            datafile = request.FILES['my_file']
            if datafile.name.endswith('.csv'):
                datafile = datafile.read().decode('utf-8').splitlines()
                datafile = csv.DictReader(datafile)
                for row in datafile:
                    try:
                        origin = zone_instance_dict[int(row['origin'])]
                        destination = zone_instance_dict[
                            int(row['destination'])]
                    except KeyError:
                        compteur = compteur+1
                    else:
                        od_pair_instance = ODPair(
                            origin=origin,
                            destination=destination,
                            size=row['size'],
                            matrix=od_matrix,
                        )
                        list_od_pair_instance.append(od_pair_instance)
                ODPair.objects.bulk_create(list_od_pair_instance)
                if compteur > 0:
                    message = "{} haven't been imported".format(compteur)
                    messages.warning(request, message)
                return redirect('od_matrix_details', od_matrix.pk)

            elif datafile.name.endswith('.tsv'):
                datafile = datafile.read().decode('utf-8').splitlines()
                datafile = csv.DictReader(datafile, delimiter='\t')
                for row in datafile:
                    try:
                        origin = zone_instance_dict[int(row['origin'])]
                        destination = zone_instance_dict[
                            int(row['destination'])]
                    except KeyError:
                        compteur = compteur+1
                    else:
                        od_pair_instance = ODPair(
                            origin=origin,
                            destination=destination,
                            size=row['size'],
                            matrix=od_matrix,
                        )
                        list_od_pair_instance.append(od_pair_instance)
                ODPair.objects.bulk_create(list_od_pair_instance)
                message = "Your ODPair file has been successfully imported !"
                messages.success(request, message)
                print(compteur)
                if compteur > 0:
                    message = "{} haven't been imported".format(compteur)
                    messages.warning(request, message)
                return redirect('od_matrix_details', od_matrix.pk)
            else:
                messages.error(request, "Uploaded file format \
                                 not recongnized")
                return redirect('upoload_od_pair', od_matrix.pk)
    else:
        form = ODPairFileForm()
        return render(request, template, {'form': form})
