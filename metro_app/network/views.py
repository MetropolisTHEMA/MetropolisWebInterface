from django.shortcuts import redirect, render
from django.contrib import messages
from metro_app.models import Project, Network, Node, Zone,ZoneNodeRelation
from metro_app.forms import NetworkForm, ZoneNodeRelationFileForm
from metro_app.filters import ZoneNodeRelationFilter
from metro_app.tables import ZoneNodeRelationTable
from django_tables2 import RequestConfig
import csv

def list_of_networks(request, pk):
    current_project = Project.objects.get(id=pk)
    networks = Network.objects.filter(project=current_project)
    total_networks = networks.count()
    context = {
        'current_project': current_project,
        'networks': networks,
        'total_populations': total_networks,

    }
    return render(request, 'list.html', context)


def create_network(request, pk):
    current_project = Project.objects.get(id=pk)
    network = Network(project=current_project)
    if request.method == 'POST':
        form = NetworkForm(request.POST, instance=network)
        if form.is_valid():
            form.save()
            msg= "Network successfully created"
            messages.success(request, msg)
            return redirect('network_details', network.pk)

    form = NetworkForm(initial={'project':current_project})
    context = {
        'project': current_project,
        'form': form
    }
    return render(request, 'form.html', context)


def update_network(request, pk):
    network = Network.objects.get(id=pk)
    if request.method == 'POST':
        form = NetworkForm(request.POST, instance=network)
        if form.is_valid():
            form.save()
            return redirect('list_of_networks', network.project.pk)

    form = NetworkForm(instance=network)
    context = {
        'form': form,
        'parent_template': 'index.html'
    }
    return render(request, 'update.html', context)

def network_details(request, pk):
    network = Network.objects.get(id=pk)
    context = {
        'network': network
    }
    return  render(request, 'details.html', context)


def upload_zone_node_relation(request, pk):
    network = Network.objects.get(id=pk) # RaodNetWork as FK
    zn = ZoneNodeRelation.objects.all()
    if zn.exists():
        messages.warning(request, 'ZoneNodeRelation already contains data')
        return redirect('network_details', pk)

    if request.method == 'POST':
        zones = Zone.objects.select_related().filter(zone_set=network.zone_set) # Zone has Zonset as FK
        nodes = Node.objects.select_related().filter(network=network.road_network) # RoadNetwork as FK

        if not zones:
            msg = "Please upload zones first"
            messages.error(request, msg)
            return redirect('network_details', pk)
        if not nodes:
            msg = "Please upload nodes first"
            messages.error(request, msg)
            return redirect('network_details', pk)
        
        list_zone_node_relation = []
        form = ZoneNodeRelationFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['my_file']
            if file.name.endswith('.csv'):
                data = file.read().decode('utf-8').splitlines()
                data = csv.DictReader(data)

                node_instance_dict = {node.node_id: node for node in nodes}
                zone_instance_dict = {zone.zone_id: zone for zone in zones}
        
                compteur = 0
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

            
                if list_zone_node_relation:
                    try:
                        ZoneNodeRelation.objects.bulk_create(list_zone_node_relation)
                    except exeption as e:
                        messages.error(request, e)
                        return redirect('network_details', pk)
                    else:
                        messages.success(request, "ZoneNodeRelation file successfully uploaded")
                        return redirect('network_details', pk)
                else:
                    messages.error(request, "No data uploaded")
                    return redirect('upload_zone_node_relation', pk)

    form = ZoneNodeRelationFileForm()
    context = {
        'form': form,
    }
    return render(request, 'network/zone_node_relation.html', context)


def zone_node_relation_table(request, pk):
    network = Network.objects.get(id=pk)
    zone_node_relation = ZoneNodeRelation.objects.select_related().filter(network=network)
    my_filter = ZoneNodeRelationFilter(request.GET, queryset=zone_node_relation)
    table = ZoneNodeRelationTable(my_filter.qs)
    #table.paginate(page=request.GET.get("page", 1), per_page=15)
    RequestConfig(request).configure(table)

    current_path = request.get_full_path()
    network_attribute = current_path.split("/")[4]

    context = {
        "table": table,
        "filter": my_filter,
        "network": network,
        "network_attribute": network_attribute
    }
    return render(request, 'table/table.html', context)