import django_tables2 as tables
from .models import Edge, Node, RoadType


class EdgeTable(tables.Table):

    class Meta:
        model = Edge
        """attrs = {'class': 'table table-striped table-condensed',
                 'data-toggle': 'table',
                 'data-show-columns': 'true',
                 'data-show-toggle': 'true',
                 }"""
        fields = ('edge_id', 'name', 'source', 'target', 'road_type',
                  'lanes', 'length', 'speed',
                  'param1', 'param2', 'param3',
                  )
        # 'data-pagination': 'true',
        # 'data-side-pagination': 'server',
        # 'data-page-size': "15",
        # 'data-page-list': "[15, 30, 45, All]",
        # 'data-show-pagination-switch': 'true',
        # 'data-search': 'true',
        # 'data-search-align': 'left',
        # 'data-show-columns': 'true',
        # 'data-show-toggle': 'true',
        # 'data-cache': 'false',
        # 'data-show-refresh': 'true',
        # 'data-show-fullscreen': 'true',
        # "th": {"data-sortable": "true"},  # sorting column


class NodeTable(tables.Table):

    class Meta:
        model = Node
        fields = ('node_id', 'name', 'location')


class RoadTypeTable(tables.Table):

    class Meta:
        model = RoadType
        fields = ('road_type_id', 'name', 'congestion', 'speed')
