"""
Django Models Modules
=====================
Note: Please note that the models module is imported from django.contrib.gis.db
and not the usual django.db module.

All model relationship create dependencies between one another, so an important
behavior is
what happens to the other party when one party is removed. The on_delete option
is designed
for this purpose, to determine what to do with records on the other side of a
relationship
when one side is removed. The on_delete option is available for all three
relationship model
data types. Here is an exellent book about this topic
https://www.webforefront.com/django/setuprelationshipsdjangomodels.html
"""

import os
import random
from datetime import timedelta
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from colorfield.fields import ColorField
from django_q.tasks import fetch


def get_sentinel_user():
    return User.objects.get_or_create(username='deleted')[0]


def get_visualization_directory():
    return os.path.join(settings.TEMPLATES[0]['DIRS'][0], 'visualization')


class Project(models.Model):
    """Projects are containers used to store input models, runs and output
    models in a coherent and organized manner.

    Each user can create multiple projects and each project can be shared
    between multiple users.
    The creator of the project is the owner. He can decide to add or remove
    users to the project.

    :owner User: The user who created and owns the project.
    :members set of User: Set of users who can view and modify the
     project.
    :public bool: If True, the project can be viewed (but not modified) by
     anyone (default is False).
    :name str: Name of the project.
    :comment str: Description of the project (default is '').
    :tags set of str: Tags describing the instance, used to search and filter
     the instances.
    :date_created datetime.date: Creation date of the Project.
    """
    owner = models.ForeignKey(User, related_name='owner',
                              on_delete=models.SET(get_sentinel_user))
    members = models.ManyToManyField(User, related_name='members',
                                     through='Membership')
    public = models.BooleanField(default=False, help_text='Allow the project \
                                 to be viewed (not editable) by anyone')
    name = models.CharField(max_length=80, help_text='Name of the project')
    comment = models.CharField(max_length=240, blank=True,
                               help_text='Additional comment for the project')
    tags = models.CharField(max_length=240, blank=True)
    date_created = models.DateField(auto_now_add=True,
                                    help_text='Creation date of the project')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Project'


