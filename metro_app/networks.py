from django.contrib import messages
from django.contrib.gis.geos import fromstr
from django.contrib.gis.geos import GEOSGeometry, LineString
from shapely import geometry as geom
from django.shortcuts import render, redirect
import json
import csv
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from shapely.ops import split
from .forms import NodeForm, EdgeForm, RoadTypeFileForm
from .models import Node, Edge, RoadNetwork, RoadType
from django.db.utils import IntegrityError
import os
from django.conf import settings


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


def upload_node(request, pk):
    template = "networks/node.html"
    roadnetwork = RoadNetwork.objects.get(id=pk)
    nodes = Node.objects.select_related('network').filter(network_id=pk)
    list_node_instance = []
    if nodes.count() > 0:
        messages.warning(request, "Fail ! Network contains\
                        already nodes data.")
        return redirect('network_details', roadnetwork.pk)

    form = NodeForm()
    if request.method == 'POST':
        # We need to include the files when creating the form
        form = NodeForm(request.POST, request.FILES)
        if form.is_valid():
            # Getting data from the fielfield input
            datafile = request.FILES['my_file']

            # IF THE FILE UPLOADED IS A GEOJSON EXTENSION
            if datafile.name.endswith('.geojson'):
                objects = json.load(datafile)
                for object in objects['features']:
                    objet_type = object['geometry']['type']
                    if objet_type == 'Point':
                        properties = object['properties']
                        geometry = object['geometry']
                        node_id = properties['id']
                        name = properties.get('name', 'No name')
                        lon = geometry['coordinates'][0]
                        lat = geometry['coordinates'][1]
                        location = fromstr(f'POINT({lon} {lat})', srid=4326)
                        node = Node(node_id=node_id, name=name,
                                    location=location, network=roadnetwork)
                        list_node_instance.append(node)
                    else:
                        messages.error(request, "The uploaded file is not the \
                                      node one, please select the good one ! ")
                        return render(request, template, {'form': form})

            elif datafile.name.endswith('.csv'):  # A CSV EXTENSION
                datafile = datafile.read().decode('utf-8').splitlines()
                datafile = csv.DictReader(datafile)
                for row in datafile:
                    lon, lat = row['x'], row['y']
                    location = fromstr(f'POINT({lon} {lat})', srid=4326)
                    node = Node(node_id=row['id'], name=row.get('name', ''),
                                location=location, network=roadnetwork)
                    list_node_instance.append(node)
            else:
                messages.error(request, 'You file does not respect Metropolis \
                                format guidelines')
                return render(request, template, {'form': form})

            Node.objects.bulk_create(list_node_instance)
            if nodes.count() > 0:
                messages.success(request, 'Your node file has been \
                             successfully imported !')
        return redirect('network_details', roadnetwork.pk)
    else:
        return render(request, template, {'form': form})


def upload_edge(request, pk):
    template = "networks/edge.html"
    roadnetwork = RoadNetwork.objects.get(id=pk)
    roadtypes = RoadType.objects.select_related('network').filter(
                                                             network_id=pk)
    nodes = Node.objects.select_related('network').filter(network_id=pk)
    edges = Edge.objects.select_related().filter(network_id=pk)
    node_id_dict = {node.node_id: node for node in nodes}
    road_type_id_dict = {roadtype.road_type_id: roadtype
                         for roadtype in roadtypes}
    list_edge_instance = []
    if edges.count() > 0:
        messages.warning(request, "Fail ! Network contains \
                            already edges data.")
        return redirect('network_details', roadnetwork.pk)

    if nodes.count() == 0 or roadtypes.count() == 0:
        messages.warning(request, "Fail ! First import node or road type file \
                            before importing edge.")
        return redirect('network_details', roadnetwork.pk)
    form = EdgeForm()
    if request.method == 'POST':
        form = EdgeForm(request.POST, request.FILES)
        if form.is_valid():
            datafile = request.FILES['my_file']
            if datafile.name.endswith('.geojson'):
                objects = json.load(datafile)

            elif datafile.name.endswith('.csv'):
                edges = pd.read_csv(datafile,)
                nodes = Node.objects.filter(network_id=pk).values()
                nodes = pd.DataFrame(nodes)
                # merge origin coordonates
                edges = edges.merge(nodes[['node_id', 'location']],
                                    left_on='source', right_on='node_id')

                # merge destination coordinates
                edges = edges.merge(
                    nodes[['node_id', 'location']], left_on='target',
                    right_on='node_id')
                edges['geometry'] = edges.apply(lambda x:
                                                [x['location_x'],
                                                 x['location_y']], axis=1)
                edges.drop(['node_id_x', 'node_id_y', 'location_x',
                            'location_y'], axis=1, inplace=True)
                edges['geometry'] = edges['geometry'].apply(geom.LineString)
                edges = gpd.GeoDataFrame(edges)
                datafile = edges.to_json()
                objects = json.loads(datafile)

            else:
                messages.error(request, "You file does not respect Metropolis \
                                format guidelines")
                return render(request, template, {'form': form})

            for object in objects['features']:
                objet_type = object['geometry']['type']
                if objet_type == 'LineString':
                    properties = object['properties']
                    geometry = object['geometry']
                    location = GEOSGeometry(
                        LineString(geometry['coordinates']), srid=4326)

                    target = properties.get('target')
                    source = properties.get('source')
                    road_type = properties.get('road_type')
                    try:
                        target = node_id_dict[target]
                        source = node_id_dict[source]
                        roadtype = road_type_id_dict[road_type]
                    except KeyError:
                        pass
                        # messages.error(request, "There is a problem at this \
                        #               source_id {}, target_id {} and \
                        #               roadtype_id {}".format(source,
                        #                                    target, roadtype))
                        # return render(request, template, {'form': form})
                    else:
                        edge = Edge(
                                edge_id=properties['id'],
                                param1=properties.get('param1', None),
                                param2=properties.get('param2', None),
                                param3=properties.get('param3', None),
                                speed=properties.get('speed', None),
                                length=properties['length'],
                                lanes=properties.get('lanes', None),
                                geometry=location,
                                name=properties.get('name', ''),
                                road_type=roadtype,
                                target=target,
                                source=source,
                                network=roadnetwork)
                        list_edge_instance.append(edge)
                else:
                    messages.error(request, "The uploaded file is not \
                                   the edge one, please select the good one !")
                    return render(request, template, {'form': form})

            Edge.objects.bulk_create(list_edge_instance)

            if list_edge_instance:
                messages.success(request, 'Your edge file has been \
                             successfully imported !')

        return redirect('network_details', roadnetwork.pk)
    else:
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
        edges_gdf['oneway'] = (edges_gdf.source + '_' + edges_gdf.target).isin(
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
        directory = os.path.join(
            settings.TEMPLATES[0]['DIRS'][0],
            'visualization') + "/" + roadnetwork.name
        os.makedirs(directory)
        edges_gdf.to_file(directory + "/edges.geojson", driver='GeoJSON')
