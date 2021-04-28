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
import folium
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
            #target = form.cleaned_data['target']
            #source = form.cleaned_data['source']
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

                    target = properties.get('target')
                    source = properties.get('source')
                    name = properties.get('name')
                    try:
                        target_node_instance = Node.objects.get(node_id=target)
                        source_node_instance = Node.objects.get(node_id=source)
                        target = Node.objects.get(
                            network_id=target_node_instance.network_id,
                            node_id=target_node_instance.node_id)
                        source = Node.objects.get(
                            network_id=source_node_instance.network_id,
                            node_id=source_node_instance.node_id)
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

                    except BaseException:
                        pass  # Do something later

        return redirect('home')
    else:
        form = EdgeForm()
        return render(request, template, {'form': form})


def read_from_postgres(table_name):
    conn = psycopg2.connect(database="metroweb",
                            user="postgres",
                            password="",
                            host="127.0.0.1",
                            port=5433)
    cursor = conn.cursor()
    if table_name == "Edge":
        sql = 'select source_id, target_id, speed, lenth, lanes, name, geometry as geom from "{}"'.format(
            table_name)
        cursor.execute(sql)
        gdf = gpd.read_postgis(sql, conn)

    elif table_name == "Node":
        sql = 'select node_id, name, location as geom from "{}"'.format(
            table_name)
        cursor.execute(sql)
        gdf = gpd.read_postgis(sql, conn)
    else:
        print("Table non identifiable")
    return gdf


def network_from_postgres(Simple,
                          set_initial_crs=4326,
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

    # Let's get data from the postgres database
    edges_gdf = read_from_postgres("Edge")
    nodes_gdf = read_from_postgres("Node")

    # Split street network caracteristics like Circular City (Simple=True) and
    # others huge one (Simple=False)
    if Simple:
        # Delete edges with null lenght (points)
        #edges_gdf = edges_gdf[edges_gdf.geometry.length > 0]
        # Setting projection equal to 4326
        edges_gdf.set_crs(convert_to_crs, inplace=True)
        nodes_gdf.set_crs(convert_to_crs, inplace=True)
        # output is a degree value which we will convert to meter in next line
        intersection_radius = min(edges_gdf.geometry.length) * 0.1
        # applying a formula which convert degree to meter (regle de trois)
        intersection_radius = intersection_radius * 111.11 * 1000
        # zone_radius and intersection_radius are dependents
        zone_radius = intersection_radius / intersection_radius_percentage
        # distance_offset depends on intersection_radius (meter)
        distance_offset = distance_offset_percentage * intersection_radius
        tiles_layer = None
    else:
        nodes_gdf.set_crs(initial_crs, allow_override=True)
        edges_gdf.set_crs(initial_crs, allow_override=True)
        nodes_gdf.to_crs(convert_to_crs, inplace=True)
        # Delete edges with null lenght (points)
        edges_gdf = edges_gdf[edges_gdf.geometry.length > 0]
        intersection_radius = intersection_radius_percentage * zone_radius
        zone_radius = zone_radius
        distance_offset = distance_offset_percentage * zone_radius
        tiles_layer = 'OpenStreetMap'

    G = nx.from_pandas_edgelist(
        edges_gdf, 'source_id', 'target_id', [
            'speed', 'lenth', 'lanes', 'name', 'geom'], create_using=nx.MultiDiGraph())

    # Add oneway column (it is a boolean column)
    for u, v, d in G.edges(keys=False, data=True):
        if G.has_edge(v, u):
            G.edges[u, v, 0]['oneway'] = False
        else:
            G.edges[u, v, 0]['oneway'] = True

    df_graph_to_pandas = nx.to_pandas_edgelist(
        G, source='source_id', target='target_id')
    gdf = gpd.GeoDataFrame(
        df_graph_to_pandas,
        geometry='geom',
        crs=convert_to_crs)

    # On convertit en metre (m) avant d'appliquer le décalage afin
    # d'uniformiser
    gdf.to_crs(crs=default_crs, inplace=True)

    # Define parallel offset Geoserie
    # geometry to offset and column it depends on
    col_list = ['geom', 'oneway']
    gdf['_offset_geometry_'] = gdf[col_list].apply(
        lambda x: x['geom'].parallel_offset(
            distance_offset,link_side) if not x['oneway']
            else x['geom'].parallel_offset(0, link_side),
        axis=1)

    # Drop old geometry and replace it by _offset_geometry_
    gdf.drop('geom', axis=1, inplace=True)
    gdf.set_geometry('_offset_geometry_', inplace=True)

    # Converting back in 4326 before ploting
    gdf.to_crs(crs=convert_to_crs, inplace=True)

    latitudes = list(nodes_gdf['geom'].y)
    longitudes = list(nodes_gdf['geom'].x)

    # Initialize the map
    m = folium.Map(location=[latitudes[0], longitudes[0]],
                   max_zoom=18, prefer_canvas=True, tiles=tiles_layer)

    layer = folium.GeoJson(
        gdf,
        tooltip=folium.GeoJsonTooltip(
            fields=[
                'oneway',
                'lanes',
                'lenth',
                'speed',
                'name'],
            localize=True),
        style_function=lambda x: {
            'color': line_color
        }).add_to(m)

    # Bounding box the map such that the network is entirely center and visible
    m.fit_bounds(layer.get_bounds())

    # Adding the nodes points
    dx = zone_radius * 10**-3 / 111.3  # Conversion metre en degres
    for lat, long in list(zip(latitudes, longitudes)):
        folium.Circle(
            location=[
                lat,
                long],
            color='cyan',
            fill=True,
            fill_opacity=1,
            radius=intersection_radius
        ).add_to(m)

    m.save('templates/_network_.html')


def network_visualization(request):
    network_from_postgres(Simple=True)
    return render(request, '_network_.html')
