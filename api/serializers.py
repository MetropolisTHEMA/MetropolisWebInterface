from rest_framework import serializers
from drf_dynamic_fields import DynamicFieldsMixin
from metro_app.models import Edge, Node, RoadNetwork, RoadType


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ('node_id', 'name')


class RoadNetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoadNetwork
        fields = ('id', 'id', 'name')


class RoadTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoadType
        fields = ('id', 'color')


class EdgeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """source = serializers.SerializerMethodField(method_name='get_node_source')
    target = serializers.SerializerMethodField(method_name='get_node_target')
    road_type = serializers.SerializerMethodField(
                                        method_name='get_road_type_id')
    speed = serializers.SerializerMethodField(method_name='get_speed')
    param2 = serializers.SerializerMethodField(method_name='get_param2')
    param3 = serializers.SerializerMethodField(method_name='get_param3')
    # lanes = serializers.SerializerMethodField(method_name='get_lanes')"""

    class Meta:
        model = Edge
        fields = (
            'id', 'edge_id', 'name', 'length', 'speed',
            'lanes', 'param1', 'param2', 'param3',  # 'network',
            'road_type', 'source', 'target'
            )
    """
    def get_road_type_id(self, instance):
        return {
                "id": instance.road_type.road_type_id,
                "name": instance.road_type.name
                }

    def get_node_source(self, instance):
        return {
                "node_id": instance.source.node_id,
                "node_name": instance.source.name
                }

    def get_node_target(self, instance):
        return {
                "node_id": instance.target.node_id,
                "node_name": instance.target.name
                }

    def get_speed(self, instance):
        if instance.speed is None:
            return instance.road_type.defaut_speed
        else:
            return instance.speed

    def get_param1(self, instance):
        if instance.param1 is None:
            return instance.road_type.default_param1
        else:
            return instance.param2

    def get_param2(self, instance):
        if instance.param2 is None:
            return instance.road_type.default_param2
        else:
            return instance.param3

    def get_param3(self, instance):
        if instance.param3 is None:
            return instance.road_type.default_param3
        else:
            return instance.param3

    def get_lanes(self, instance):
        if instance.lanes is None:
            return instance.road_type.default_lanes
        else:
            return instance.lanes
    """


def serialize_edge(edge):
    return {
        'id': edge.pk,
        'edge_id': edge.edge_id,
        'name': edge.name,
        'length': edge.length,
        'speed': edge.speed,
        'lanes': edge.lanes,
        'param1': edge.param1,
        'param2': edge.param2,
        'param3': edge.param3,
    }
