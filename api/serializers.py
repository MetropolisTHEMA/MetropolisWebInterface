from rest_framework import serializers
from drf_dynamic_fields import DynamicFieldsMixin
from metro_app.models import Edge, Node, RoadNetwork, RoadType, EdgeResults


class EdgeResultsSerializer(serializers.ModelSerializer):
    time = serializers.TimeField(format='%H:%M')

    class Meta:
        model = EdgeResults
        fields = '__all__'
        # exclude = ('id')


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
    speed = serializers.SerializerMethodField(method_name='get_speed')
    lanes = serializers.SerializerMethodField(method_name='get_lanes')

    class Meta:
        model = Edge
        fields = (
            'edge_id', 'name', 'length', 'speed', 'lanes',
        )

    def get_speed(self, instance):
        if instance.speed is None:
            return instance.road_type.default_speed
        else:
            return instance.speed

    def get_lanes(self, instance):
        if instance.lanes is None:
            return instance.road_type.default_lanes
        else:
            return instance.lanes
