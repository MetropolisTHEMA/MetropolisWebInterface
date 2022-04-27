import django_filters
from django_filters import CharFilter, NumberFilter
from .models import (Edge, Node, RoadType, RoadNetwork, Zone, ODPair,
                     Agent, ZoneNodeRelation, Vehicle)
from django import forms


class EdgeFilter(django_filters.FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains',
                      widget=forms.TextInput(attrs={
                                  'class': 'form-control',
                                  'placeholder': 'Name contains',
                              }))

    lanes = NumberFilter(field_name='lanes', lookup_expr='gte',
                         widget=forms.TextInput(attrs={
                               'class': 'form-control',
                               'placeholder': 'Lane greather than or equal to'
                           }))

    speed = NumberFilter(field_name='speed', lookup_expr='gte',
                         widget=forms.TextInput(
                           attrs={
                               'class': 'form-control',
                               'placeholder': 'Speed greather than or equal to'
                           }))

    class Meta:
        model = Edge
        fields = [
            'name',
            'lanes',
            'speed',
        ]


class NodeFilter(django_filters.FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains',
                      widget=forms.TextInput(attrs={
                                  'class': 'form-control',
                                  'placeholder': 'Name contains',
                              }))

    class Meta:
        model = Node
        fields = ('name',)


class RoadTypeFilter(django_filters.FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains',
                      widget=forms.TextInput(attrs={
                                  'class': 'form-control',
                                  'placeholder': 'Name contains',
                              }))

    class Meta:
        model = RoadType
        fields = ['congestion', 'name']


class RoadNetworkFilter(django_filters.FilterSet):
    class Meta:
        model = RoadNetwork
        fields = ('name',)


class ZoneFilter(django_filters.FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains',
                      widget=forms.TextInput(attrs={
                                  'class': 'form-control',
                                  'placeholder': 'Name contains',
                              }))

    class Meta:
        model = Zone
        fields = ('name',)


class ODPairFilter(django_filters.FilterSet):

    class Meta:
        model = ODPair
        fields = ('origin', 'destination', 'size')


class AgentFilter(django_filters.FilterSet):
    agent_id = NumberFilter(field_name='Agent id', lookup_expr='icontains',
                      widget=forms.TextInput(attrs={
                                  'class': 'form-control',
                                  'placeholder': 'Agent id contains',
                              }))
    origin_zone__zone_id = NumberFilter(field_name='Destination', lookup_expr='icontains',
                      widget=forms.TextInput(attrs={
                                  'class': 'form-control',
                                  'placeholder': 'Origin id contains',
                              }))
    destination_zone__zone_id = NumberFilter(field_name='Origin', lookup_expr='icontains',
                      widget=forms.TextInput(attrs={
                                  'class': 'form-control',
                                  'placeholder': 'Destination Id contains',
                              }))
    class Meta:
        model = Agent
        fields = (
            'agent_id', 
            'origin_zone__zone_id',
            'destination_zone__zone_id', 
            # 'vehicle__vehicle_id'
        )


class ZoneNodeRelationFilter(django_filters.FilterSet):
    class Meta:
        model = ZoneNodeRelation
        exclude = ('tags', 'date_created')


class VehicleFilter(django_filters.FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains',
                      widget=forms.TextInput(attrs={
                                  'class': 'form-control',
                                  'placeholder': 'Name contains',
                              }))

    length = NumberFilter(field_name='length', lookup_expr='gte',
                         widget=forms.TextInput(
                           attrs={
                               'class': 'form-control',
                               'placeholder': 'Length greather than or equal to'
                           }))
    class Meta:
        model = Vehicle
        fields = [
            'name', 'length'
        ]