import json
from datetime import timedelta
import numpy as np
import os

from metro_app.models import *


"""Generate `size` values from random distribution `distr`, with given mean and
standard-deviation, using the given random-number generator.

Supported distributions are:
- 0: constant
- 1: uniform
- 2: normal
- 3: log-normal
"""


def get_input_directory(run):
    return os.path.join(
        settings.BASE_DIR, 'input_dir', str(run.id)
    )


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
def generate_agents(population):
    agents = list()
    i = 0
    rng = np.random.default_rng(population.random_seed)

    for population_segment in population.populationsegment_set.all():
        preferences = population_segment.preferences
        od_matrix = population_segment.od_matrix
        size = od_matrix.size

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
            dep_time_car_u = rng.uniform(0, 1, size=size)
            dep_time_car_mu = generate_values(
                rng,
                preferences.dep_time_car_mu_distr,
                preferences.dep_time_car_mu_mean,
                preferences.dep_time_car_mu_std,
                size,
            )
        elif preferences.dep_time_car_choice_model == preferences.CONSTANT_DEP_TIME:
            dep_time_car_constant = generate_values(
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

        for od_pair in od_matrix.odpair_set.all():
            for _ in range(od_pair.size):
                agent = Agent(
                    agent_id=i + 1,
                    population=population,
                    origin_zone=od_pair.origin,
                    destination_zone=od_pair.destination,
                    mode_choice_model=preferences.mode_choice_model,
                    t_star=timedelta(seconds=t_star[i]),
                    delta=timedelta(seconds=delta[i]),
                    beta=beta[i],
                    gamma=gamma[i],
                    desired_arrival=preferences.desired_arrival,
                    vehicle=preferences.vehicle,
                    dep_time_car_choice_model=preferences.dep_time_car_choice_model,
                    car_vot=car_vot[i],
                )
                if preferences.mode_choice_model == preferences.DETERMINISTIC_MODE:
                    agent.mode_choice_u = mode_choice_u[i]
                elif preferences.mode_choice_model == preferences.LOGIT_MODE:
                    agent.mode_choice_u = mode_choice_u[i]
                    agent.mode_choice_mu = mode_choice_mu[i]
                if preferences.dep_time_car_choice_model == preferences.LOGIT_DEP_TIME:
                    agent.dep_time_car_u = dep_time_car_u[i]
                    agent.dep_time_car_mu = dep_time_car_mu[i]
                elif preferences.dep_time_car_choice_model == preferences.CONSTANT_DEP_TIME:
                    agent.dep_time_car_constant = timedelta(
                        seconds=dep_time_car_constant[i])
                agents.append(agent)
                i += 1

    Agent.objects.bulk_create(agents)

    population.generated = True
    population.save()


"""
Create a JSON input file readable by the simulator from a Run.
"""
def to_input_json(run):
    network = dict()
    road_network = run.network.road_network
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
                'base_speed': edge.get_speed_in_m_per_s(),
                'length': edge.get_length_in_meters(),
                'lanes': edge.get_lanes(),
                'speed_density': edge.get_speed_density(),
            }
            if (outflow := edge.get_outflow_in_m_per_s()) is not None:
                edge_data['bottleneck_outflow'] = outflow
            graph['edges'].append([source, target, edge_data])

    # Read vehicles.
    vehicles = list()
    vehicle_map = dict()
    for i, vehicle in enumerate(run.project.vehicle_set.all()):
        vehicle_map[vehicle.id] = i
        speed_function = vehicle.get_speed_input()
        vehicles.append({
            'name': vehicle.name,
            'length': vehicle.length,
            'speed_function': speed_function,
        })

    agents = list()
    valid_vehicles = set()
    for agent in run.population.agent_set.all().select_related(
            'vehicle', 'origin_zone', 'destination_zone'):
        modes = list()
        # Add Car mode.
        car_origin = node_map[agent.get_origin_node(run.network).node_id]
        car_destination = node_map[agent.get_destination_node(run.network).node_id]
        vehicle_id = vehicle_map[agent.vehicle.id]
        try:
            car = {
                'origin': car_origin,
                'destination': car_destination,
                'vehicle': vehicle_id,
                'departure_time_period': run.parameter_set.get_period(),
                'departure_time_model': agent.get_car_dep_time_model(),
                'utility_model': agent.get_car_utility_model(),
            }
            modes.append({'Car': [0, car]})
            valid_vehicles.add(vehicle_id)
        except KeyError:
            pass
        agents.append({
            'modes': modes,
            'mode_choice': agent.get_mode_choice_model(),
            'schedule_utility': agent.get_schedule_delay_utility(),
        })

    # Keep only the vehicles with at least one agent.
    vehicles = [vehicles[i] for i in valid_vehicles]
    # Add a vehicle with a base speed function as last vehicle (used to get
    # comparible output).
    vehicles.append({
        'name': 'Dummy vehicle',
        'length': 1.0,
        'speed_function': 'Base',
    })
    network['road_network'] = {
        'graph': graph,
        'vehicles': vehicles,
    }

    parameters = dict()
    parameters['period'] = run.parameter_set.get_period()
    parameters['learning_model'] = run.parameter_set.get_learning_model()
    parameters['convergence_criteria'] = \
        run.parameter_set.get_convergence_criteria()
    if run.parameter_set.random_seed:
        parameters['random_seed'] = run.parameter_set.random_seed
    else:
        parameters['random_seed'] = get_random_seed()
    parameters['update_ratio'] = run.parameter_set.update_ratio
    rn_params = {
        'edge_approx_bound': 10.0,
        'space_approx_bound': 10.0,
        'weight_simplification': {
            'Interval': run.parameter_set.period_interval.total_seconds(),
        },
    }
    network_params = {'road_network': rn_params}
    parameters['network'] = network_params

    simulation = {
        'network': network,
        'agents': agents,
        'parameters': parameters,
    }

    # Create and save agents in json file
    directory = get_input_directory(run)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    
    with open(os.path.join(directory, "simulation.json"), 'w') as file:
        # Saving the file
        json.dump(simulation, file)

    # return json.dumps(simulation)


