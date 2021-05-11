from django.contrib import messages
from django.contrib.gis.geos import fromstr
from django.contrib.gis.geos import GEOSGeometry, LineString
from django.core.serializers import serialize
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from .forms import NodeForm, EdgeForm, RoadTypeFileForm
from .models import Node, Edge, RoadNetWork, RoadType
import json
from shapely import geometry
import pandas as pd
import geopandas as gpd
from pyproj import CRS
import folium
import csv
import io
# ............................................................................#
#                   VIEW OF UPLOADING A PROJECT IN THE DATABASE               #
# ............................................................................#


def upload_road(request, pk):
    template = "networks/node.html"
    roadnetwork = RoadNetWork.objects.get(id=pk)
    L = []
    if request.method == 'POST':
        form = RoadTypeFileForm(request.POST, request.FILES)
        if form.is_valid():
            datafile = request.FILES['my_file']
            datafile = datafile.read().decode('utf-8')
            objects = io.StringIO(datafile)
            next(objects)
            # csv.DictReader si csv par virgule, tsv alors \t
            for column in csv.reader(objects, delimiter='\t'):
                roadtype = RoadType(
                    name=column[2],
                    congestion=column[3],
                    default_speed=column[4],
                    default_lanes=column[5],
                    default_param1=column[6],
                    default_param2=column[6],
                    default_param3=column[6],
                    network_id=roadnetwork.pk
                )
                L.append(roadtype)
            RoadType.objects.bulk_create(L)
            messages.success(request, 'Your road file has been \
                             successfully imported !')
            return redirect('network_details', roadnetwork.pk)

    else:
        form = RoadTypeFileForm()
        return render(request, template, {'form': form})
    return render(request, template, roadnetwork)


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


def upload_csv(request):
    template = "networks/node.html"
    roadnetwork = RoadNetWork.objects.get(id=3)
    list_node_instance = []
    if request.method == 'POST':
        # We need to include the files when creating the form
        form = NodeForm(request.POST, request.FILES)
        if form.is_valid():
            # Getting data from the fielfield input
            datafile = request.FILES['my_file']
            datafile = datafile.read().decode('utf-8').splitlines()
            datafile = csv.DictReader(datafile)
            for row in datafile:
                lon, lat = row['x'], row['y']
                location = fromstr(f'POINT({lon} {lat})', srid=4326)
                node = Node(node_id=row['id'], name=row.get('name', ''),
                            location=location, network=roadnetwork)
                list_node_instance.append(node)
            Node.objects.bulk_create(list_node_instance)

    form = NodeForm()
    return render(request, template, {'form': form})


def upload_node(request, pk):
    template = "networks/node.html"
    roadnetwork = RoadNetWork.objects.get(id=pk)
    node_instance = Node.objects.filter(network_id=pk)
    list_node_instance = []

    if node_instance.count() > 0:
        messages.warning(request, "Fail ! Network contains\
                        already nodes data.")
        return redirect('network_details', roadnetwork.pk)

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

            Node.objects.bulk_create(list_node_instance)
            if node_instance.count() > 0:
                messages.success(request, 'Your node file has been \
                             successfully imported !')

        return redirect('network_details', roadnetwork.pk)
    else:
        form = NodeForm()
        return render(request, template, {'form': form})


"""
def upload_nodeold(request, pk):
    template = "networks/node.html"
    roadnetwork = RoadNetWork.objects.get(id=pk)
    node_instance = Node.objects.filter(network_id=pk)
    list_node_instance = []

    if node_instance.count() > 0:
        messages.warning(request, "Fail ! Network contains\
                        already nodes data.")
        return redirect('network_details', roadnetwork.pk)

    if request.method == 'POST':
        # We need to include the files when creating the form
        form = NodeForm(request.POST, request.FILES)
        if form.is_valid():
            # Getting data from the fielfield input
            datafile = request.FILES['my_file']
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
            Node.objects.bulk_create(list_node_instance)
            messages.success(request, 'Your node file has been \
                             successfully imported !')

        return redirect('network_details', roadnetwork.pk)
    else:
        form = NodeForm()
        return render(request, template, {'form': form})
"""


