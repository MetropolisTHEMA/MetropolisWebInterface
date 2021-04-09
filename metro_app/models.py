
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
from users.models import CustomUser

#class CustomUser(AbstractUser):
    #https://testdriven.io/blog/django-custom-user-model/
    #pass # Create an separate app for users accounts

class Project(models.Model):
    """
    A project can belongs to many users. And a user can have many projects

    :owner str: the owner of the project.
    :public bool: specify if the created project is private or public.
    :name str: is the name of the project's owner.
    """
    owner = models.ManyToManyField(CustomUser)
    public = models.BooleanField(default=False)
    name = models.CharField('Project Name', max_length=200, null=False)

    def __str__(self):
        return "Project Name : {} \n Project Owner: {} \n Public:  {}".format(
        self.name, self.owener, self.public)

    class Meta:
        db_table = 'Project'

class File(models.Model):
    """
    :project: a foreign key. The first argument "Project" indicate the relationship model.
    :public: boolean field. If true this is a public, else this private.
    :title: file name
    :location:
    """
    project = models.ForeignKey(Project, related_name='file_project', on_delete=models.CASCADE)
    public = models.BooleanField()
    title = models.CharField('File Title', max_length=200)
    location = models.CharField('Location File', max_length=300)

    def __str__(self):
        return "{}".format(self.title)

    class Meta:
        db_table='File'

