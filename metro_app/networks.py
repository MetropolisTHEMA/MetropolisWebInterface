from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import NodeForm, EdgeForm
from .models import Node, Edge
import csv
import io
import json
from django.contrib.gis.geos import fromstr
from django.contrib.gis.geos import GEOSGeometry, LineString
import psycopg2
import pandas
import geopandas as gpd
import matplotlib
from pyproj import CRS
import networkx as nx
#............................................................................ #
#                   VIEW OF UPLOADING A PROJECT IN THE DATABASE               #
#............................................................................ #
"""
def upload_node(request):
    template = 'upload.html'
    if request.method =='POST':
        datafile = request.FILES['my_file']
        datafile = pd.read_csv(datafile)
        # location = fromstr(f'POINT({longitude} {latitude})', srid=4326)
        location = gpd.points_from_xy(datafile.x, datafile.y)
        datafile = gpd.GeoDataFrame(datafile, geometry=location)
        datafile=datafile.to_dict()
        print(datafile)
"""


def file_process(filename):
    objects = json.load(filename)
    if filename.endswith('.geojson'):
        for object in objects['features']:
            try:
                objet_type = object['geometry']['type']
                if objet_type == 'Point':
                    properties = object['properties']
                    geometry = object['geometry']

                    # Get models's variables values.
                    node_id = properties.get('id')
                    name = properties['name']
                    lat = geometry['coordinates'][0]
                    lon = geometry['coordinates'][1]
                    #location = geometry['coordinates']
                    location = fromstr(f'POINT({lon} {lat})')

            except KeyError:
                pass
        return (node_id, name, location)

# bulk_create, bulk_update


def upload_node(request):
    template = "node.html"
    if request.method == 'POST':
        # We need to include the files when creating the form
        form = NodeForm(request.POST, request.FILES)
        if form.is_valid():
            network = form.cleaned_data['network']
            # Getting data from the fielfield input
            datafile = request.FILES['my_file']
            objects = json.load(datafile)
            for object in objects['features']:
                objet_type = object['geometry']['type']
                if objet_type == 'Point':
                    properties = object['properties']
                    geometry = object['geometry']

                    # Get models's variables values.
                    node_id = properties.get('id')
                    name = properties['name']
                    lat = geometry['coordinates'][0]
                    lon = geometry['coordinates'][1]
                    #location = geometry['coordinates']
                    location = fromstr(f'POINT({lon} {lat})')
                    Node(
                        node_id=node_id,
                        name=name,
                        location=location,
                        network=network
                    ).save()
        return redirect('home')
    else:
        form = NodeForm()
        return render(request, template, {'form': form})


def upload_edge(request):
    template = "edge.html"
    if request.method == 'POST':
        # We need to include the files when creating the form
        form = EdgeForm(request.POST, request.FILES)
        if form.is_valid():
            road_type = form.cleaned_data['road_type']
            target = form.cleaned_data['target']
            source = form.cleaned_data['source']
            network = form.cleaned_data['network']
            # Getting data from the fielfield input
            datafile = request.FILES['my_file']
            objects = json.load(datafile)
            for object in objects['features']:
                objet_type = object['geometry']['type']
                if objet_type == 'LineString':
                    properties = object['properties']
                    geometry = object['geometry']
                    point1 = geometry['coordinates'][0]
                    point2 = geometry['coordinates'][1]
                    location = GEOSGeometry(
                        LineString(geometry['coordinates']))
                    Edge(
                        param1=properties.get('param1', 1.0),
                        param2=properties.get('param2', 0),
                        param3=properties.get('param3', 0),
                        speed=properties.get('speed', 0),
                        lenth=properties.get('lenth', 0),
                        lanes=properties.get('lanes', 0),
                        geometry=location,
                        name=properties.get('name', 0),
                        road_type=road_type,
                        target=target,
                        source=source,
                        network=network
                    ).save()
        return redirect('home')
    else:
        form = EdgeForm()
        return render(request, template, {'form': form})


def read_from_postgres(table_name):
    if table_name == "Edges":
        conn = psycopg2.connect(database="postgres",
                                user="postgres",
                                password="",
                                host="127.0.0.1",
                                port=5433)
        cursor = conn.cursor()
        sql = 'select speed, lenth, lanes, name, geometry as geom from "{}"'.format(
            table_name)
        cursor.execute(sql)
        gdf = gpd.read_postgis(sql, conn)
        return gdf


def network_from_postgres(Simple,
                          set_initial_crs,
                          zone_radius=15,
                          intersection_radius_percentage=0.8,
                          distance_offset_percentage=0.8,
                          line_color='orange',
                          link_side='right'
                          ):
    initial_crs = "EPSG:{}".format(set_initial_crs)
    initial_crs = CRS(initial_crs)
    convert_to_crs = "EPSG:4326"
    default_crs = "EPSG:3857"

    edges_gdf = read_from_postgres("Edges")

    # Convert a GeoDataFrame to a Graph
    G = nx.from_pandas_edgelist(edges_gdf, 'origin', 'destination',
                                ['key', 'id_edge', 'name', 'lanes', 'length',
                                 'speed', 'capacity', 'function', 'geometry'],
                                create_using=nx.MultiDiGraph())

    # Add oneway column (it is a boolean column)
    for u, v, d in G.edges(keys=False, data=True):
        if G.has_edge(v, u):
            G.edges[u, v, 0]['oneway'] = False
        else:
            G.edges[u, v, 0]['oneway'] = True

    df_graph_to_pandas = nx.to_pandas_edgelist(
        G, source='origin', target='destination')
    df_all_roads = df_graph_to_pandas.copy()
    df_all_roads = gpd.GeoDataFrame(df_all_roads, crs=set_initial_crs)

    # We convert to meters (m) before applying the offset in order to have the
    # same unit
    df_all_roads.to_crs(crs=default_crs, inplace=True)

    # Let's define the parallel offset GeoSerie
    df_all_roads['_offset_geometry_'] = df_all_roads[['geometry', 'oneway']].apply(
        lambda x: x['geometry'].parallel_offset(distance_offset, link_side) if not
        x['oneway'] else x['geometry'].parallel_offset(0, link_side), axis=1)

    # Drop the old geometry and replace it by __offset_geometry_
    df_all_roads.drop('geometry', axis=1, inplace=True)
    gdf_all_roads = gpd.GeoDataFrame(
        df_all_roads,
        geometry='_offset_geometry_',
        crs=default_crs)

    gdf_all_roads.to_crs(crs=convert_to_crs, inplace=True)

    # Ploting the network

    # Initialize the map
    m = folium.Map(
        location=[
            latitudes[0],
            longitudes[0]],
        max_zoom=18,
        prefer_canvas=True,
        tiles=tiles_layer)

    # Create a GeoJson onject and display the street network
    layer = folium.GeoJson(
        gdf_all_roads,
        tooltip=folium.GeoJsonTooltip(
            fields=[
                'oneway',
                'id_edge',
                'lanes',
                'length',
                'speed',
                'capacity'],
            localize=True),
        style_function=lambda x: {
            'color': line_color,
            'dashArray': '5, 5' if x['properties']['function'] == 1 else '5, 1'}).add_to(m)

    # Bounding box the map such that the network is entirely center and visible
    m.fit_bounds(layer.get_bounds())
    m.save('templates/__network__.html')


def network_visualization(request):
    network_from_postgres(False, 27561)
    return render(request, '__network.html__')
