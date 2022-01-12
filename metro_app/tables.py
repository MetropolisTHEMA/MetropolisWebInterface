import django_tables2 as tables
from .models import Edge, Node, RoadType, Zone, ODPair


class EdgeTable(tables.Table):

    class Meta:
        model = Edge
        """attrs = {'class': 'table table-striped table-condensed',
                 'data-toggle': 'table',
                 'data-show-columns': 'true',
                 'data-show-toggle': 'true',
                 }"""
        fields = ('edge_id', 'name', 'source', 'target', 'road_type',
                  'lanes', 'length', 'speed', 'outflow',
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
        fields = ('road_type_id', 'name', 'congestion',
                  'default_speed', 'default_lanes',
                  'default_outflow',
                  'default_param1', 'default_param2',
                  'default_param3', 'color')


class ZoneTable(tables.Table):
    centroid = tables.Column(accessor='location')

    class Meta:
        model = Zone
        fields = ('zone_id', 'name', 'radius', 'centroid')


class ODPairTable(tables.Table):

    class Meta:
        model = ODPair
        fields = ('origin', 'destination', 'size')
