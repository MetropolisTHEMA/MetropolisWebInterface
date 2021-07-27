import django_filters
from .models import Edge

class EdgeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Edge
        fields = [
            'name',
            'length',
            'speed',
        ]
