from rest_framework import viewsets
from rest_framework import status
from .serializers import (EdgeSerializer, NodeSerializer)
from metro_app.models import Edge, Node, RoadNetwork
from rest_framework.response import Response
from rest_framework.decorators import api_view


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
    Display a single instance.
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
        edges = Edge.objects.select_related('network', 'source', 'target',
                                            'road_type').filter(
                                             network=roadnetwork)

    if request.method == 'GET':
        serializer = EdgeSerializer(edges,
                                    context={'request': request}, many=True)
        return Response(serializer.data)


"""
class EdgeViewSet(viewsets.ModelViewSet):
    queryset = Edge.objects.select_related(
        'network', 'source', 'target', 'road_type'
        )
    serializer_class = EdgeSerializer

class NodeViewSet(viewsets.ModelViewSet):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer

class RoadNetworkViewSet(viewsets.ModelViewSet):
    queryset = RoadNetwork.objects.all()
    serializer_class = RoadNetworkSerializer

class RoadTypeViewSet(viewsets.ModelViewSet):
    queryset = RoadType.objects.all()
    serializer_class = RoadTypeSerializer
"""
