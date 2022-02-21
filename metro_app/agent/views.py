from django.shortcuts import render, redirect
from django.contrib import messages
from metro_app.models import Agent, Population, Vehicle, Zone
from metro_app.forms import AgentForm, AgentFileForm
import json


def add_agent(request, pk):
    population = Population.objects.get(id=pk)
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
    agents = Agent.objects.all()
    if agents.count() > 0:
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
                    else:
                        mode_choice = feature['mode_choice']
                        if mode_choice == 'First':
                            mode_choice_model == 2
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
                            t_star=feature.get('t_star', None),
                            delta=feature['delta'],
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

