"""
Django Models Modules
=====================
Note: Please note that the models module is imported from django.contrib.gis.db and not the
usual django.db module.

All model relationship create dependencies between one another, so an important behavior is
what happens to the other party when one party is removed. The on_delete option is designed
for this purpose, to determine what to do with records on the other side of a relationship
when one side is removed. The on_delete option is available for all three relationship model
data types. Here is an exellent book about this topic
https://www.webforefront.com/django/setuprelationshipsdjangomodels.html
"""
#from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import User
#from users.models import CustomUser

# class CustomUser(AbstractUser):
# https://testdriven.io/blog/django-custom-user-model/
# pass # Create an separate app for users accounts


class Project(models.Model):
    """Projects are containers used to store input models, runs and output
    models in a coherent and organized manner.

    Each user can create multiple projects and each project can be shared
    between multiple users.
    The creator of the project is the owner. He can decide to add or remove
    users to the project.

    :owner CustomUser: The user who created and owns the project.
    :users set of CustomUser: Set of users who can view and modify the project.
    :public bool: If True, the project can be viewed (but not modified) by
     anyone (default is False).
    :name str: Name of the project.
    :comment str: Description of the project (default is '').
    """
    owner = models.ManyToManyField(User) # define as FK and add a user as ManyToManyField

    public = models.BooleanField(default=False)
    name = models.CharField('Project Name', max_length=200, null=False)
    comment = models.TextField()

    def __str__(self):
        return "Project Name : {} \n Project Owner: {} \n Public:  {}".format(
            self.name, self.owner, self.public)

    class Meta:
        db_table = 'Project'


class File(models.Model):
    """File shared by the users of a project.

    :project Project: Project the file belongs to.
    :public bool: if True, the file can be viewed by anyone (only if the
     project is also public.
    :title str: Title of the file, as shown on the interface.
    :location file: Location of the file on the server.
    """
    project = models.ForeignKey(
        Project,
        related_name='file_project',
        on_delete=models.CASCADE)
    public = models.BooleanField(default=False)
    title = models.CharField('File Title', max_length=200)
    location = models.CharField('File Location', max_length=300)

    def __str__(self):
        return "{}".format(self.title)

    class Meta:
        db_table = 'File'


