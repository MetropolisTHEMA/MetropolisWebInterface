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
            msg= "Network successfully created"
            messages.success(request, msg)
            return redirect('network2_details', network.pk)

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
    zn = ZoneNodeRelation.objects.all()
    if zn.exists():
        messages.warning(request, 'ZoneNodeRelation already contains data')
        return redirect('network2_details', pk)

    if request.method == 'POST':
        zones = Zone.objects.filter(zone_set=network.zone_set) # Zone has Zonset as FK
        nodes = Node.objects.filter(network=network.road_network) # RoadNetwork as FK

        if not zones:
            msg = "Please upload zones first"
            messages.error(request, msg)
            return redirect('network2_details', pk)
        if not nodes:
            msg = "Please upload nodes first"
            messages.error(request, msg)
            return redirect('network2_details', pk)

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
                    try:
                        node = node_instance_dict[int(row['node'])]
                        zone = zone_instance_dict[int(row['zone'])]
                    except KeyError:
                        pass
                    else:
                        zone_node_relation_instance = ZoneNodeRelation(
                            network=network,
                            zone=zone,
                            node=node)
                        list_zone_node_relation.append(zone_node_relation_instance)
            try:
                ZoneNodeRelation.objects.bulk_create(list_zone_node_relation)
            except exeption as e:
                messages.error(request, e)
            else:
                messages.success(request, "ZoneNodeRelation file successfully uploaded")
                return redirect('network2_details', pk)

    form = ZoneNodeRelationFileForm()
    context = {
        'form': form,
    }
    return render(request, 'network/zone_node_relation.html', context)
