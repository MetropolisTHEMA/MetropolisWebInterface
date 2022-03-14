import json
from datetime import timedelta
import numpy as np

from metro_app.models import *


"""Generate `size` values from random distribution `distr`, with given mean and
standard-deviation, using the given random-number generator.

Supported distributions are:
- 0: constant
- 1: uniform
- 2: normal
- 3: log-normal
"""


def generate_values(rng, distr, mean, std, size):
    if isinstance(mean, timedelta):
        mean = mean.total_seconds()
    if isinstance(std, timedelta):
        std = std.total_seconds()
    assert isinstance(mean, float), f'Invalid mean value: {mean}'
    assert std is None or isinstance(std, float), f'Invalid std value: {std}'
    if distr == 0:  # Constant.
        return np.repeat(mean, size)
    elif distr == 1:  # Uniform.
        assert std is not None, \
            'Std must be non-null for uniform distributions'
        return rng.uniform(mean - std, mean + std, size=size)
    elif distr == 2:  # Normal.
        assert std is not None, \
            'Std must be non-null for normal distributions'
        return rng.normal(mean, std, size=size)
    elif distr == 3:  # Log-normal.
        assert std is not None, \
            'Std must be non-null for log-normal distributions'
        return rng.lognormal(mean, std, size=size)
    else:
        raise f'Unsupported distribution: {distr}'


"""Generate a list of agents for a given population segment and store them in
the database.
"""

from time import sleep
def generate_agents(population_segment):
    sleep(10)
    preferences = population_segment[0].preferences
    od_matrix = population_segment[0].od_matrix
    size = od_matrix.size
    rng = np.random.default_rng(population_segment[0].random_seed)

    # Generate random values.
    if preferences.mode_choice_model == preferences.DETERMINISTIC_MODE:
        mode_choice_u = rng.uniform(0, 1, size=size)
    elif preferences.mode_choice_model == preferences.LOGIT_MODE:
        mode_choice_u = rng.uniform(0, 1, size=size)
        mode_choice_mu = generate_values(
            rng,
            preferences.mode_choice_mu_distr,
            preferences.mode_choice_mu_mean,
            preferences.mode_choice_mu_std,
            size,
        )
    elif preferences.mode_choice_model == preferences.FIRST_MODE:
        # Nothing to do.
        pass
    else:
        msg = 'Unsupported distribution for mode choice: {}'
        raise msg.format(preferences.mode_choice_model)
    t_star = generate_values(
        rng,
        preferences.t_star_distr,
        preferences.t_star_mean,
        preferences.t_star_std,
        size,
    )
    delta = generate_values(
        rng,
        preferences.delta_distr,
        preferences.delta_mean,
        preferences.delta_std,
        size,
    )
    beta = generate_values(
        rng,
        preferences.beta_distr,
        preferences.beta_mean,
        preferences.beta_std,
        size,
    )
    gamma = generate_values(
        rng,
        preferences.gamma_distr,
        preferences.gamma_mean,
        preferences.gamma_std,
        size,
    )
    if preferences.dep_time_car_choice_model == preferences.LOGIT_DEP_TIME:
        dep_time_u = rng.uniform(0, 1, size=size)
        dep_time_mu = generate_values(
            rng,
            preferences.dep_time_car_mu_distr,
            preferences.dep_time_car_mu_mean,
            preferences.dep_time_car_mu_std,
            size,
        )
    elif preferences.dep_time_car_choice_model == preferences.CONSTANT_DEP_TIME:
        dep_time_constant = generate_values(
            rng,
            preferences.dep_time_car_constant_distr,
            preferences.dep_time_car_constant_mean,
            preferences.dep_time_car_constant_std,
            size,
        )
    else:
        msg = 'Unsupported distribution for departure time: {}'
        raise msg.format(preferences.dep_time_car_choice_model)
    car_vot = generate_values(
        rng,
        preferences.car_vot_distr,
        preferences.car_vot_mean,
        preferences.car_vot_std,
        size,
    )

    agents = list()
    i = 0
    for od_pair in od_matrix.odpair_set.all():
        for _ in range(od_pair.size):
            agent = Agent(
                agent_id=i + 1,
                population_segment=population_segment,
                origin_zone=od_pair.origin,
                destination_zone=od_pair.destination,
                mode_choice_model=preferences.mode_choice_model,
                t_star=timedelta(seconds=tstar[i]),
                delta=timedelta(seconds=delta[i]),
                beta=beta[i],
                gamma=gamma[i],
                desired_arrival=preferences.desired_arrival,
                vehicle=preferences.vehicle,
                dep_time_car_choice_model=preferences.dep_time_car_choice_model,
                car_vot=car_vot,
            )
            if preferences.mode_choice_model == preferences.DETERMINISTIC_MODE:
                agent.mode_choice_u = mode_choice_u[i]
            elif preferences.mode_choice_model == preferences.LOGIT_MODE:
                agent.mode_choice_u = mode_choice_u[i]
                agent.mode_choice_mu = mode_choice_mu[i]
            if preferences.dep_time_car_model == preferences.LOGIT_DEP_TIME:
                agent.dep_time_car_u = dep_time_car_u[i]
                agent.dep_time_car_mu = dep_time_car_mu[i]
            elif preferences.dep_time_car_model == preferences.CONSTANT_DEP_TIME:
                agent.dep_time_car_constant = timedelta(
                    seconds=dep_time_car_constant[i])
            agents.append(agent)
            i += 1
    
    Agent.objects.bulk_create(agents)
    population_segment.generated = True
    # population_segment.save()


