from rest_framework import serializers
from metro_app.models import Edge, Node, RoadNetwork, RoadType

class EdgeSerializer(serializers.ModelSerializer):
    source = serializers.SerializerMethodField(method_name='get_node_source')
    target = serializers.SerializerMethodField(method_name='get_node_target')
    road_type = serializers.SerializerMethodField(
                                        method_name='get_road_type_id')

    class Meta:
        model = Edge
        fields = (
            'id', 'edge_id', 'name', 'length', 'speed',
            'lanes', 'param1', 'param2', 'param3', 'network',
            'road_type', 'source', 'target'
        )

    def get_road_type_id(self, instance):
        return instance.road_type.road_type_id

    def get_node_source(self, instance):
        return {"node_id":instance.source.node_id, "name": instance.source.name}

    def get_node_target(self, instance):
        return {"node_id":instance.target.node_id, "name": instance.target.name}
        

class NodeSerializer(serializers.ModelSerializer):
    model = Node
    fields = ('node_id', 'name')

class RoadNetworkSerializer(serializers.ModelSerializer):
    model = RoadNetwork
    fields = ('id', 'id', 'name')

class RoadTypeSerializer(serializers.ModelSerializer):
    model= RoadType
    fields = ('id', 'color')
