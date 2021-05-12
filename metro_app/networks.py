from django.contrib import messages
from django.contrib.gis.geos import fromstr
from django.contrib.gis.geos import GEOSGeometry, LineString, Point
from django.core.serializers import serialize
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from .forms import NodeForm, EdgeForm
from .models import Node, Edge, RoadNetWork, RoadType
import csv
import io
import json
from shapely import geometry
from shapely.geometry import mapping, shape
from shapely.ops import split
from django_pandas.io import read_frame
import psycopg2
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pyproj import CRS
import networkx as nx
import folium
import datetime
from datetime import datetime
#............................................................................ #
#                   VIEW OF UPLOADING A PROJECT IN THE DATABASE               #
#............................................................................ #

def upload_node(request, pk):
    template = "networks/node.html"
    roadnetwork = RoadNetWork.objects.get(id=pk)
    node_instance = Node.objects.filter(network_id=pk)
    if node_instance.count()>0:
        messages.warning(request, "Fail ! Network contains already nodes data.")
        return redirect('network_details', roadnetwork.pk )

    if request.method == 'POST':
        # We need to include the files when creating the form
        form = NodeForm(request.POST, request.FILES)
        if form.is_valid():
            # Getting data from the fielfield input
            datafile = request.FILES['my_file']
            objects = json.load(datafile)
            L=[]
            for object in objects['features']:
                objet_type = object['geometry']['type']
                if objet_type == 'Point':
                    properties = object['properties']
                    geometry = object['geometry']
                    node_id = properties['id']
                    name = properties.get('name','No name')
                    lon = geometry['coordinates'][0]
                    lat = geometry['coordinates'][1]
                    #location = geometry['coordinates']
                    location = fromstr(f'POINT({lon} {lat})', srid=4326)
                    node = Node(node_id=node_id, name=name,
                                location=location, network=roadnetwork)
                    L.append(node)
            Node.objects.bulk_create(L)
            messages.success(request, 'Your node file has beeb successfully imported !')

        return redirect('network_details', roadnetwork.pk )
    else:
        form = NodeForm()
        return render(request, template, {'form': form})

def upload_edge(request, pk):
    print("Executed at ", datetime.now())
    t1 = datetime.now()
    template = "networks/edge.html"
    roadnetwork = RoadNetWork.objects.get(id=pk)
    road_type = RoadType.objects.get(pk=2)
    node_instance = Node.objects.filter(network_id=pk)
    edge_instance = Edge.objects.filter(network_id=pk)

    if edge_instance.count()>0:
        messages.warning(request, "Fail ! Network contains already edges data.")
        return redirect('network_details', roadnetwork.pk )

    if request.method == 'POST':
        form = EdgeForm(request.POST, request.FILES)
        if form.is_valid():
            datafile = request.FILES['my_file']
            objects = json.load(datafile)
            L=[]
            for object in objects['features']:
                objet_type = object['geometry']['type']
                if objet_type == 'LineString':
                    properties = object['properties']
                    geometry = object['geometry']
                    location = GEOSGeometry(
                        LineString(geometry['coordinates']), srid=4326)

                    target = properties.get('target')
                    source = properties.get('source')
                    name = properties.get('name')

                    try:
                        target = node_instance.get(node_id=target)
                        source = node_instance.get(node_id=source)
                        node = Edge(
                                param1=properties.get('param1', 1.0),
                                param2=properties.get('param2', 0),
                                param3=properties.get('param3', 0),
                                speed=properties.get('speed', 0),
                                length=properties.get('length', 0),
                                lanes=properties.get('lanes', 0),
                                geometry=location,
                                name=properties.get('name', 0),
                                road_type=road_type,
                                target=target,
                                source=source,
                                network=roadnetwork)
                        L.append(node)
                    except ObjectDoesNotExist:
                        pass

        print("Finish at ", datetime.now())
        t2=datetime.now()
        print('delta time is :', t2-t1)
        Edge.objects.bulk_create(L)
        messages.success(request, 'Your edge file has beeb successfully imported !')
        return redirect('home')
    else:
        form = EdgeForm()
        return render(request, template, {'form': form})