def upload_edge(request, pk):
    template = "networks/edge.html"
    roadnetwork = RoadNetWork.objects.get(id=pk)
    road_type = RoadType.objects.get(pk=2)
    node_instance = Node.objects.filter(network_id=pk)
    edge_instance = Edge.objects.filter(network_id=pk)
    list_edge_instance = []
    if edge_instance.count() > 0:
        messages.warning(request, "Fail ! Network contains \
                            already edges data.")
        return redirect('network_details', roadnetwork.pk)

    if node_instance.count() == 0:
        messages.warning(request, "Fail ! First import node file \
                            before importing edge.")
        return redirect('network_details', roadnetwork.pk)

    if request.method == 'POST':
        form = EdgeForm(request.POST, request.FILES)
        if form.is_valid():
            datafile = request.FILES['my_file']
            objects = json.load(datafile)
            for object in objects['features']:
                objet_type = object['geometry']['type']
                if objet_type == 'LineString':
                    properties = object['properties']
                    geometry = object['geometry']
                    location = GEOSGeometry(
                        LineString(geometry['coordinates']), srid=4326)

                    target = properties.get('target')
                    source = properties.get('source')

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
                        list_edge_instance.append(node)
                    except ObjectDoesNotExist:
                        pass
            Edge.objects.bulk_create(list_edge_instance)
            messages.success(request, 'Your edge file has beeb \
                            successfully imported !')
        return redirect('network_details', roadnetwork.pk)
    else:
        form = EdgeForm()
        return render(request, template, {'form': form})


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
    edges = serialize('geojson', edges, fields=('id', 'param1', 'param2',
                                                'param3', 'speed', 'length',
                                                'lanes', 'geometry', 'name',
                                                'source', 'target', 'network',
                                                'road_type'))
    edges = json.loads(edges)
    # Convert a geojson as geodataframe
    edges_gdf = gpd.GeoDataFrame.from_features(edges['features'])

    nodes = Node.objects.filter(network_id=network_id).values()
    nodes_df = pd.DataFrame(nodes)
    nodes_df['location'] = nodes_df['location'].apply(geometry.Point)
    nodes_gdf = gpd.GeoDataFrame(nodes_df, geometry=nodes_df['location'])

    # Split street network caracteristics like Circular City (Simple=True) and
    # others huge one (Simple=False)
    if Simple:
        edges_gdf.set_crs(CRS84, inplace=True)
        nodes_gdf.set_crs(CRS84, inplace=True)
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
        edges_gdf.set_crs(initial_crs, inplace=True)
        nodes_gdf.set_crs(initial_crs, inplace=True)
        nodes_gdf.to_crs(CRS84, inplace=True)
        edges_gdf = edges_gdf[edges_gdf.geometry.length > 0]
        zone_radius = zone_radius
        intersection_radius = intersection_radius_percentage * zone_radius
        distance_offset = distance_offset_percentage * zone_radius
        tiles_layer = 'OpenStreetMap'

    edges_gdf["oneway"] = edges_gdf.apply(lambda x: not edges_gdf[
            (edges_gdf["source"] == x["target"]
             & edges_gdf["target"] == x["source"])
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
    # Converting back in 4326 before ploting
    edges_gdf.to_crs(crs=CRS84, inplace=True)

    latitudes = list(nodes_gdf['geometry'].y)
    longitudes = list(nodes_gdf['geometry'].x)

    # Initialize the map
    m = folium.Map(location=[latitudes[0], longitudes[0]],
                   max_zoom=18, prefer_canvas=True, tiles=tiles_layer)

    layer = folium.GeoJson(
        edges_gdf,
        tooltip=folium.GeoJsonTooltip(fields=['oneway', 'lanes', 'length',
                                              'speed', 'name'], localize=True),
        style_function=lambda x: {'color': line_color}).add_to(m)

    # Bounding box the map such that the network is entirely center and visible
    m.fit_bounds(layer.get_bounds())

    # Adding the nodes points
    for lat, long in list(zip(latitudes, longitudes)):
        folium.Circle(location=[lat, long], color='cyan', fill=True,
                      fill_opacity=1, radius=intersection_radius).add_to(m)

    m.save('templates/visualization/visualization.html')
