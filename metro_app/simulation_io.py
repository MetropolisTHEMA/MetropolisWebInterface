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
                    beta=beta[i] / 3600.0,
                    gamma=gamma[i] / 3600.0,
                    desired_arrival=preferences.desired_arrival,
                    vehicle=preferences.vehicle,
                    dep_time_car_choice_model=preferences.dep_time_car_choice_model,
                    # The minus is here because the simulator expects the travel
                    # utility coefficient (not travel cost coefficient).
                    car_vot=-car_vot[i] / 3600.0,
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
    
    try:
        Agent.objects.bulk_create(agents)
    except Exception as e:
        return "Couldn't save agent due to his error: {}".format(e)
    else:
        population.generated = True
        population.save()
        return "Agents successfully created"
   

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
    #  vehicles = [vehicles[i] for i in valid_vehicles]
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
    assert len(agents) == len(output['agent_results']), \
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
        if 'Car' in sim_res['mode_results']:
            res.mode = AgentResults.CAR
            res.car_exp_arrival_time = timedelta(
                seconds=sim_res['pre_day_results']['choices']['Car']['expected_arrival_time'])
        agent_results.append(res)
    AgentResults.objects.bulk_create(agent_results)

    # Read agent paths.
    agent_paths = list()
    edges = run.network.road_network.edge_set.all()
    for (sim_res, agent) in zip(output['agent_results'], agents):
        if not 'Car' in sim_res['mode_results']:
            continue
        route = sim_res['mode_results']['Car']['route']
        breakpoints = sim_res['mode_results']['Car']['road_breakpoints']
        for i in range(len(route)):
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
    AgentRoadPath.objects.bulk_create(agent_paths)

    # Read edge travel times.
    breakpoints = np.arange(
        run.parameter_set.period_start.total_seconds(),
        run.parameter_set.period_end.total_seconds() + 1,
        run.parameter_set.period_interval.total_seconds(),
    )
    edge_results = list()
    # TODO: For now, we only take the edge weights of the first vehicle.
    for i, ttf in enumerate(output['weights']['road_network'][0]):
        edge = edges[i]
        length = edge.length
        if 'Piecewise' in ttf:
            points = ttf['Piecewise']['points']
            n = len(points)
            j = 0
            for bp in breakpoints:
                while j + 1 < n and points[j + 1]['x'] <= bp:
                    j += 1
                res = EdgeResults(
                    edge=edge,
                    run=run,
                    time=timedelta(seconds=bp),
                    congestion=0.0, # TODO
                    travel_time=timedelta(seconds=points[j]['y']),
                    speed=length / points[j]['y'],
                )
                edge_results.append(res)
        else:
            tt = ttf['Constant']
            for bp in breakpoints:
                res = EdgeResults(
                    edge=edge,
                    run=run,
                    time=timedelta(seconds=bp),
                    congestion=0.0, # TODO
                    travel_time=timedelta(seconds=tt),
                    speed=length / tt,
                )
                edge_results.append(res)
    EdgeResults.objects.bulk_create(edge_results)


"""
Load the aggregate results of an iteration.
"""
def read_iteration_results(run, iteration_counter, filename):
    with open(filename) as f:
        output = json.load(f)
    car_output = output['mode_results']['Car']

    results = AggregateResult(
        run=run,
        iteration=iteration_counter,
        surplus_mean=output['surplus']['mean'],
        surplus_std=output['surplus']['std'],
        surplus_min=output['surplus']['min'],
        surplus_max=output['surplus']['max'],
        car_count=car_output['count'],
        car_congestion=car_output['congestion'],
        car_departure_time_mean=car_output['departure_times']['mean'],
        car_departure_time_std=car_output['departure_times']['std'],
        car_departure_time_min=car_output['departure_times']['min'],
        car_departure_time_max=car_output['departure_times']['max'],
        car_arrival_time_mean=car_output['arrival_times']['mean'],
        car_arrival_time_std=car_output['arrival_times']['std'],
        car_arrival_time_min=car_output['arrival_times']['min'],
        car_arrival_time_max=car_output['arrival_times']['max'],
        car_road_time_mean=car_output['road_times']['mean'],
        car_road_time_std=car_output['road_times']['std'],
        car_road_time_min=car_output['road_times']['min'],
        car_road_time_max=car_output['road_times']['max'],
        car_bottleneck_time_mean=car_output['bottleneck_times']['mean'],
        car_bottleneck_time_std=car_output['bottleneck_times']['std'],
        car_bottleneck_time_min=car_output['bottleneck_times']['min'],
        car_bottleneck_time_max=car_output['bottleneck_times']['max'],
        car_pending_time_mean=car_output['pending_times']['mean'],
        car_pending_time_std=car_output['pending_times']['std'],
        car_pending_time_min=car_output['pending_times']['min'],
        car_pending_time_max=car_output['pending_times']['max'],
        car_travel_time_mean=car_output['pending_times']['mean'],
        car_travel_time_std=car_output['travel_times']['std'],
        car_travel_time_min=car_output['travel_times']['min'],
        car_travel_time_max=car_output['travel_times']['max'],
        car_free_flow_travel_time_mean=car_output['free_flow_travel_times']['mean'],
        car_free_flow_travel_time_std=car_output['free_flow_travel_times']['std'],
        car_free_flow_travel_time_min=car_output['free_flow_travel_times']['min'],
        car_free_flow_travel_time_max=car_output['free_flow_travel_times']['max'],
        car_length_mean=car_output['lengths']['mean'],
        car_length_std=car_output['lengths']['std'],
        car_length_min=car_output['lengths']['min'],
        car_length_max=car_output['lengths']['max'],
        car_edge_count_mean=car_output['edge_counts']['mean'],
        car_edge_count_std=car_output['edge_counts']['std'],
        car_edge_count_min=car_output['edge_counts']['min'],
        car_edge_count_max=car_output['edge_counts']['max'],
        car_utility_mean=car_output['utilities']['mean'],
        car_utility_std=car_output['utilities']['std'],
        car_utility_min=car_output['utilities']['min'],
        car_utility_max=car_output['utilities']['max'],
        car_exp_travel_time_diff_mean=car_output['exp_travel_time_diff']['mean'],
        car_exp_travel_time_diff_std=car_output['exp_travel_time_diff']['std'],
        car_exp_travel_time_diff_min=car_output['exp_travel_time_diff']['min'],
        car_exp_travel_time_diff_max=car_output['exp_travel_time_diff']['max'],
    )
    results.save()