"""
def read_from_postgress_old(table_name):
    #network
    #edges = Edge.objects.all()
    #
    conn = psycopg2.connect(database="metro",
                            user="postgres",
                            password="",
                            host="127.0.0.1",
                            port=5433)
    cursor = conn.cursor()
    if table_name == "Edge":
        sql = 'select source_id, target_id, speed, length, lanes, name, geometry as geom from "{}"  where network_id=4'.format(
            table_name)
        cursor.execute(sql)
        gdf = gpd.read_postgis(sql, conn)

    elif table_name == "Node":
        sql = 'select node_id, name, location as geom from "{}" where network_id=4'.format(
            table_name)
        cursor.execute(sql)
        gdf = gpd.read_postgis(sql, conn)
    else:
        print("Table non identifiable")
    return gdf
"""

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
    splitted_polygons = split(polygon, linestring)
    if drive_right:
        # Returns the right-hand side of the split.
        return split(polygon, linestring)[0]
    else:
        # Returns the left-hand side of the split.
        return split(polygon, linestring)[-1]

def make_network_visualization(road_network_id, node_radius=12,
                               node_color='lightgray', edge_width_ratio=1,
                               max_lanes=2):
    """Generates an HTML file with the Leaflet.js representation of a network.

    :param road_network_id: Id of the road network to represent.
    :param node_radius: Radius of the nodes of the road network, in meters. It
       is used only if the road network is not abstract.
    :param node_color: HTML color used to display the nodes of the road
       network.
    :param edge_width_ratio: Width of the edges of the road network, as a share
       of node's diameter.
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
    road_network = RoadNetWork.objects.get(pk=road_network_id)

    degree_crs = "EPSG:4326"
    meter_crs = "EPSG:3857"

    # Retrieve all nodes of the road network as a GeoDataFrame.
    nodes = Node.objects.filter(network=road_network)
    columns = ['id', 'node_id', 'location']
    values = nodes.values_list(*columns)
    nodes_gdf = gpd.GeoDataFrame.from_records(values, columns=columns)
    nodes_gdf['location'] = gpd.GeoSeries.from_wkt(
        nodes_gdf['location'].apply(lambda x: x.wkt), crs=degree_crs)
    nodes_gdf.set_geometry('location', inplace=True)

    # Retrieve all edges of the road network as a GeoDataFrame.
    edges = Edge.objects.filter(network=road_network)
    columns = ['id', 'lanes', 'road_type', 'source', 'target', 'geometry']
    values = edges.values_list(*columns)
    edges_gdf = gpd.GeoDataFrame.from_records(values, columns=columns)

    # Retrieve all road types of the road network as a DataFrame.
    rtypes = RoadType.objects.all()
    # TODO: remove previous line and uncomment the following line once the road
    # types are properly imported.
    #  rtypes = RoadType.objects.filter(network=road_network)
    columns = ['id', 'default_lanes', 'color']
    values = rtypes.values_list(*columns)
    rtypes_df = pd.DataFrame.from_records(values, columns=columns)

    if (rtypes_df['color'] == '').any():
        # Set a default color from a matplotlib colormap.
        cmap = plt.get_cmap('Set1')
        for key, row in rtypes_df.iterrows():
            if not row['color']:
                rtypes_df.loc[key, 'color'] = mcolors.to_hex(cmap(key))

    edges_gdf = edges_gdf.merge(rtypes_df, left_on='road_type', right_on='id')

    # Get the number of lanes for edges with NULL values from the default
    # number of lanes of the corresponding road type.
    edges_gdf.loc[
        edges_gdf['lanes'].isna(),
        'lanes'
    ] = edges_gdf['default_lanes']

    edges_gdf = edges_gdf.set_index(['source', 'target']).sort_index()
    edges_gdf['geometry'] = gpd.GeoSeries.from_wkt(
        edges_gdf['geometry'].apply(lambda x: x.wkt), crs=degree_crs)

    # As node radius and edge width are expressed in meters, we need to convert
    # the geometries in a metric projection.
    edges_gdf.to_crs(crs=meter_crs, inplace=True)
    # Discard NULL geometries.
    edges_gdf = edges_gdf.loc[edges_gdf.geometry.length > 0]

    if road_network.abstract:
        # The node radius is implied from the characteristics of the network,
        # i.e., the more widespread the nodes, the larger the radius.
        node_radius = .1 * edges_gdf.geometry.length.min()

    # Adjust the max_lanes value if it is larger than the maximum number of
    # lanes in the edges of the road network.
    max_lanes = min(max_lanes, edges_gdf['lanes'].max())
    # Compute the width of a edge which has max_lanes lanes.
    max_width = edge_width_ratio * node_radius / 2
    # Constrain edge width by bounding the number of lanes of the edges.
    edges_gdf['lanes'] = np.minimum(max_lanes, edges_gdf['lanes'])
    # The width of the edges is proportional to their number of lanes.
    edges_gdf['width'] = max_width * edges_gdf['lanes'] / max_lanes

    # Identify oneway edges.
    edges_gdf['oneway'] = True
    keys = set()
    for key in edges_gdf.index:
        if key[::-1] in keys:
            edges_gdf.loc[key, 'oneway'] = False
            edges_gdf.loc[key[::-1], 'oneway'] = False
        else:
            keys.add(key)

    drive_right = True
    # TODO: remove previous line and uncomment the following line once the
    # drive_right attribute of road networks is added.
    #  drive_right = road_network.drive_right

    # Replace the geometry of the edges with an offset polygon of corresponding
    # width.
    col_list = ['geometry', 'oneway', 'width']
    edges_gdf['geometry'] = edges_gdf[col_list].apply(
        lambda row: get_offset_polygon(
            linestring=row['geometry'],
            width=row['width'],
            drive_right=drive_right,
            oneway=row['oneway']
        ),
        axis=1,
    )

    # Convert back to the CRS84 projection, required by Folium.
    edges_gdf.to_crs(crs=degree_crs, inplace=True)

    # Initialize the map
    tiles_layer = None if road_network.abstract else 'OpenStreetMap'
    m = folium.Map(max_zoom=19, prefer_canvas=True, tiles=tiles_layer)

    def style_function(feature):
        """Function defining the style of the edges."""
        return dict(
            color='black',
            weight=.1,
            fillColor=feature['properties']['color'],
            fillOpacity=.8,
        )

    def highlight_function(feature):
        """Function defining the style of the edges on mouse hover."""
        return dict(
            color='red',
            weight=.1,
            fillColor='yellow',
            fillOpacity=.8,
        )

    # Add the representation of the edges.
    edges_gdf.drop(
        columns=['lanes', 'road_type', 'default_lanes', 'width'], inplace=True)
    layer = folium.GeoJson(
        edges_gdf,
        style_function=style_function,
        highlight_function=highlight_function,
        smooth_factor=1,
        name='Roads'
    ).add_to(m)

    # Create a FeatureGroup that will hold all the nodes.
    node_group = folium.FeatureGroup(name='Intersections')
    m.add_child(node_group)

    # Add the representation of the nodes.
    for lon, lat in zip(nodes_gdf.geometry.x, nodes_gdf.geometry.y):
        folium.Circle(
            location=[lat, lon], color=node_color, opacity=1, fill=True,
            fill_opacity=.8, radius=node_radius,
        ).add_to(node_group)

    # Add a LayerControl to toggle FeatureGroups.
    folium.LayerControl(position='topright').add_to(m)

    # Bound the map such that the network is centered and entirely visible.
    m.fit_bounds(layer.get_bounds())

    m.save('templates/visualization/visualization.html')
