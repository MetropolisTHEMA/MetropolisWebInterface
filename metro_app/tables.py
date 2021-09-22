import django_tables2 as tables
from .models import Edge


class EdgeTable(tables.Table):
    class Meta:
        model = Edge
        fields = ('name',
                  'source',
                  'target',
                  'lanes',
                  'length',
                  'speed',
                  'param1',
                  'param2',
                  'param3',
                  )