class ParameterSet(models.Model):
    """Set of technical parameters used for a run.

    :project Project: Project the ParameterSet instance belongs to.
    :period_start datetime.time: Earliest possible departure time.
    :period_end datetime.time: Latest possible departure time.
    :period_interval  timedelta: Interval at which link-specific results are
     recorded.
    :learn_process str: Type of learning process for the day-to-day model.
     Possible values are 'EX' (exponential model), 'LI' (linear model), 'QU'
     (quadratic model) and 'GE' (genetic model).
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
    """
    leraning_process = (
        ('EX', 'exponential'),
        ('LI', 'linear'),
        ('QU', 'quadratic'),
        ('GE', 'genetic')
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    public = models.BooleanField(default=False)
    period_start = models.TimeField('Period Start')
    period_end = models.TimeField('Period Start')
    period_interval = models.DurationField(default=5)
    learn_process = models.CharField(
        max_length=100,
        null=False,
        choices=leraning_process)
    learn_param = models.FloatField(blank=False)
    iter_check = models.BooleanField(default=False)
    iter_value = models.SmallIntegerField()
    converg_check = models.BooleanField(default=False)
    converg_value = models.FloatField()
    spillback_enable = models.BooleanField()
    spillback_value = models.FloatField()
    locked = models.BooleanField(default=False)
    name = models.CharField('Name of the instance', max_length=200)
    comment = models.TextField()
    tags = models.TextField()

    def __str__(self):
        return "{}".format(self.learn_process)

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
    :representation file: Location on the server of the HTML file with the
     Leaflet.js representation of the road network.
    :nb_nodes int: Total number of nodes in the road network.
    :nb_edges int: Total number of edges in the road network.
    :crs str: Coordinate reference system used for the coordinates of the
     nodes and the geometry of the edges.
    :name str: Name of the instance.
    :comment str: Description of the instance.
    :tags set of str: Tags describing the instance, used to search and filter
     the instances.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    simple = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    #representation = path
    nb_nodes = models.IntegerField()
    nb_edges = models.IntegerField()
    name = models.CharField('Network Name', max_length=200, blank=False)
    comment = models.TextField()
    tags = models.TextField()

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        db_table = 'RoadNetWork'


class RoadType(models.Model):
    """Congestion model for a set of edges.

    :network RoadNetwork: RoadNetwork the RoadType instance belongs to.
    :user_id int: Id of the road type, as used by the users in the import
     files. Must be unique for a specific RoadNetwork.
    :name str: Name of the road type (default is '').
    :congestion str: Congestion model used to compute the travel time of the
     edges. Possible values are 'FF' (free-flow), 'BN' (bottleneck), 'LD' (log
     density) and 'BP' (bureau of public roads function).
    :default_speed float: Default free-flow speed of the edges for this road
     type, in kilometers per hour.
    :default_param1 float: Default value for the first parameter used in the
     congestion model. The exact meaning depends on the congestion model.
    :default_param2 float: Default value for the second parameter used in the
     congestion model. The exact meaning depends on the congestion model.
    :default_param3 float: Default value for the third parameter used in the
     congestion model. The exact meaning depends on the congestion model.
    """
    name = models.CharField('Road Type', max_length=200, blank=False)
    congestion_choices = (
        ('Free flow', 'Free flow'),
        ('Congestion', 'Congestion'),
    )
    network = models.ForeignKey(
        RoadNetwork,
        related_name='roads_type_network',
        on_delete=models.CASCADE)
    # user_id
    congestion = models.CharField(max_length=200, choices=congestion_choices)
    default_speed = models.FloatField(default=50)
    default_lanes = models.SmallIntegerField(default=1)
    default_param1 = models.FloatField(default=1.0)
    default_param2 = models.FloatField(default=1.0)
    default_param3 = models.FloatField(default=3.0)

    def __str__(self):
        return "{} - ({})".format(self.name, self.congestion)

    class Meta:
        db_table = 'RoadType '


class Node(models.Model):
    """A Node is an element of the road-network graph, representing an
    intersection or an origin / destination point.

    :network: RoadNetwork instance the Node belongs to.
     The first argument "RoadNetWork" indicate the relationship model.
    :user_id int: Id of the node, as used by the users in the import files.
     Must be unique for a specific RoadNetwork.
    :name str: Name of the node (default is '').
    :location Point: Point representing the location of the node on the
     network, in EPSG:4326.
    """
    network = models.ForeignKey(RoadNetwork, on_delete=models.CASCADE)
    node_id = models.IntegerField()  # user_id =
    name = models.CharField('Node Name', max_length=200)
    location = models.PointField()

    def __str__(self):
        return "Node : {} of ( Network {} )".format(self.name, self.network)

    class Meta:
        db_table = 'Node'


class Edge(models.Model):
    """An Edge is an element of the road-network graph, representing road
    sections or connectors (between an origin / destination and the network).

    :network RoadNetwork: RoadNetwork the Node instance belongs to.
    :source Node: Node representing the starting point of the edge.
    :target Node: Node representing the ending point of the edge.
    :roadtype RoadType: Road type representing the congestion model of the
     edge.
    :user_id int: Id of the edge, as used by the users in the import files.
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
    # capacity = models.FloatField()
    param1 = models.FloatField(null=True, blank=True)
    param2 = models.FloatField()
    param3 = models.FloatField()
    speed = models.FloatField()
    lenth = models.FloatField(null=False)
    lanes = models.SmallIntegerField(null=False)
    geometry = models.LineStringField(null=True)
    name = models.CharField('Edge Name', max_length=200, blank=False)
    # user_id
    road_type = models.ForeignKey(
        RoadType,
        related_name='edges_road_type',
        on_delete=models.CASCADE)
    target = models.ForeignKey(
        Node,
        related_name='edges_target',
        on_delete=models.CASCADE)
    source = models.ForeignKey(
        Node,
        related_name='edges_source',
        on_delete=models.CASCADE)
    network = models.ForeignKey(
        RoadNetwork,
        related_name='edges_network',
        on_delete=models.CASCADE)

    def __str__(self):
        return "Edge : {}".format(self.name)

    class Meta:
        db_table = 'Edge'


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
    """
    generated = models.BooleanField(blank=False)
    random_seed = models.IntegerField()

    def __str__(self):
        return "Population - random vaule: ({})".format(self.random_seed)

    class Meta:
        db_table = 'Population'


class ODMatrix(models.Model):
    """Origin-destination matrix representing the origin and destination for a
    set of agents.

    :project Project: Project the ODMatrix instance belongs to.
    :size int: Total number of agents in the origin-destination matrix.
    :locked bool: If True, the instance cannot be modified (default is False).
    :name str: Name of the instance (default is '').
    :comment str: Description of the instance (default is '').
    :tags set of str: Tags describing the instance, used to search and filter
     the instances.
    """
    project = models.ForeignKey(
        Project,
        related_name='odmatrix_project',
        on_delete=models.CASCADE)
    public = models.BooleanField(default=False)
    size = models.IntegerField(null=False)
    locked = models.BooleanField(default=False)
    name = models.CharField('Name of the instance', max_length=200)
    comment = models.TextField()
    tags = models.TextField()

    def __str__(self):
        pass

    class Meta:
        db_table = 'ODMatrix'


class PopulationSegment(models.Model):
    """Representation of a set of agents that can be represented with an
    origin-destination matrix and a distribution of preferences.

    :population Population: Population the PopulationSegment is a part of.
    :preferences Preferences: Preferences instance representing the
     distribution of preferences for this population segment.
    :od_matrix ODMatrix: ODMatrix instance representing the origin-destination
     matrix for this population segment.
    """
    population = models.ForeignKey(Population, related_name='population_segment', on_delete=models.CASCADE)
    preferences = models.IntegerField(blank=False)
    od_matrix = models.ForeignKey(
        ODMatrix,
        related_name='opulationsegments_od_matrix',
        on_delete=models.CASCADE)

    def __str__(self):
        return "Population segment - ({})".format(self.population)

    class Meta:
        db_table = 'PopulationSegment'


class Preferences(models.Model):
    """Distribution of preferences describing a set of agents.

    :project Project: Project the Preferences instance belongs to.
    ...
    :locked bool: If True, the instance cannot be modified (default is False).
    :name str: Name of the instance (default is '').
    :comment str: Description of the instance (default is '').
    :tags set of str: Tags describing the instance, used to search and filter
     the instances.
    """
    project = models.ForeignKey(
        Project,
        related_name='preferences_project',
        on_delete=models.CASCADE)
    public = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    name = models.CharField('Name of the instance', max_length=200)
    comment = models.TextField()
    tags = models.TextField()

    def __str__(self):
        return "Preferences - ({})".format(self.project)

    class Meta:
        db_table = 'Preferences'


class Zone(models.Model):
    """Point or area representing the origin or destination of agents.

    Zones can be defined in two ways:
    - As a circle, with a given center and radius (zero for points).
    - As an area defined by a polygon.

    :centroid Point: Center point of the circle or centroid of the area.
    :geometry Polygon: Polygon representing the zone, if it is an area.
    :radius float: Radius of the zone in meters, if it is a circle.
    :name str: Name of the zone (default is '').
    """
    centroid = models.PointField()
    geometry = models.PolygonField()
    radius = models.FloatField(null=False)
    name = models.CharField('Zone Name', max_length=200)

    def __str__(self):
        return 'Zone name: ({})'.format(self.name)

    class Meta:
        db_table = 'Zone'


class ODPair(models.Model):
    """Single origin-destination pair of an ODMatrix.

    :matrix ODMatrix: ODMatrix the ODPair belongs to.
    :origin Zone: Origin zone for the OD pair.
    :destination Zone: Destination zone for the OD pair.
    :size int: Number of agents with the given origin and destination.
    """
    matrix = models.ForeignKey(
        ODMatrix,
        related_name='odpairs_matrix',
        on_delete=models.CASCADE)
    origin = models.ForeignKey(
        Zone,
        related_name='odpairs_origin',
        on_delete=models.CASCADE)
    destination = models.ForeignKey(
        Zone,
        related_name='odpairs_destination',
        on_delete=models.CASCADE)
    size = models.IntegerField(null=False)

    def __str(self):
        pass

    class Meta:
        db_table = 'ODPair'

 # ........................................................................... #
 #                            Metrosim                                         #
 # ........................................................................... #


class Run(models.Model):
    """Class to represent a run of MetroSim.

    :project Project: Project the Run instance belongs to.
    :parameter_set ParameterSet: ParameterSet used for the run.
    :population Population: Population used for the run.
    :policy Policy: Policy used for the run.
    :road_network RoadNetwork: RoadNetwork used for the run.
    :pt_network PTNetwork: PTNetwork used for the run.
    :status str: Status of the run. Possible values are 'NR' (not ready), 'RY'
     (ready), 'IP' (in progress), 'FI' (finished), 'AB' (aborted) and 'FA'
     (failed).
    :name str: Name of the instance (default is '').
    :comment str: Description of the instance (default is '').
    :tags set of str: Tags describing the instance, used to search and filter
     the instances.
    :start_time datetime.datetime: Starting time of the run.
    :end_time datetime.datetime: Ending time of the run.
    :time_taken timedelta: Total running time of the run.
    :iterations int: Number of iterations of the run.
    """
    pass

    class Meta:
        db_table = 'Run'


class Agent(models.Model):
    """Generated agent ready to be used by MetroSim.

    :population Population: Population instance the Agent belongs to.
    :origin_node Node: Node of the road network used as the origin of the
     agent for car trips.
    :destination_node Node: Node of the road network used as the destination of
     the agent for car trips.
    :origin_stop PTStop: PTStop of the public-transit network used as the
     origin of the agent for public-transit trips.
    :destination_stop PTStop: PTStop of the public-transit network used as the
     destination of the agent for public-transit trips.
    ...
    """
    pass


class AgentResults(models.Model):
    """Class to hold results of MetroSim for a specific agent.

    :agent Agent: Agent instance for which the AgentResults is created.
    :run Run: Run instance from which the results are coming.
    :mode str: Mode chosen by the agent for the last iteration. Possible values
     are 'PV' (private vehicle), 'PT' (public transit) and 'WA' (walking).
    :departure_time datetime.time: Departure time of the agent for the last
     iteration.
    :arrival_time datetime.time: Arrival time of the agent for the last
     iteration.
    :travel_time timedelta: Travel time of the agent for the last iteration.
    :utility float: Utility level obtained by the agent for the last iteration.
    :real_cost float: Cost paid by the agent for the last iteration.
    """
    pass

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
    pass

    class Meta:
        db_table = 'AgentRoadPath'


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
    pass

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
    pass

    class Meta:
        db_table = 'EdgesResutls'
