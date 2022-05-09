from django.shortcuts import render, redirect
from django.contrib import messages
from metro_app.models import Agent, Population, Vehicle, Zone
from metro_app.forms import AgentForm, AgentFileForm
from metro_app.filters import AgentFilter
from metro_app.tables import AgentTable
from django_tables2 import RequestConfig
import json
from datetime import timedelta
from metro_app.simulation_io import generate_agents
from django_q.tasks import async_task
from metro_app.hooks import str_hook
from metro_app.models import Population, BackgroundTask


def add_agent(request, pk):
    population = Population.objects.get(id=pk)
    population_segment = population.populationsegment_set.all()

    if population_segment.count() > 0:
        messages.warning(request, 'There exists a population segment \
            already created. So you can not create or add an agent.')
        return redirect('population_details', pk)
    else:
        agent = Agent(population=population)
        if request.method == 'POST':
            form = AgentForm(request.POST, instance = agent)
            if form.is_valid():
                form.save()
                return redirect('population_details', pk)
            
        form = AgentForm(initial={'population': population})
        context = {
            'form': form
        }
        return render(request, 'views/form.html', context)

def upload_agent(request, pk):
    population = Population.objects.get(id=pk)
    population_segment = population.populationsegment_set.all()

    if population_segment.exists():
        messages.warning(request, 'There exists a population segment \
            already created. So you can not create or add an agent.')
        return redirect('population_details', pk)

    agents = population.agent_set.all()
    if agents.exists():
        messages.warning(request, "Fail! Agent already contains agents data. \
                            Delete them before importing again")
        return redirect('population_details', pk)

    if request.method == 'POST':
        vehicles = Vehicle.objects.all()
        zones = Zone.objects.filter(zone_set=population.zone_set)
        zone_instance_dict = {zone.zone_id: zone for zone in zones}
        vehicle_instance_dict = {vehicle.vehicle_id: vehicle for vehicle in vehicles}

        form = AgentFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['my_file']
            list_agent = []
            if file.name.endswith('.json'):
                data = json.load(file)
                for feature in data:
                    try:
                        origin = zone_instance_dict[feature['origin']]
                        destination = zone_instance_dict[feature['destination']]
                        vehicle = vehicle_instance_dict[feature['vehicle']]
                    except KeyError:
                        messages.error(request, 'Either a wrong file is imported,\
                                         either origin, destination or/and\
                                         vehicle are missing')
                        return redirect('upload_agent', pk)
                    mode_choice = feature['mode_choice']
                    if mode_choice == 'First':
                        mode_choice_model = 2
                        mode_choice_u = None
                        mode_choice_mu = None
                    elif type(mode_choice) == dict:
                        mode_choice_model_key = list(mode_choice.keys())[0]
                        if mode_choice_model_key == 'Deterministic':
                            mode_choice_model = 0
                            mode_choice_u = list(mode_choice.values())[0]
                            mode_choice_mu = None
                        elif mode_choice_model_key == 'Logit':
                            mode_choice_model = 1
                            mode_choice_u = mode_choice['Logit']['u']
                            mode_choice_mu = mode_choice['Logit']['mu']
                    
                    departure_time_model = feature['departure_time_model']
                    dep_time_car_choice_model_key = list(departure_time_model.keys())[0]
                    if dep_time_car_choice_model_key == 'Constant':
                        dep_time_car_choice_model = 1
                        dep_time_car_u = list(departure_time_model.values())[0]
                        dep_time_car_mu = None
                    elif dep_time_car_choice_model_key == 'Logit':
                        dep_time_car_choice_model = 0
                        dep_time_car_u = departure_time_model['Logit']['u']
                        dep_time_car_mu = departure_time_model['Logit']['mu']

                    agent_instance = Agent(
                        agent_id=feature['id'],
                        population=population,
                        origin_zone=zone_instance_dict[feature['origin']],
                        destination_zone=zone_instance_dict[feature['destination']],
                        mode_choice_model = mode_choice_model,
                        mode_choice_u=mode_choice_u,
                        mode_choice_mu=mode_choice_mu,
                        t_star=timedelta(seconds=feature.get('t_star', 0)),
                        delta=timedelta(seconds=feature.get('delta', 0)),
                        beta=feature['beta'],
                        gamma=feature['gamma'],
                        desired_arrival=feature['desired_arrival'],
                        vehicle=vehicle_instance_dict[feature['vehicle']],
                        dep_time_car_choice_model=dep_time_car_choice_model,
                        dep_time_car_u=dep_time_car_u,
                        dep_time_car_mu=dep_time_car_mu,
                        dep_time_car_constant=feature.get('dep_time_car_constant', None),
                        car_vot=feature.get('car_vot', None)
                    )
                    list_agent.append(agent_instance)
            else:
                messages.error(request, 'File extension is not recognized,\
                               please select a good one')
                return redirect('upload_agent', pk)
            try:
                Agent.objects.bulk_create(list_agent)
            except Exception as e:
                messages.error(request, e)
                return redirect('upload_agent', pk)
            else:
                messages.success(request, 'agents file successfully upoloaded')
                return redirect('population_details', pk)
    form = AgentFileForm()
    context = {
        'form': form
    }
    return render(request, 'agent/agent.html', context)

def agent_table(request, pk):
    """"
    This function display database Agent table in the front end UI.
    So, users can sort, filter and paginate through pages
    """

    population = Population.objects.get(id=pk)
    agent = Agent.objects.select_related().filter(population=population)
    my_filter = AgentFilter(request.GET, queryset=agent)
    table = AgentTable(my_filter.qs)
    RequestConfig(request).configure(table)
    table.paginate(page=request.GET.get("page", 1), per_page=15)

    current_path = request.get_full_path()
    network_attribute = current_path.split("/")[4]
    context = {
        "table": table,
        "filter": my_filter,
        "population": population,
        "network_attribute": network_attribute
    }
    return render(request, 'table/table.html', context)

def delete_agents(request, pk):
    population = Population.objects.get(id=pk)
    agents = Agent.objects.filter(population=population)
    if agents:
        if request.method == 'POST':
            agents.delete()
            messages.success(request, "Population successfuly deleted")
            return redirect('population_details', pk)
    else:
        messages.warning(request, "There is no data to delete")
        return redirect('population_details', pk)
    
    context = {
        'population': population,
        'agents_to_delete': agents
    }
    return render(request, 'delete.html', context)

def generate_agents_input(request, pk):
    population = Population.objects.get(id=pk)    
    # population_segment = population.populationsegment_set.all()
    task_id = async_task(generate_agents, population,  hook=str_hook)
    description = 'Generating agents'
    db_task = BackgroundTask(
        project=population.project,
        id=task_id,
        description=description,
        population=population)
    db_task.save()
    messages.success(request, "Task successfully started")
    return redirect('population_details', pk)
    
