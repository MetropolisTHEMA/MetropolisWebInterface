import django_filters
from django_filters import CharFilter
from .models import Edge


class EdgeFilter(django_filters.FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    lanes = CharFilter(field_name='lanes', lookup_expr='gte')
    speed = CharFilter(field_name='speed', lookup_expr='gte')

    class Meta:
        model = Edge
        fields = [
            'name',
            'lanes',
            'speed',
        ]
