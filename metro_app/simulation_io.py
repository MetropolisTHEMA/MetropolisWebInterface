import json

def to_input_json(parameters, populations=[], road_network=None):
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
                edge_data['bottleneck_outflow'] = outflow * edge.get_lanes()
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
    for population in populations:
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
