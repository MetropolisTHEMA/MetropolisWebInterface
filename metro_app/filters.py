import django_filters
from django_filters import CharFilter, NumberFilter
from .models import Edge, Node, RoadType, RoadNetwork, Zone, ODPair
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
