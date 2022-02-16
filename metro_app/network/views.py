from django.shortcuts import redirect, render
from django.contrib import messages
from metro_app.models import Project, Network, Node, Zone,ZoneNodeRelation
from metro_app.forms import NetworkForm, ZoneNodeRelationFileForm
import csv

def create_network2(request, pk):
    current_project = Project.objects.get(id=pk)
    network = Network(project=current_project)
    if request.method == 'POST':
        form = NetworkForm(request.POST, instance=network)
        if form.is_valid():
            form.save()
            return redirect('project_details', pk)

    form = NetworkForm(initial={'project':current_project})
    context = {
        'form': form
    }
    return render(request, 'views/form.html', context)


def update_network2(request, pk):
    network = Network.objects.get(id=pk)
    if request.method == 'POST':
        form = NetworkForm(request.POST, instance=network)
        if form.is_valid():
            form.save()
            return redirect('project_details', network.project.pk)

    form = NetworkForm(instance=network)
    context = {
        'form': form,
        'parent_template': 'index.html'
    }
    return render(request, 'update.html', context)


def network2_details(request, pk):
    network = Network.objects.get(id=pk)
    context = {
        'network': network
    }
    return  render(request, 'views/details.html', context)


def upload_zone_node_relation(request, pk):
    network = Network.objects.get(id=pk) # RaodNetWork as FK
    if request.method == 'POST':
        zones = Zone.objects.filter(zone_set=network.zone_set) # Zone has Zonset as FK
        nodes = Node.objects.filter(network=network.road_network) # RoadNetwork as FK
        node_instance_dict = {node.node_id: node for node in nodes}
        zone_instance_dict = {zone.zone_id: zone for zone in zones}
        
        list_zone_node_relation = []
        form = ZoneNodeRelationFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['my_file']
            if file.name.endswith('.csv'):
                data = file.read().decode('utf-8').splitlines()
                data = csv.DictReader(data, delimiter=',')
                for row in data:
                    node = node_instance_dict[int(row['node'])]
                    zone = zone_instance_dict[int(row['zone'])]
                    zone_node_relation_instance = ZoneNodeRelation(
                        network=network,
                        zone=zone,
                        node=node)
                    list_zone_node_relation.append(zone_node_relation_instance)

            ZoneNodeRelation.objects.bulk_create(list_zone_node_relation)
            messages.success(request, "file successfully uploaded")
            return redirect('network2_details', pk)

            """try:
                        node = node_instance_dict[row['node']]
                        zone = zone_instance_dict[row['zone']]
                    except KeyError:
                        mess
                    else:
                        zone_node_relation_instance = ZoneNodeRelation(
                            network=network,
                            zone=node,
                            Node=node
            )"""

                    

    form = ZoneNodeRelationFileForm()
    context = {
        'form': form,
    }
    return render(request, 'network/zone_node_relation.html', context)
