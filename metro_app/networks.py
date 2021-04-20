from django.contrib import messages
from django.shortcuts import render
from .forms import NodeForm
from .models import Node
import csv
import io
import json
from django.contrib.gis.geos import fromstr


#............................................................................ #
#                   VIEW OF UPLOADING A PROJECT IN THE DATABASE               #
#............................................................................ #

def upload_node(request):
    template = "upload.html"
    # json.decoder.JSONDecodeError
    form = NodeForm()
    if request.method == 'POST':
        # Let's get the uploaded file (Get the incoming JSON Data)
        form = NodeForm(request.POST)
        if form.is_valid():
            #Forms only get a cleaned_data attribute when is_valid() has been called
            #network_fk = form.cleaned_data['nework']
            network_fk = form.cleaned_data['nework']

            datafile = request.FILES['my_file']
            objects = json.load(datafile)
            for object in objects['features']:
                properties = object['properties']
                geometry = object['geometry']
                node_id = properties.get('id')
                name = properties.get('name', 'no-name')
                location = fromstr(geometry.get('coordinates'))
                Node(
                    node_id = node_id,
                    name = name,
                    location = location,
                    network = network_fk,
                    ).save()
        else:
            print('Non cvalides')

    return render(request, template, {'form':form})