class Membership(models.Model):
    """Membership defines a relation between an user and a project.

    This model represents a many-to-many relation between projects and users.
    An entry indicates that a user is a member of a project. The permissions of
    the user for this project are stored here.

    :user User: The user who is a member of the project.
    :project Project: The project for which the user is a member of.
    :can_add bool: If True, the user can add new input data (default is True).
    :can_delete bool: If True, the user can delete input data (default is
     True).
    :can_run bool: If True, the user can run simulations (default is True).
    :can_add_members bool: If True, the user can add new members (default is
     False).
    :can_manage_perms bool: If True, the user can manage members' permissions
     (default is False).
    :can_remove_members bool: If True, the user can remove members (default is
     False).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    can_add = models.BooleanField(
        default=True, help_text='The member can add new input data')
    can_delete = models.BooleanField(
        default=True, help_text='The member can delete input data')
    can_run = models.BooleanField(
        default=True, help_text='The member can run simulations')
    can_add_members = models.BooleanField(
        default=False, help_text='The member can add new members')
    can_manage_perms = models.BooleanField(
        default=False, help_text='The member can manage permissions')
    can_remove_members = models.BooleanField(
        default=False, help_text='The member can remove members')

    def __str__(self):
        return '{} is a member of {}'.format(self.user, self.project)

    class Meta:
        db_table = 'Membership'


def project_directory_path(instance, filename):
    return 'project_files/{}/{}'.format(instance.project.id, filename)


class File(models.Model):
    """File shared by the users of a project.

    :project Project: Project the file belongs to.
    :public bool: if True, the file can be viewed by anyone (only if the
     project is also public.
    :title str: Title of the file, as shown on the interface.
    :location FieldFile: Location of the file on the server.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    public = models.BooleanField(
        default=False, help_text='Allow the file to be viewable by anyone')
    title = models.CharField(max_length=80, help_text='Title of the file')
    location = models.FileField(verbose_name='File',
                                upload_to=project_directory_path)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'File'


class ParameterSet(models.Model):
    """Set of technical parameters used for a run.

    :project Project: Project the ParameterSet instance belongs to.
    :period_start timedelta: Earliest possible departure time (expressed as
     time since midnight).
    :period_end timedelta: Latest possible departure time (expressed as time
     since midnight).
    :period_interval  timedelta: Interval at which link-specific results are
     recorded.
    :learn_process str: Type of learning process for the day-to-day model.
     Possible values are exponential, linear, quadratic and genetic.
    :learn_param float: Weight of the previous day in the learning process. The
     exact meaning depends on the type of learning process.
    :iter_check bool: If True, the run stops when the maximum number of
     iterations is exceeded.
    :iter_value int: Maximum number of iterations of the run.
    :converg_check bool: If True, ther run stops when the convergence criteria
     is smaller than the threshold value.
    :converg_value float: Threshold of the convergence criteria.
    :spillback_enable bool: If True, congestion can spread on upstream links
     (i.e., queues are horizontal, not vertical).
    :spillback_value float: Length of a base vehicle, in meters. Used to
     compute the length of the trafic jams. Only relevant if spillback_enable
     is True.
    :locked bool: If True, the instance cannot be modified (default is False).
    :name str: Name of the instance.
    :comment str: Description of the instance.
    :tags set of str: Tags describing the instance, used to search and filter
     the instances.
    :date_created datetime.date: Creation date of the ParameterSet.
    """
    learning_process = (
        (0, 'exponential'),
        (1, 'linear'),
        (2, 'quadratic'),
        (3, 'genetic')
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    period_start = models.DurationField(
        help_text='Starting time of the simulated period')
    period_end = models.DurationField(
        help_text='Ending time of the simulated period')
    period_interval = models.DurationField(
        default=timedelta(minutes=5),
        help_text='Time interval at which results are saved',
    )
    learn_process = models.PositiveSmallIntegerField(
        default=0, choices=learning_process,
        help_text='Type of learning process')
    learn_param = models.FloatField(
        default=.1, help_text='Weight of the previous day')
    iter_check = models.BooleanField(
        default=True,
        help_text=(
            'Stop the simulation when the maximum number of iterations is'
            ' exceeded'
        ),
    )
    iter_value = models.SmallIntegerField(
        default=50, help_text='Maximum number of iterations')
    converg_check = models.BooleanField(
        default=True,
        help_text=(
            'Stop the simulation when the convergence criteria is reached'
        ),
    )
    converg_value = models.FloatField(
        default=.01, help_text='Value of the convergence criteria')
    spillback_enable = models.BooleanField(
        default=True, help_text='Allow congestion to spread on upstream roads')
    spillback_value = models.FloatField(
        default=7.0, help_text='Length of a vehicle in meters')
    locked = models.BooleanField(default=False)
    name = models.CharField(
        max_length=80, help_text='Name of the parameter set')
    comment = models.CharField(
        max_length=240, blank=True,
        help_text='Additional comment for the parameter set',
    )
    tags = models.CharField(max_length=240, blank=True)
    date_created = models.DateField(
        auto_now_add=True, help_text='Creation date of the parameter set')

    def __str__(self):
        return self.name

    def get_learning_model(self):
        if self.learn_process == 0:
            return {
                'Exponential': {
                    'alpha': self.learn_param,
                }
            }
        else:
            raise 'Unsupported learning process: {}'.format(self.learn_process)

    def get_convergence_criteria(self):
        criteria = []
        if self.iter_check:
            criteria.append({'MaxIteration': self.iter_value})
        assert len(criteria) > 0, \
               'At least one convergence criteria must be enabled'
        return criteria

    class Meta:
        db_table = 'ParameterSet'


class RoadNetwork(models.Model):
    """Container storing the graph-representation of a road network.
    A road network is composed of a set of nodes and of a set of edges
    connecting the nodes.
    Road types are used to describe the congestion model of the roads.

    :project Project: Project the RoadNetwork instance belongs to.
    :simple bool: If True, the coordinates of the nodes are abstract.
     Otherwise, the coordinates of the nodes are expressed in a real coordinate
     system.
    :locked bool: If True, the instance cannot be modified (default is False).
    :visualization_path file: Location on the server of the HTML file with the
     Leaflet.js representation of the road network.
    :nb_road_types int: Total number of roadtypes in the road network.
    :nb_nodes int: Total number of nodes in the road network.
    :nb_edges int: Total number of edges in the road network.
    :srid str: Spatial Reference System Identifier used for the coordinates of
     the nodes and the geometry of the edges.
    :name str: Name of the instance.
    :comment str: Description of the instance.
    :tags set of str: Tags describing the instance, used to search and filter
     the instances.
    :date_created datetime.date: Creation date of the Road Network.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    simple = models.BooleanField(
        default=False, verbose_name='Abstract network',
        help_text=(
            'Abstract networks are networks that cannot be expressed in a'
            ' geographic projection'
        ),
    )
    locked = models.BooleanField(default=False)
    visualization_path = models.FilePathField(
        path=get_visualization_directory, match='*.html')
    nb_road_types = models.PositiveIntegerField(default=0)
    nb_nodes = models.PositiveIntegerField(default=0)
    nb_edges = models.PositiveIntegerField(default=0)
    srid = models.PositiveIntegerField(
        default=4326,
        help_text=(
            'Spatial Reference System Identifier used for the coordinates of'
            ' the network nodes and edges'
        ),
    )
    name = models.CharField(
        max_length=80, help_text='Name of the road network')
    comment = models.CharField(
        max_length=240, blank=True,
        help_text='Additional comment for the road network',
    )
    tags = models.CharField(max_length=240, blank=True)
    date_created = models.DateField(
        auto_now_add=True, help_text='Creation date of the road network')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'RoadNetwork'


class RoadType(models.Model):
    """Congestion model for a set of edges.

    :network RoadNetwork: RoadNetwork the RoadType instance belongs to.
    :road_type_id int: Id of the road type, as used by the users in the import
     files. Must be unique for a specific RoadNetwork.
    :name str: Name of the road type (default is '').
    :congestion str: Congestion model used to compute the travel time of the
     edges. Possible values are free flow, bottleneck, log-density, bureau of
     public roads function and linear.
    :default_speed float: Default free-flow speed of the edges for this road
     type, in kilometers per hour.
    :default_lanes int: Default number of lanes for this road type.
    :default_outflow float: Default outflow of the bottleneck at the end of the
     edge (in meters of vehicles per lane per hour)
    :default_param1 float: Default value for the first parameter used in the
     congestion model. The exact meaning depends on the congestion model.
    :default_param2 float: Default value for the second parameter used in the
     congestion model. The exact meaning depends on the congestion model.
    :default_param3 float: Default value for the third parameter used in the
     congestion model. The exact meaning depends on the congestion model.
    :color Color: Color used to display the edges of this road type on the
     network visualization.
    """
    BOTTLENECK = 0
    FREEFLOW = 1
    LOGDENSITY = 2
    BPR = 3
    LINEAR = 4
    CONGESTION_CHOICES = (
        (BOTTLENECK, 'Bottleneck'),
        (FREEFLOW, 'FreeFlow'),
        (LOGDENSITY, 'LogDensity'),
        (BPR, 'BureauOfPublicRoads'),
        (LINEAR, 'Linear'),
    )
    network = models.ForeignKey(RoadNetwork, on_delete=models.CASCADE)
    road_type_id = models.PositiveIntegerField(
        db_index=True, help_text='Id of the road type (must be unique)')
    name = models.CharField(max_length=80, blank=True,
                            help_text='Name of the road type')
    congestion = models.SmallIntegerField(
        default=0, choices=CONGESTION_CHOICES)
    default_speed = models.FloatField(default=50)
    default_lanes = models.SmallIntegerField(default=1)
    default_outflow = models.FloatField(null=True, blank=True)
    default_param1 = models.FloatField(null=True, blank=True)
    default_param2 = models.FloatField(null=True, blank=True)
    default_param3 = models.FloatField(null=True, blank=True)
    color = ColorField(null=True, blank=True)

    def __str__(self):
        return '{} - ({})'.format(self.road_type_id, self.name)
        # return self.name or 'Roadtype {}'.format(self.road_type_id)

    class Meta:
        db_table = 'RoadType'


class Node(models.Model):
    """A Node is an element of the road-network graph, representing an
    intersection or an origin / destination point.

    :network: RoadNetwork instance the Node belongs to.
     The first argument "RoadNetwork" indicate the relationship model.
    :node_id int: Id of the node, as used by the users in the import files.
     Must be unique for a specific RoadNetwork.
    :name str: Name of the node (default is '').
    :location Point: Point representing the location of the node on the
     network, in EPSG:4326.
    """
    network = models.ForeignKey(RoadNetwork, on_delete=models.CASCADE)
    node_id = models.PositiveBigIntegerField(
        db_index=True, help_text='Id of the node (must be unique)')
    name = models.CharField(
        max_length=80, blank=True, help_text='Name of the node')
    location = models.PointField()

    def __str__(self):
        return '{} - ({})'.format(self.node_id, self.name)
        # return self.name or 'Node {}'.format(self.node_id)

    class Meta:
        db_table = 'Node'


class Edge(models.Model):
    """An Edge is an element of the road-network graph, representing road
    sections or connectors (between an origin / destination and the network).

    :network RoadNetwork: RoadNetwork the Node instance belongs to.
    :source Node: Node representing the starting point of the edge.
    :target Node: Node representing the ending point of the edge.
    :road_type RoadType: Road type representing the congestion model of the
     edge.
    :edge_id int: Id of the edge, as used by the users in the import files.
     Must be unique for a specific RoadNetwork.
    :name str: Name of the edge (default is '').
    :geometry LineString: Exact or approximate representation of the geometry
     of the edge as a sequence of points, in EPSG:4326 (default is a straight
     line between source and target node).
    :length float: Length of the edge, in kilometers.
    :speed float: Free-flow speed of the link, in kilometers per hour. The
     default speed for the given road type is used if empty.
    :lanes int: Number of lanes on the edge. The default number of lanes for
     the given road type is used if empty.
    :outflow float: Outflow of the bottleneck at the end of the edge (in meters
     of vehicles per lane per hour)
    :param1 float: Parameter used to compute the travel time of the edge. The
     exact meaning depends on the congestion model. The default value for the
     given road type is used if empty.
    :param2 float: Parameter used to compute the travel time of the edge. The
     exact meaning depends on the congestion model. The default value for the
     given road type is used if empty.
    :param3 float: Parameter used to compute the travel time of the edge. The
     exact meaning depends on the congestion model. The default value for the
     given road type is used if empty.
    """
    network = models.ForeignKey(RoadNetwork, on_delete=models.CASCADE)
    source = models.ForeignKey(Node, related_name='source',
                               verbose_name='from',
                               on_delete=models.CASCADE,
                               help_text='Source node of the edge',
                               )
    target = models.ForeignKey(Node, related_name='target',
                               verbose_name='to',
                               on_delete=models.CASCADE,
                               help_text='Target node of the edge',
                               )
    road_type = models.ForeignKey(RoadType, on_delete=models.CASCADE,
                                  help_text='Roadtype of the edge'
                                  )
    edge_id = models.PositiveBigIntegerField(
        db_index=True, help_text='Id of the edge (must be unique)')
    name = models.CharField(
        max_length=80, blank=True, null=True, help_text='Name of the edge')
    geometry = models.LineStringField()
    length = models.FloatField()
    speed = models.FloatField(null=True, blank=True)
    lanes = models.SmallIntegerField(null=True, blank=True)
    outflow = models.FloatField(null=True, blank=True)
    param1 = models.FloatField(null=True, blank=True)
    param2 = models.FloatField(null=True, blank=True)
    param3 = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name or 'Edge {}'.format(self.edge_id)

    class Meta:
        db_table = 'Edge'

    def get_lanes(self):
        return self.lanes or self.road_type.default_lanes

    def get_speed(self):
        return self.speed or self.road_type.default_speed

    def get_length_decimal_places(self):
        return "{:.3}".format(self.length)

    def get_length_in_km(self):
        return self.length

    def get_length_in_meters(self):
        return self.length * 1000.0

    def get_outflow(self):
        return self.outflow or self.road_type.default_outflow

    def get_param1(self):
        return self.param1 or self.road_type.default_param1

    def get_param2(self):
        return self.param2 or self.road_type.default_param2

    def get_param3(self):
        return self.param3 or self.road_type.default_param3


def get_random_seed():
    return random.randint(0, 1000)


class Population(models.Model):
    """A Population represents a set of agents, with given characteristics,
    whose preferences and decisions are simulated.

    A Population is composed of two parts:
    - A set of population segments representing each an origin-destination
      matrix of agents with a given distribution of preferences.
    - A set of agents with given origin, destination and preferences, generated
      according to the population segments.

    :generated bool: If True, indicate that the set of agents corresponding to
     the population segments has been generated.
    :locked bool: If True, the instance cannot be modified (default is False).
    :random_seed int: Seed for the random number generator used to generate the
     agents (default is a random integer).
    :name str: Name of the instance.
    :comment str: Description of the instance (default is '').
    :tags set of str: Tags describing the instance, used to search and filter
     the instances.
    :date_created datetime.date: Creation date of the Population.
    """
    generated = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    random_seed = models.PositiveIntegerField(get_random_seed)
    name = models.CharField(max_length=80, help_text='Name of the Population')
    comment = models.CharField(
        max_length=240, blank=True,
        help_text='Additional comment for the Population',
    )
    tags = models.CharField(max_length=240, blank=True)
    date_created = models.DateField(
        auto_now_add=True, help_text='Creation date of the population')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Population'


class ZoneSet(models.Model):
    """Set of zones.

    :project Project: Project the ZoneSet instance belongs to.
    :locked bool: If True, the instance cannot be modified (default is False).
    :srid str: Spatial Reference System Identifier used for the coordinates of
     the zones.
    :name str: Name of the instance.
    :comment str: Description of the instance (default is '').
    :tags set of str: Tags describing the instance, used to search and filter
     the instances.
    :date_created datetime.date: Creation date of the ZoneSet.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    locked = models.BooleanField(default=False)
    srid = models.PositiveIntegerField(
        default=4326,
        help_text=(
            'Spatial Reference System Identifier used for the coordinates of'
            ' the zones in the ZoneSet'
        ),
    )
    name = models.CharField(max_length=80, help_text='Name of the ZoneSet')
    comment = models.CharField(
        max_length=240, blank=True,
        help_text='Additional comment for the ZoneSet',
    )
    tags = models.CharField(max_length=240, blank=True)
    date_created = models.DateField(
        auto_now_add=True, help_text='Creation date of the ZoneSet')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'ZoneSet'


class Zone(models.Model):
    """Point or area representing the origin or destination of agents.

    Zones can be defined in two ways:
    - As a circle, with a given center and radius (zero for points).
    - As an area defined by a polygon.

    :zone_id int: Id of the zone, as used by the users in the import files.
     Must be unique for a specific ODMatrix.
    :zone_set ZoneSet: ZoneSet instance the zone belongs to.
    :centroid Point: Center point of the circle or centroid of the area.
    :geometry Polygon: Polygon representing the zone, if it is an area.
    :radius float: Radius of the zone in meters, if it is a circle.
    :name str: Name of the zone (default is '').
    """
    zone_id = models.PositiveBigIntegerField(
        db_index=True, help_text='Id of the zone')
    zone_set = models.ForeignKey(ZoneSet, on_delete=models.CASCADE)
    centroid = models.PointField(null=True, blank=True)
    geometry = models.PolygonField(null=True, blank=True)
    radius = models.FloatField(null=True, blank=True)
    name = models.CharField(null=True, max_length=80, blank=True,
                            help_text='Name of the zone')

    def __str__(self):
        return "{} - ({})".format(self.zone_id, self.name)
        # return self.name or 'Zone {}'.format(self.zone_id)

    def location(self):
        return str(self.centroid).split(';')[1]

    class Meta:
        db_table = 'Zone'


class ODMatrix(models.Model):
    """Origin-destination matrix representing the origin and destination for a
    set of agents.

    :project Project: Project the ODMatrix instance belongs to.
    :zone_set ZoneSet: ZoneSet used to describe the origins and destinations of
     the matrix.
    :size int: Total number of agents in the origin-destination matrix.
    :locked bool: If True, the instance cannot be modified (default is False).
    :name str: Name of the instance.
    :comment str: Description of the instance (default is '').
    :tags set of str: Tags describing the instance, used to search and filter
     the instances.
    :date_created datetime.date: Creation date of the ODMatrix.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    zone_set = models.ForeignKey(ZoneSet, on_delete=models.CASCADE)
    size = models.PositiveIntegerField(
        default=0, help_text='Total number of agents in the OD matrix')
    locked = models.BooleanField(default=False)
    name = models.CharField(max_length=80, help_text='Name of the O-D matrix')
    comment = models.CharField(
        max_length=240, blank=True,
        help_text='Additional comment for the O-D matrix',
    )
    tags = models.CharField(max_length=240, blank=True)
    date_created = models.DateField(
        auto_now_add=True, help_text='Creation date of the O-D matrix')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'ODMatrix'


class Preferences(models.Model):
    """Distribution of preferences describing a set of agents.

    :project Project: Project the Preferences instance belongs to.
    ...
    :locked bool: If True, the instance cannot be modified (default is False).
    :name str: Name of the instance.
    :comment str: Description of the instance (default is '').
    :tags set of str: Tags describing the instance, used to search and filter
     the instances.
    :date_created datetime.date: Creation date of the Preferences.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    locked = models.BooleanField(default=False)
    name = models.CharField(max_length=80, help_text='Name of the Preferences')
    comment = models.CharField(
        max_length=240, blank=True,
        help_text='Additional comment for the Preferences',
    )
    tags = models.CharField(max_length=240, blank=True)
    date_created = models.DateField(
        auto_now_add=True, help_text='Creation date of the preferences')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Preferences'


class PopulationSegment(models.Model):
    """Representation of a set of agents that can be represented with an
    origin-destination matrix and a distribution of preferences.

    :population Population: Population the PopulationSegment is a part of.
    :preferences Preferences: Preferences instance representing the
     distribution of preferences for this population segment.
    :od_matrix ODMatrix: ODMatrix instance representing the origin-destination
     matrix for this population segment.
    :name str: Name of the instance.
    :comment str: Description of the instance (default is '').
    :tags set of str: Tags describing the instance, used to search and filter
     the instances.
    :date_created datetime.date: Creation date of the PopulationSegment.
    """
    population = models.ForeignKey(Population, on_delete=models.CASCADE)
    preferences = models.ForeignKey(Preferences, on_delete=models.CASCADE)
    od_matrix = models.ForeignKey(ODMatrix, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=80, help_text='Name of the population segment')
    comment = models.CharField(
        max_length=240, blank=True,
        help_text='Additional comment for the population segment',
    )
    tags = models.CharField(max_length=240, blank=True)
    date_created = models.DateField(
        auto_now_add=True, help_text='Creation date of the population segment')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'PopulationSegment'


class ODPair(models.Model):
    """Single origin-destination pair of an ODMatrix.

    :matrix ODMatrix: ODMatrix the ODPair belongs to.
    :origin Zone: Origin zone for the OD pair.
    :destination Zone: Destination zone for the OD pair.
    :size int: Number of agents with the given origin and destination.
    """
    matrix = models.ForeignKey(ODMatrix, on_delete=models.CASCADE)
    origin = models.ForeignKey(
        Zone, related_name='origin', on_delete=models.CASCADE)
    destination = models.ForeignKey(
        Zone, related_name='destination', on_delete=models.CASCADE)
    size = models.PositiveIntegerField()

    class Meta:
        db_table = 'ODPair'


class Run(models.Model):
    """Class to represent a run of MetroSim.

    :project Project: Project the Run instance belongs to.
    :parameter_set ParameterSet: ParameterSet used for the run.
    :population Population: Population used for the run.
    :policy Policy: Policy used for the run.
    :road_network RoadNetwork: RoadNetwork used for the run.
    :pt_network PTNetwork: PTNetwork used for the run.
    :status str: Status of the run. Possible values are 'Not ready', 'Ready',
     'In progress', 'Finished', 'Aborted' and 'Failed'.
    :name str: Name of the instance (default is '').
    :comment str: Description of the instance (default is '').
    :tags set of str: Tags describing the instance, used to search and filter
     the instances.
    :start_date datetime.datetime: Starting time of the run.
    :end_date datetime.datetime: Ending time of the run.
    :time_taken timedelta: Total running time of the run.
    :iterations int: Number of iterations of the run.
    :date_created datetime.date: Creation date of the Run.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE)
    population = models.ForeignKey(Population, on_delete=models.CASCADE)
    #  policy = models.ForeignKey(
    #      Policy, on_delete=models.CASCADE, null=True, blank=True)
    network = models.ForeignKey(
        RoadNetwork, on_delete=models.CASCADE, null=True, blank=True)
    #  pt_network = models.ForeignKey(
    #      PTNetwork, on_delete=models.CASCADE, null=True, blank=True)
    status_choices = (
        (0, 'Not ready'),
        (1, 'Ready'),
        (2, 'In progress'),
        (3, 'Finished'),
        (4, 'Aborted'),
        (5, 'Failed'),
    )
    status = models.PositiveSmallIntegerField(
        default=0, choices=status_choices)
    name = models.CharField(
        max_length=80, help_text='Name of the run')
    comment = models.CharField(
        max_length=240, blank=True,
        help_text='Additional comment for the run',
    )
    tags = models.CharField(max_length=240, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    time_taken = models.DurationField(null=True, blank=True)
    iterations = models.PositiveSmallIntegerField(null=True, blank=True)
    date_created = models.DateField(auto_now_add=True,
                                    help_text='Creation date of the run')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Run'


class NodeResults(models.Model):
    """Class to hold results of MetroSim for a specific node of the road
    network.

    :node Node: Node instance for which the NodeResults is created.
    :run Run: Run instance from which the results are coming.
    :upstream Edge: Edge whose target is node.
    :downstream Edge: Edge whose source is node.
    :time datetime.time: Center of the time window for which results are
     computed.
    :vehicles int: Number of vehicles who crossed the node, from edge upstream
     to edge downstream during the time window.
    :crossing_time timedelta: Average crossing time of the vehicles during the
     time window.
    """
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    upstream = models.ForeignKey(
        Edge, related_name='upstream', on_delete=models.CASCADE)
    downstream = models.ForeignKey(
        Edge, related_name='downstream', on_delete=models.CASCADE)
    time = models.TimeField()
    vehicles = models.IntegerField()
    crossing_time = models.DurationField()

    class Meta:
        db_table = 'NodeResults'


class EdgeResults(models.Model):
    """Class to hold results of MetroSim for a specific edge of the road
    network.

    :edge Edge: Edge instance for which the EdgeResults is created.
    :run Run: Run instance from which the results are coming.
    :time datetime.time: Center of the time window for which results are
     computed.
    :congestion float: Average congestion level on the edge during the time
     window, in percentage.
    :travel_time timedelta: Average travel time of the edge during the time
     window.
    :speed real: Average speed on the edge during the time window, in
     kilometers per hour.
    """
    edge = models.ForeignKey(Edge, on_delete=models.CASCADE)
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    time = models.TimeField()
    congestion = models.FloatField()
    travel_time = models.DurationField()
    speed = models.FloatField()

    def __str__(self):
        return "{}".format(self.run)

    class Meta:
        db_table = 'EdgesResults'


class VehicleSet(models.Model):
    """A set of Vehicles.

    :project Project: Project the VehicleSet instance belongs to.
    :locked bool: If True, the instance cannot be modified (default is False).
    :name str: Name of the instance.
    :comment str: Description of the instance (default is '').
    :tags set of str: Tags describing the instance, used to search and filter
     the instances.
    :date_created datetime.date: Creation date of the VehicleSet.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    locked = models.BooleanField(default=False)
    name = models.CharField(max_length=80, help_text='Name of the VehicleSet')
    comment = models.CharField(
        max_length=240, blank=True,
        help_text='Additional comment for the VehicleSet',
    )
    tags = models.CharField(max_length=240, blank=True)
    date_created = models.DateField(
        auto_now_add=True, help_text='Creation date of the VehicleSet')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'VehicleSet'


class Vehicle(models.Model):
    """A Vehicle is an element of the road-network graph, representing a class
    of vehicle moving on the network.

    :network: RoadNetwork instance the Vehicle belongs to.
    :vehicle_id int: Id of the Vehicle, as used by the users in the import
     files.
     Must be unique for a specific RoadNetwork.
    :name str: Name of the Vehicle (default is '').
    :length float: Front-to-front length of the Vehicle (in meters).
    :speed_multiplicator float: Optional. If not None, the free-flow speed of
    the vehicle on an edge is the base speed on the edge multiplied by this
    value.
    :speed_function 2-D array of float: Optional. If not None, it must be an
    array of [float, float] arrays where the first value represents the base
    speed and the second value represents the actual speed of the vehicle for
    this base speed.
    """
    vehicle_id = models.PositiveBigIntegerField(
        db_index=True, help_text='Id of the vehicle (must be unique)')
    name = models.CharField('Name',
        max_length=80, blank=True, help_text='Name of the vehicle')
    length = models.FloatField(help_text='Length of the vehicle (meters)')
    speed_multiplicator = models.FloatField(null=True, blank=True)
    speed_function = ArrayField(
        ArrayField(
            models.FloatField(),
            size=2,
        ),
        size=20,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name or 'Vehicle {}'.format(self.vehicle_id)

    def get_speed_function(self):
        if self.speed_multiplicator:
            {'Multiplicator': self.speed_multiplicator}
        elif len(self.speed_function) > 0:
            {'Piecewise': self.speed_function}
        else:
            'Base'

    class Meta:
        db_table = 'Vehicle'


class Agent(models.Model):
    """Generated agent ready to be used by MetroSim.

    :agent_id int: Id of the agent, as used by the users in the import files.
     Must be unique for a specific Population.
    :population Population: Population instance the Agent belongs to.
    :origin_zone Zone: Zone used as the origin of the agent for his trips.
    :destination_zone Zone: Zone used as the destination of the agent for his
     trips.
    :mode_choice_model int: Type of mode-choice model for the agent (either
     deterministic or logit).
    :mode_choice_u float: Random value 0 <= u < 1 for the mode choice.
    :mode_choice_mu float: Variance of the error term for a Logit mode-choice
     model.
    :t_star timedelta: Desired arrival at destination (or departure from
     origin) of the agent (expressed as a duration since midnight).
    :delta timedelta: Length of the desired arrival / departure time period.
    :beta float: Penalty for early arrivals / departures (in utility / hour).
    :gamma float: Penalty for late arrivals / departures (in utility / hour).
    :desired_arrival bool: If True, t_star represents a desired arrival time at
     destination, otherwise it represents a desired departure time from origin.
    :vehicle Vehicle: Vehicle used by the agent for car trips.
    :dep_time_car_u float: Random value 0 <= u < 1 for the car departure-time
     choice.
    :dep_time_car_mu float: Variance of the error term in the car
     departure-time choice model.
    :car_vot float: Value of time in a car (in utility / hour).
    :origin_stop PTStop: PTStop of the public-transit network used as the
     origin of the agent for public-transit trips.
    :destination_stop PTStop: PTStop of the public-transit network used as the
     destination of the agent for public-transit trips.
    """
    agent_id = models.PositiveBigIntegerField(
        db_index=True, help_text='Id of the agent')
    population = models.ForeignKey(Population, on_delete=models.CASCADE)
    # Origin - destination.
    origin_zone = models.ForeignKey(
        Zone, related_name='origin_zone', on_delete=models.CASCADE,
        help_text='Origin zone of the agent',
    )
    destination_zone = models.ForeignKey(
        Zone, related_name='destination_zone', on_delete=models.CASCADE,
        help_text='Destination zone of the agent',
    )
    # Mode-choice parameters.
    DETERMINISTIC = 0
    LOGIT = 1
    MODE_CHOICES = (
        (DETERMINISTIC, 'Deterministic'),
        (LOGIT, 'Logit'),
    )
    mode_choice_model = models.SmallIntegerField(
        default=0, choices=MODE_CHOICES)
    mode_choice_u = models.FloatField()
    mode_choice_mu = models.FloatField(blank=True, null=True)
    # Schedule utility parameters.
    t_star = models.DurationField()
    delta = models.DurationField(default=timedelta())
    beta = models.FloatField()
    gamma = models.FloatField()
    desired_arrival = models.BooleanField(default=True)
    # Car mode.
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, help_text='Vehicle of the agent')
    dep_time_car_u = models.FloatField()
    dep_time_car_mu = models.FloatField()
    car_vot = models.FloatField

    def __str__(self):
        return 'Agent {}'.format(self.agent_id)

    def get_car_dep_time_model(self):
        return {
            'Logit': {
                'u': self.dep_time_car_u,
                'mu': self.dep_time_car_mu,
            }
        }

    def get_car_utility_model(self):
        return {
            'Proportional': {
                'alpha': self.car_vot,
            }
        }

    def get_mode_choice_model(self):
        if self.mode_choice_model == self.DETERMINISTIC:
            return {
                'Deterministic': {
                    'u': self.mode_choice_u,
                }
            }
        else:
            return {
                'Logit': {
                    'u': self.mode_choice_u,
                    'mu': self.mode_choice_mu,
                }
            }

    def get_schedule_delay_utility(self):
        return {
            'AlphaBetaGammaModel': {
                't_star_low': max(
                    0, (self.t_star - self.delta / 2).total_seconds()),
                't_star_high': (self.t_star + self.delta / 2).total_seconds(),
                'beta': self.beta,
                'gamma': self.gamma,
                'desired_arrival': self.desired_arrival,
            }
        }

    def get_origin_node(self, road_network):
        try:
            relation = ZoneNodeCorrespondance.objects.get(
                zone_set=self.origin_zone.zone_set, road_network=road_network)
        except ZoneNodeCorrespondance.DoesNotExist:
            return None
        try:
            link = self.origin_zone.zonenoderelation_set.get(relation=relation)
        except ZoneNodeRelation.DoesNotExist:
            return None
        return link.node

    def get_destination_node(self, road_network):
        try:
            relation = ZoneNodeCorrespondance.objects.get(
                zone_set=self.destination_zone.zone_set,
                road_network=road_network)
        except ZoneNodeCorrespondance.DoesNotExist:
            return None
        try:
            link = self.destination_zone.zonenoderelation_set.get(
                relation=relation)
        except ZoneNodeRelation.DoesNotExist:
            return None
        return link.node

    class Meta:
        db_table = 'Agent'


class AgentResults(models.Model):
    """Class to hold results of MetroSim for a specific agent.

    :agent Agent: Agent instance for which the AgentResults is created.
    :run Run: Run instance from which the results are coming.
    :mode str: Mode chosen by the agent for the last iteration. Possible values
     are private vehicle, public transit and walking.
    :departure_time datetime.time: Departure time of the agent for the last
     iteration.
    :arrival_time datetime.time: Arrival time of the agent for the last
     iteration.
    :travel_time timedelta: Travel time of the agent for the last iteration.
    :utility float: Utility level obtained by the agent for the last iteration.
    :real_cost float: Cost paid by the agent for the last iteration.
    """
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    mode_choices = (
        (0, 'Private vehicle'),
        (1, 'Public transit'),
        (2, 'Walking'),
    )
    mode = models.PositiveSmallIntegerField()
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    travel_time = models.DurationField()
    utility = models.FloatField()
    real_cost = models.FloatField()

    class Meta:
        db_table = 'AgentResults'


class AgentRoadPath(models.Model):
    """Road path taken by a specific agent for the last iteration of a run.

    An AgentRoadPath only exists for agents who took the car for the last
    iteration of the run.

    :agent Agent: Agent instance for which the AgentRoadPath is created.
    :run Run: Run instance from which the results are coming.
    :edge Edge: Edge of the road network taken.
    :time datetime.time: Time at which the edge was taken.
    :travel_time timedelta: Travel time on the edge.
    """
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    edge = models.ForeignKey(Edge, on_delete=models.CASCADE)
    time = models.TimeField()
    travel_time = models.DurationField()

    class Meta:
        db_table = 'AgentRoadPath'


class Network(models.Model):
    """Class to link a road network, a vehicle set and a zone set (and
    eventually, a public-transit network).

    The road network and the zone set are further connected through
    ZoneNodeRelations.

    :project Project: Project the Network instance belongs to.
    :road_network RoadNetwork: RoadNetwork of the Network.
    :vehicle_set VehicleSet: VehicleSet of the Network.
    :zone_set ZoneSet: ZoneSet of the Network.
    :name str: Name of the Network.
    :comment str: Description of the Network (default is '').
    :tags set of str: Tags describing the instance, used to search and filter
     the instances.
    :date_created datetime.date: Creation date of the Network.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    road_network = models.ForeignKey(RoadNetwork, on_delete=models.CASCADE)
    vehicle_set = models.ForeignKey(VehicleSet, on_delete=models.CASCADE)
    zone_set = models.ForeignKey(ZoneSet, on_delete=models.CASCADE)
    name = models.CharField(max_length=80, help_text='Name of the Network')
    comment = models.CharField(max_length=240, blank=True,
                               help_text='Additional comment for the Network')
    tags = models.CharField(max_length=240, blank=True)
    date_created = models.DateField(auto_now_add=True,
                                    help_text='Creation date of the Network')

    def __str__(self):
        self.name

    class Meta:
        db_table = 'Network'


class ZoneNodeRelation(models.Model):
    """Link between an OD zone and a road-network node.
    """
    network = models.ForeignKey(Network, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    node = models.ForeignKey(Node, on_delete=models.CASCADE)


class BackgroundTask(models.Model):
    """Class to represent a task that was run in the background on the server.

    :id UUID: Id of the related django-q task.
    :project Project: Project instance for which the task was created.
    :status Status: Status of the task (in-progress, finished or failed).
    :description str: Description of the task.
    :start_date datetime.datetime: Starting time of the task.
    :end_date datetime.datetime: Ending time of the task.
    :time_taken timedelta: Total running time of the task.
    """
    INPROGRESS = 0
    FINISHED = 1
    FAILED = 2
    STATUS_CHOICES = (
        (INPROGRESS, 'In-progress'),
        (FINISHED, 'Finished'),
        (FAILED, 'Failed'),
    )
    id = models.UUIDField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    status = models.SmallIntegerField(default=0, choices=STATUS_CHOICES)
    description = models.CharField(max_length=50)
    start_date = models.DateTimeField(auto_now_add=True)
    time_taken = models.DurationField(null=True, blank=True)
    result = models.TextField(null=True, blank=True)

    # Optional Foreign Keys.
    road_network = models.ForeignKey(RoadNetwork, on_delete=models.CASCADE,
                                     blank=True, null=True)

    def get_status(self):
        return self.STATUS_CHOICES[self.status][1]

    def instance(self):
        if self.road_network:
            return str(self.road_network)
        return ''

    class Meta:
        db_table = 'BackgroundTask'