# from rest_framework import viewsets
from rest_framework import status
from .serializers import (EdgeSerializer, EdgeResultsSerializer)
from metro_app.models import Edge, RoadNetwork, EdgeResults, Run, RoadType
from rest_framework.response import Response
from django.http import HttpResponse, Http404 # JsonResponse
from rest_framework.decorators import api_view
import json
from django.shortcuts import render
import datetime

@api_view(['GET', 'POST'])
def edge_list(request):
    """
    List all edges of all networks, or create a new edge.
    """
    if request.method == 'GET':
        edges = Edge.objects.prefetch_related('network', 'source', 'target',
                                              'road_type').all()
        context = {'request': request}  # for filtering by field in url
        serializer = EdgeSerializer(edges, many=True, context=context)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = EdgeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def edge_detail(request, pk):
    """
    Display a single edge instance of all network.
    """
    try:
        edge = Edge.objects.get(pk=pk)
    except Edge.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EdgeSerializer(edge, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = EdgeSerializer(edge, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        edge.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def edges_of_a_network(request, pk):
    """
    List all edges of a network.
    """
    try:
        roadnetwork = RoadNetwork.objects.get(pk=pk)
    except RoadNetwork.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    else:
        edges = Edge.objects.values("road_type_id", "edge_id",
                                    "name", "length", "speed",
                                    "lanes").filter(network=roadnetwork)
        roadtypes = RoadType.objects.filter(network=roadnetwork)
        roadtypes = {roadtype.id: roadtype for roadtype in roadtypes}

        for edge in edges:
            if edge["lanes"] is None:
                edge['lanes'] = roadtypes[edge['road_type_id']].default_lanes

            if edge["speed"] is None:
                edge['speed'] = roadtypes[edge['road_type_id']].default_speed

    edges = json.dumps(list(edges))
    if request.method == 'GET':
        return HttpResponse(edges, content_type="application/json")
        """"serializer = EdgeSerializer(edges, context={'request': request},
                                    many=True)
        return Response(serializer.data)"""


@api_view(['GET'])
def single_edge_instance_of_a_network(request, pk, id):
    """
    Display a single edge instance of a network.
    """
    try:
        roadnetwork = RoadNetwork.objects.get(pk=pk)
        edge = Edge.objects.filter(network=roadnetwork).get(edge_id=id)

    except RoadNetwork.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    except Edge.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # serializer = EdgeSerializer(edge, context={'request': request})
        # return Response(serializer.data)

        return render(request, 'mapbox_popup.html', {'edge': edge})


def get_lanes_field_attribute(request, pk):
    """
    This function is for filtering only lanes field from the api instead of
    having them all (name, speed, lanes and length). The results will used to
    as speed_output in the hml roadtype filter in the visualization.
    """
    try:
        roadnetwork = RoadNetwork.objects.get(pk=pk)

    except RoadNetwork.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    else:
        edges = Edge.objects.filter(
            network=roadnetwork).values('road_type_id', 'edge_id', 'lanes')
        roadtypes = RoadType.objects.filter(network=roadnetwork)
        roadtypes = {roadtype.id: roadtype for roadtype in roadtypes}
        lanes_dict = {}
        for edge in edges:
            if edge["lanes"] is None:
                edge['lanes'] = roadtypes[edge['road_type_id']].default_lanes

            values_list = list(edge.values())
            lanes_dict[values_list[1]] = values_list[2]

        edges = json.dumps(lanes_dict)
    if request.method == 'GET':
        return HttpResponse(edges, content_type="application/json")


def get_length_field_attribute(request, pk):
    """
    This function is for filtering only length field from the api instead of
    having them all (name, speed, lanes and length). The results will used to
    as speed_output in the hml roadtype filter in the visualization.
    """
    try:
        roadnetwork = RoadNetwork.objects.get(pk=pk)

    except RoadNetwork.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    else:
        edges = Edge.objects.filter(
            network=roadnetwork).values('edge_id', 'length')
        length_dict = {list(edge.values())[0]: list(edge.values())[1]
                       for edge in edges}

        edges = json.dumps(length_dict)
    if request.method == 'GET':
        return HttpResponse(edges, content_type="application/json")


def get_speed_field_attribute(request, pk):
    """
    This function is for filtering only speed field from the api instead of
    having them all (name, speed, lanes and length). The results will used to
    as speed_output in the hml roadtype filter in the visualization.
    """
    try:
        roadnetwork = RoadNetwork.objects.get(pk=pk)

    except RoadNetwork.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    else:
        edges = Edge.objects.filter(
            network=roadnetwork).values('road_type_id', 'edge_id', 'speed')

        roadtypes = RoadType.objects.filter(network=roadnetwork)
        roadtypes = {roadtype.id: roadtype for roadtype in roadtypes}

        speed_dict = {}
        for edge in edges:
            if edge["speed"] is None:
                edge['speed'] = roadtypes[edge['road_type_id']].default_speed

            values_list = list(edge.values())
            speed_dict[values_list[1]] = values_list[2]

        edges = json.dumps(speed_dict)
    if request.method == 'GET':
        return HttpResponse(edges, content_type="application/json")

@api_view(['GET'])
def edges_results(request, pk):
    """Return edges results data """
    # roadnetwork = RoadNetwork.objects.get(pk=pk)

    run = Run.objects.get(id=pk)
    # network_id = run.network_id
    edges = EdgeResults.objects.select_related(
        'run').filter(run=run)
   # edges = json.dumps(edges)
    if request.method == 'GET':
        #return HttpResponse(edges, content_type="application/json")
        serializer = EdgeResultsSerializer(edges, 
            context={'request': request}, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def get_field_from_edges_results(request, pk, field):
   
    if not field in ("congestion", "speed", "travel_time"):
        raise Http404
        # return Response(status=status.HTTP_404_NOT_FOUND)
    
    run = Run.objects.get(id=pk)
    edges = EdgeResults.objects.select_related('run').filter(
        run=run).values("edge__edge_id", field)

    speed_dict = {}
    for dictionary in edges:
        if dictionary["edge__edge_id"] in speed_dict:
            speed_dict[dictionary["edge__edge_id"]].append(dictionary[field])
        else:
            speed_dict[dictionary["edge__edge_id"]] = [dictionary[field]]
    
    edges = json.dumps(speed_dict, default=datetime.timedelta.total_seconds)
    if request.method == 'GET':
        return HttpResponse(edges, content_type="application/json")



