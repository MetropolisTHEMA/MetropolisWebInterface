from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from .models import EdgeResults, Edge, Run
import csv
import os
from metro_project.settings import BASE_DIR

"""Uploading edges results from metrosim to metro app database"""


def upload_edges_results(request, pk):
    """ Cette fonctin est mise a  cote en attendant le developpement
        de la partie simulation. Il nous faut cette partie pour pouvoir
        uploader les edges results du reseau correspondant sans changement
        manuel dans le code. Merci de ne pas mettre o days dans le travel times
        De ce fait nous continuerons le plugin TimeDimension une fois cette
        partie terminée"""
    list_edges_results = []
    test = []
    none_existing_edge_id = []
    run = Run.objects.get(id=1)
    edges = Edge.objects.select_related().filter(network_id=pk)
    edges_instance_dict = {edge.edge_id: edge for edge in edges}
    edges_results_root = os.path.join(BASE_DIR, 'edges_results/edge_results.csv')
    with open(edges_results_root) as edges_results:
        edges_results = edges_results.read().splitlines()

        # The following line return an objet containing each row
        # as a composition of directionary with column name as key
        edges_results = csv.DictReader(edges_results, delimiter=',',
                                       skipinitialspace=True)
        for row in edges_results:  # each row is dictionary
            try:
                edge_instance = edges_instance_dict[int(row["id"])]
        
            except KeyError:
                none_existing_edge_id.append(row["id"])
            else:
                edge = EdgeResults(
                    time=row["time"],
                    congestion=row["congestion"],
                    travel_time=row["travel_time"],
                    speed=row["speed"],
                    edge=edge_instance,
                    run=run)
                list_edges_results.append(edge)

    try:
        EdgeResults.objects.bulk_create(list_edges_results)
    except IntegrityErroras as e:
        raise ValidationError(e)
    else:
        return HttpResponse('Process finished')