"""
Create a JSON input file readable by the simulator from a Run.
"""


# Generate input
def to_input_json(parameters, population, road_network=None):
    network = dict()

    if road_network is not None:
        graph = dict()
        graph["edge_property"] = "directed"
        # Read nodes.
        graph['nodes'] = list(road_network.node_set.all().values('id'))
        node_map = dict()
        for i, node in enumerate(graph['nodes']):
            node_map[node['id']] = i
        # Read edges.
        graph['edges'] = list()
        edges = road_network.edge_set.all().select_related(
                'road_type', 'source', 'target')
        for edge in edges:
            source = node_map[edge.source.id]
            target = node_map[edge.target.id]
            edge_data = {
                'id': edge.id,
                'base_speed': edge.get_speed(),
                'length': edge.get_length_in_km(),
                'lanes': edge.get_lanes(),
                'speed_density': edge.road_type.get_congestion_display(),
            }
            if (outflow := edge.get_outflow()) is not None:
                edge_data['bottleneck_outflow'] = outflow
            if (param1 := edge.get_param1()) is not None:
                edge_data['param1'] = param1
            if (param2 := edge.get_param2()) is not None:
                edge_data['param2'] = param2
            if (param3 := edge.get_param3()) is not None:
                edge_data['param3'] = param3
            graph['edges'].append([source, target, edge_data])
        # Read vehicles.
        vehicles = list()
        vehicle_map = dict()
        for i, vehicle in enumerate(road_network.vehicle_set.all()):
            vehicle_map[vehicle.id] = i
            vehicles.append({
                'name': vehicle.name,
                'length': vehicle.length,
                'speed_function': vehicle.get_speed_function(),
            })
        network['road_network'] = {
            'graph': graph,
            'vehicles': vehicles,
        }

    agents = list()
    for agent in population.agent_set.all():
        modes = list()
        # Add Car mode if available.
        if road_network is not None:
            car_origin = node_map[agent.get_origin_node(road_network)]
            car_destination = node_map[
                agent.get_destination_node(road_network)]
            try:
                car = {
                    'origin': car_origin,
                    'destination': car_destination,
                    'vehicle': vehicle_map[agent.vehicle],
                    'departure_time_model': agent.get_car_dep_time_model(),
                    'utility_model': agent.get_car_utility_model(),
                }
                modes.append(car)
            except KeyError:
                pass
            agents.append({
                'modes': modes,
                'mode_choice': agent.get_mode_choice_model(),
                'schedule_utility': agent.get_schedule_delay_utility(),
            })

    parameters_data = dict()
    parameters_data['period'] = [parameters.period_start.total_seconds(),
                                 parameters.period_end.total_seconds()]
    parameters_data['learning_model'] = parameters.get_learning_model()
    parameters_data['convergence_criteria'] = \
        parameters.get_convergence_criteria()

    simulation = {
        'network': network,
        'agents': agents,
        'parameters': parameters_data,
    }
    return json.dumps(simulation)
