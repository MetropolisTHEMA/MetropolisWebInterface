from django.http import HttpResponse
from .models import EdgeResults, Edge, Run
import csv
import os
from metro_project.settings import BASE_DIR

"""Uploading edges results from metrosim to metro app database"""


def upload_edges_results(request, pk):
    list_edges_results = []
    none_existing_edge_id = []
    run = Run.objects.get(id=1)
    edges = Edge.objects.select_related().filter(network_id=pk)
    edges_instance_dict = {edge.edge_id: edge for edge in edges}
    edges_results_root = os.path.join(BASE_DIR, 'edges_results')
    url = edges_results_root + "/edge_results.csv"
    with open(url) as edges_results:
        edges_results = edges_results.read().splitlines()
        # The following line return an objet containing each row
        # as a composition of directionary with column name as key
        edges_results = csv.DictReader(edges_results, delimiter=',',
                                       skipinitialspace=True)
        for row in edges_results:  # each row is dictionary
            try:
                edge_instance = edges_instance_dict[int(row["id"])]
                edge_id = edge_instance.edge_id
            except KeyError:
                none_existing_edge_id.append(row["id"])
            else:
                edge = EdgeResults(
                    time=row["time"],
                    congestion=row["congestion"],
                    travel_time=row["travel_time"],
                    speed=row["speed"],
                    edge_id=edge_id,
                    run_id=run.id
                )
                list_edges_results.append(edge)
        EdgeResults.objects.bulk_create(list_edges_results)
        return HttpResponse('Process finished')
