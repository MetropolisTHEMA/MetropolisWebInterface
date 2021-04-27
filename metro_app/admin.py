from django.contrib.gis import admin
from .models import *

@admin.register(Project)
class ProjectAdmin(admin.OSMGeoAdmin):
    pass

@admin.register(File)
class FileAdmin(admin.OSMGeoAdmin):
    pass

@admin.register(ParameterSet)
class ParameterSetAdmin(admin.OSMGeoAdmin):
    pass

@admin.register(RoadNetwork)
class RoadNetworkAdmin(admin.OSMGeoAdmin):
    pass

@admin.register(RoadType)
class RoadTypeAdmin(admin.OSMGeoAdmin):
    pass
    
@admin.register(Node)
class NodeAdmin(admin.OSMGeoAdmin):
    pass

@admin.register(Edge)
class EdgeAdmin(admin.OSMGeoAdmin):
    pass

@admin.register(Population)
class PopulationAdmin(admin.OSMGeoAdmin):
    pass

@admin.register(ODMatrix)
class ODMatrixAdmin(admin.OSMGeoAdmin):
    pass

@admin.register(PopulationSegment)
class PopulationSegmentAdmin(admin.OSMGeoAdmin):
    pass

@admin.register(Preferences)
class PreferencesAdmin(admin.OSMGeoAdmin):
    pass

@admin.register(Zone)
class ZoneAdmin(admin.OSMGeoAdmin):
    pass

@admin.register(ODPair)
class ODPairAdmin(admin.OSMGeoAdmin):
    pass