"""
Load the output of a run in the database.
"""
def from_output_json(run, filename):
    with open(filename) as f:
        output = json.load(f)

    # Read agent-specific results.
    agent_results = list()
    agents = run.population.agent_set.all()
    assert agents.len() == output['agent_results'].len(), \
        'Invalid number of agent-specific results'
    for (sim_res, agent) in zip(output['agent_results'], agents):
        dt = timedelta(seconds=sim_res['departure_time'])
        at = timedelta(seconds=sim_res['arrival_time'])
        res = AgentResults(
            agent=agent,
            run=run,
            utility=sim_res['utility'],
            departure_time=dt,
            arrival_time=at,
            travel_time=at - dt,
            real_cost=0.0,
            surplus=sim_res['pre_day_results']['expected_utility'],
        )
        if sim_res['mode_results'].keys()[0] == 'Car':
            res.mode = AgentResults.CAR
            res.car_exp_arrival_time = timedelta(
                seconds=sim_res['pre_day_results']['choices']['Car']['expected_arrival_time'])
        agent_results.append(res)
    AgentResults.bulk_create(agent_results)

    # Read agent paths.
    agent_paths = list()
    edges = run.network.road_network.edge_set.all()
    for (sim_res, agent) in zip(output['agent_results'], agents):
        if sim_res['mode_results'].keys()[0] != 'Car':
            continue
        route = sim_res['mode_results']['Car']['route']
        breakpoints = sim_res['mode_results']['Car']['road_breakpoints']
        for i in len(route):
            edge = edges[route[i]]
            if i + 1 < len(route):
                tt = breakpoints[i + 1] - breakpoints[i]
            else:
                tt = sim_res['arrival_time'] - breakpoints[i]
            path_entry = AgentRoadPath(
                agent=agent,
                run=run,
                edge=edge,
                time=timedelta(seconds=breakpoints[i]),
                travel_time=timedelta(seconds=tt),
            )
            agent_paths.append(path_entry)
    AgentRoadPath.bulk_create(agent_paths)

    # Read edge travel times.
    breakpoints = np.arange(
        run.parameters.period_start.total_seconds(),
        run.parameters.period_end.total_seconds() + 1,
        run.parameters.period_interval.total_seconds(),
    )
    edge_results = list()
    for i, ttf in enumerate(output['weights']['road_network'][-1]):
        edge = edges[i]
        length = edge.length
        if 'Piecewise' in ttf:
            for j, bp in enumerate(breakpoints):
                res = EdgeResults(
                    edge=edge,
                    run=run,
                    time=timedelta(seconds=bp),
                    congestion=0.0, # TODO
                    travel_time=timedelta(seconds=ttf['travel_times'][j]),
                    speed=length / ttf['travel_times'][j],
                )
                edge_results.append(res)
        for j, bp in enumerate(breakpoints):
            assert ttf['departure_times'][j] == bp, \
                'Invalid travel-time function for edge {}'.format(i)
            res = EdgeResults(
                edge=edge,
                run=run,
                time=timedelta(seconds=bp),
                congestion=0.0, # TODO
                travel_time=timedelta(seconds=ttf['travel_times'][j]),
                speed=length / ttf['travel_times'][j],
            )
            edge_results.append(res)
    EdgeResults.bulk_create(edge_results)