class ParameterSet(models.Model):
    """
    :project: a foreign key. The first argument "Project" indicate the relationship model.
    :public: boolean field. If true this is a public, else this private.
    :period_start: start period
    :period_end: end period
    :period_interval:
    :lerarn_process: type of learning process (exponential, linear, quadratic, genetic )
    :iter_check: boolean value
    :iter_value: number of iterations, if zero number of iterations is unlimited
    :converg_check: boolean value
    :converg_value: value of convergence after iteration.
    :spill_back: boolean value
    :locked: if true, I can no more modify it.
    """
    leraning_process = (
        (1, 'exponential'),
        (2, 'linear'),
        (3, 'quadratic'),
        (4, 'genetic')
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    public = models.BooleanField(default=False)
    period_start = models.DateTimeField('Period Start', auto_now_add=True)
    period_end = models.DateTimeField('Period Start', auto_now_add=True)
    #period_interval =
    learn_process =models.CharField(max_length=100, null=False, choices=leraning_process)
    learn_param = models.FloatField(blank=False)
    iter_check = models.BooleanField(default=False)
    iter_value = models.SmallIntegerField()
    converg_check= models.BooleanField()
    converg_value = models.FloatField(blank=False)
    spillback_enable = models.BooleanField()
    spillback_value = models.FloatField(blank=False)
    locked = models.BooleanField(default=False)

    def __str__(self):
        return "{}".format(self.learn_process)

    class Meta:
        db_table='ParameterSet'

class RoadNetwork(models.Model):
    """
    :project: foreign key. The first argument "Project" indicate the relationship model.
    :public: boolean field. If true this is a public, else this private.
    :boolean: if True this is an abstract network, False a valid network.
    :locked: boolean field, if true this is locked.
    :representation:
    :nb_nodes: total number of nodes.
    :nb_edges: total number of edges.
    :name: network name. It can be IDF, Brussels, etc.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    public = models.BooleanField(default=False)
    simple = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    #representation = path
    nb_nodes = models.IntegerField()
    nb_edges = models.IntegerField()
    name = models.CharField('Network Name', max_length=200, blank=False)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        db_table='RoadNetWork'


class Node(models.Model):
    """
    A RoadNetwork model record can have many Edges model records associated with.
    A Node belongs to a single RoadNetWork record. This is one to many relationship.

    :network: a foreign key which create the one to many relationship.
              The first argument "RoadNetWork" indicate the relationship model.

    :user_id: used in import and output files. Should be unique among all network's links.
    :enable_origin: boolean value
    :enable_destination: boolean value
    """
    network = models.ForeignKey(RoadNetwork, on_delete=models.CASCADE)
    id_node =models.IntegerField() #user_id =
    enable_origin = models.BooleanField()
    enable_destination= models.BooleanField()
    name = models.CharField('Node Name', max_length=200)

    def __str__(self):
        return "Node : {}".format(self.name)

    class Meta:
        db_table='Node'


class Edge(models.Model):
    """
    Sometimes you may read edge and other time link. These two words mean same thing.
    A RoadNetwork model record can have many Edges model records associated with.
    An Edge belongs to a single RoadNetWork record. This is one to many relationship.

    :congestion: congestion function, 1 equal to free flow and 2 to congestion
    :capacity: number of vehicle per lane and per hour.
    :speed: speed of the link (km/h)
    :length: lenth of the link (km)
    :lanes: number of lanes of a link
    :geometry: linestring of links
    :name: edge name, usefull for displaying name on the netowork
    :user_id: used in import and output files. Should be unique among all network's links.
    :target: is the destination of travellers
    :source: is the orgin of travellers
    """
    free_flow, congestion =1, 2
    congestion_choice = (
                         (1, free_flow),
                         (2, congestion),
                         )
    congestion = models.IntegerField(default=free_flow, choices=congestion_choice)
    capacity = models.FloatField(null=False, blank=False)
    speed = models.FloatField(blank=False)
    lenth = models.FloatField(null=False)
    lanes = models.SmallIntegerField(null=False)
    geometry = models.LineStringField(null=True)
    name = models.CharField('Edge Name',max_length=200, blank=False)
    #user_id
    target = models.ForeignKey(Node, related_name='edges_target', on_delete=models.CASCADE)
    source = models.ForeignKey(Node, related_name='edges_source', on_delete=models.CASCADE)
    network = models.ForeignKey(RoadNetwork, related_name='edges_network', on_delete=models.CASCADE)

    def __str__(self):
        return "Edge : {}".format(self.name)

    class Meta:
        db_table = 'Edges'


class Population(models.Model):
    """
    :generated: boolen value
    :random_seed: radom number.
    """
    generated = models.BooleanField(blank=False)
    random_seed = models.IntegerField()

    def __str__(self):
        return "Population - random vaule: ({})".format(random_seed)

    class Meta:
        db_table = 'Population'


class ODMatrix(models.Model):
    """
    :project: a foreign key. The first argument "Project" indicate the relationship model.
    :public: boolean field. If true this is a public, else this private.
    :size:  total number of agents in OD matrix.
    :locked: boolean field, if true this is locked.
    """
    project = models.ForeignKey(Project, related_name='odmatrix_project', on_delete=models.CASCADE)
    public = models.BooleanField(default=False)
    size = models.IntegerField(null=False)
    locked = models.BooleanField(default=False)

    def __str__(self):
        pass

    class Meta:
        db_table='ODMatrix'


class PopulationSegment(models.Model):
    """
    :population: a foreign key which creates the one to many relationship.
    :preferences: user preferences
    :od_matrix: the origin destination matrix.
    """
    population = models.ForeignKey(Population, on_delete=models.CASCADE)
    preferences = models.IntegerField(blank=False)
    od_matrix = models.ForeignKey(ODMatrix, related_name='opulationsegments_od_matrix', on_delete=models.CASCADE)

    def __str__(self):
        return "Population segment - ({})".format(population)

    class Meta:
        db_table='PopulationSegment'


class Preferences(models.Model):
    """
    :project: a foreign key. The first argument "Project" indicate the relationship model.
    :public: boolean field. If true this is a public, else this private.
    :locked: boolean field, if true this is locked.
    """
    project = models.ForeignKey(Project, related_name='preferences_project' , on_delete=models.CASCADE)
    public = models.BooleanField(default=False)
    #parameter =TBD
    locked = models.BooleanField(default=False)

    def __str__(self):
        return "Preferences - ({})".format(self.project)

    class Meta:
        db_table='Preferences'

class Zone(models.Model):
    """
    :centroid: fixed point of network representing an area(e.g city or district), which is the origin
     or destination of travellers.
    :geometry: Polygon Field
    :raidus: zone or intersection radius
    :name: zone name
    """
    centroid= models.PointField()
    geometry = models.PolygonField()
    radius = models.FloatField(null=False)
    name=models.CharField('Zone Name', max_length=200)

    def __str__(self):
        return 'Zone name: ({})'.format(self.name)

    class Meta:
        db_table='Zone'


class ODPair(models.Model):
    """
    :matrix: a foreign key. The first argument "ODMatrix" indicate the relationship model.
    :origin: foreign key
    :destination: foreign key
    :size: number of agents travelling from an origin to a destination.
    """
    matrix = models.ForeignKey(ODMatrix, related_name='odpairs_matrix', on_delete=models.CASCADE)
    origin = models.ForeignKey(Zone, related_name='odpairs_origin', on_delete=models.CASCADE)
    destination = models.ForeignKey(Zone, related_name='odpairs_destination' , on_delete=models.CASCADE)
    size = models.IntegerField(null=False)

    def __str(self):
        pass

    class Meta:
        db_table = 'ODPair'

 # ........................................................................... #
 #                            Metrosim                                         #
 # ........................................................................... #

class Run(models.Model):
    pass

    class Meta:
        db_table='Run'


class AgentResults(models.Model):
    pass

    class Meta:
        db_table = 'AgentResults'


class AgentRoadPath(models.Model):
    pass

    class Meta:
        db_table = 'AgentRoadPath'


class NodeResults(models.Model):
    pass

    class Meta:
        db_table = 'NodeResults'


class EdgeResults(models.Model):
    pass

    class Meta:
        db_table = 'EdgesResutls'
