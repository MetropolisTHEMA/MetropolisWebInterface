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
from django_pandas.io import read_frame
import psycopg2
import pandas as pd
import geopandas as gpd
import matplotlib
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
    node_instance = Node.objects.filter(network_id=pk).select_related()

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

def retrieve_data_from_postgres(network_id, Simple,
                          set_initial_crs=4326,
                          zone_radius=15,
                          intersection_radius_percentage=0.8,
                          distance_offset_percentage=0.8,
                          line_color='orange',
                          link_side='left',

                          ):
    initial_crs = "EPSG:{}".format(set_initial_crs)
    initial_crs = CRS(initial_crs)
    CRS84 = "EPSG:4326"
    default_crs = "EPSG:3857"

    edges = Edge.objects.filter(network_id=network_id)
    edges = serialize('geojson', edges,
        fields=('id', 'param1', 'param2', 'param3', 'speed', 'length',
        'lanes','geometry', 'name', 'source', 'target','network', 'road_type'))

    edges = json.loads(edges)
    edges_gdf = gpd.GeoDataFrame.from_features(edges['features']) # Convert a geojson as geodataframe

    nodes = Node.objects.filter(network_id=network_id).values()
    nodes_df = pd.DataFrame(nodes)
    nodes_df['location'] = nodes_df['location'].apply(geometry.Point)
    nodes_gdf = gpd.GeoDataFrame(nodes_df, geometry=nodes_df['location'])


    # Split street network caracteristics like Circular City (Simple=True) and
    # others huge one (Simple=False)
    if Simple:
        edges_gdf.set_crs(CRS84, inplace=True)
        nodes_gdf.set_crs(CRS84, inplace=True)
        intersection_radius = min(edges_gdf.geometry.length) * 0.1 # output is a degree value which we will convert to meter in next line
        intersection_radius = intersection_radius * 111.11 * 1000 # applying a formula which convert degree to meter (regle de trois)
        zone_radius = intersection_radius / intersection_radius_percentage # zone_radius and intersection_radius are dependents
        distance_offset = distance_offset_percentage * intersection_radius # # distance_offset depends on intersection_radius (meter)
        tiles_layer = None
    else:
        edges_gdf.set_crs(initial_crs, inplace=True)
        nodes_gdf.set_crs(initial_crs, inplace=True)
        nodes_gdf.to_crs(CRS84, inplace=True)
        edges_gdf = edges_gdf[edges_gdf.geometry.length > 0]
        zone_radius = zone_radius
        intersection_radius = intersection_radius_percentage * zone_radius
        distance_offset = distance_offset_percentage * zone_radius
        tiles_layer = 'OpenStreetMap'

    edges_gdf["oneway"] = edges_gdf.apply(lambda x: not edges_gdf[
            (edges_gdf["source"] == x["target"]) &
            (edges_gdf["target"] == x["source"])
            & (edges_gdf.index != x.name)].empty, axis=1)

    # On convertit en metre (m) avant d'appliquer le décalage afin
    # d'uniformiser car parallel_offset se calcule en (m)
    edges_gdf.to_crs(crs=default_crs, inplace=True)

    col_list = ['geometry', 'oneway']
    edges_gdf['_offset_geometry_'] = edges_gdf[col_list].apply(
        lambda x: x['geometry'].parallel_offset(
            distance_offset, link_side) if not x['oneway']
        else x['geometry'].parallel_offset(0, link_side),
        axis=1)

    edges_gdf.drop('geometry', axis=1, inplace=True)
    edges_gdf.set_geometry('_offset_geometry_', inplace=True)
    edges_gdf.to_crs(crs=CRS84, inplace=True) # Converting back in 4326 before ploting

    latitudes = list(nodes_gdf['geometry'].y)
    longitudes = list(nodes_gdf['geometry'].x)

    # Initialize the map
    m = folium.Map(location=[latitudes[0], longitudes[0]],
                   max_zoom=18, prefer_canvas=True, tiles=tiles_layer)

    layer=folium.GeoJson(
        edges_gdf,
        tooltip=folium.GeoJsonTooltip(fields=['oneway','lanes',
        'length','speed','name'],localize=True),
        style_function=lambda x: {'color': line_color}).add_to(m)

    # Bounding box the map such that the network is entirely center and visible
    m.fit_bounds(layer.get_bounds())

    # Adding the nodes points
    for lat, long in list(zip(latitudes, longitudes)):
        folium.Circle(location=[lat, long], color='cyan', fill=True,
            fill_opacity=1,radius=intersection_radius).add_to(m)

    m.save('templates/visualization/visualization.html')
