from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import NodeForm, EdgeForm
from .models import Node, Edge
import csv
import io
import json
from django.contrib.gis.geos import fromstr
from django.contrib.gis.geos import GEOSGeometry, LineString
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
                if objet_type =='Point':
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
        return  (node_id, name, location)

# bulk_create, bulk_update

def upload_node(request):
    template = "node.html"
    if request.method == 'POST':
        # We need to include the files when creating the form
        form = NodeForm(request.POST,request.FILES)
        if form.is_valid():
            network = form.cleaned_data['network']
            # Getting data from the fielfield input
            datafile = request.FILES['my_file']
            objects = json.load(datafile)
            for object in objects['features']:
                objet_type = object['geometry']['type']
                if objet_type =='Point':
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
                        node_id = node_id,
                        name = name,
                        location = location,
                        network = network
                        ).save()
        return redirect('home')
    else:
        form = NodeForm()
        return render(request, template, {'form':form})


def upload_edge(request):
    template = "edge.html"
    if request.method == 'POST':
        # We need to include the files when creating the form
        form = EdgeForm(request.POST,request.FILES)
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
                if objet_type =='LineString':
                    properties = object['properties']
                    geometry = object['geometry']
                    point1 = geometry['coordinates'][0]
                    point2 = geometry['coordinates'][1]
                    location = GEOSGeometry(LineString(geometry['coordinates']))
                    Edge(
                        param1 = properties.get('param1', 1.0),
                        param2 = properties.get('param2', 0),
                        param3 = properties.get('param3', 0),
                        speed = properties.get('speed', 0),
                        lenth = properties.get('lenth', 0),
                        lanes = properties.get('lanes', 0),
                        geometry = location,
                        name = properties.get('name', 0),
                        road_type = road_type,
                        target = target,
                        source = source,
                        network = network
                        ).save()
        return redirect('home')
    else:
        form = EdgeForm()
        return render(request, template, {'form':form})
