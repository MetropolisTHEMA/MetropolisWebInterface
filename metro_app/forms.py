from django import forms
from .models import (Project, RoadType, RoadNetwork, ZoneSet, ODMatrix,
                     Vehicle, Preferences, Population, Agent, ParameterSet,
                     Network, PopulationSegment, ZoneNodeRelation, Run
                     )


class NodeForm(forms.Form):
    my_file = forms.FileField()


class EdgeForm(forms.Form):
    my_file = forms.FileField()


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'public',
            'name',
            'comment',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Give a name for the project'}),
            'comment': forms.TextInput(attrs={'rows': 1}),
        }


class RoadNetworkForm(forms.ModelForm):
    class Meta:
        model = RoadNetwork
        fields = [
            'srid',
            'simple',
            'name',
            'comment',
            'tags',
        ]
        widgets = {
            'comments': forms.TextInput(attrs={'rows': 1}),
            'tags': forms.TextInput(attrs={'rows': 1}),
        }


class RoadTypeForm(forms.ModelForm):
    class Meta:
        model = RoadType
        exclude = ('network', )  # added comma to make this a tuple
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }


class RoadTypeFileForm(forms.Form):
    my_file = forms.FileField()


class ZoneSetForm(forms.ModelForm):
    class Meta:
        model = ZoneSet
        fields = [
            'srid',
            'name',
            'comment',
            'tags',
        ]


class ZoneFileForm(forms.Form):
    my_file = forms.FileField()


class ODMatrixForm(forms.ModelForm):

    def __init__(self, project=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            queryset = ZoneSet.objects.filter(project=project)
            self.fields['zone_set'].queryset = queryset

    class Meta:
        model = ODMatrix
        exclude = ('size', 'locked', 'project')
            
class ODPairFileForm(forms.Form):
    my_file = forms.FileField()

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = '__all__'
        
class VehicleFileForm(forms.Form):
    my_file = forms.FileField()

class PreferencesForm(forms.ModelForm):
    class Meta:
        model = Preferences
        fields = '__all__'
        exclude = ('project', 'locked')
    
    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(PreferencesForm, self).__init__(*args, **kwargs)
        # there's a `fields` property now
        self.fields['mode_choice_mu_distr'].required = False
        self.fields['mode_choice_mu_mean'].required = False
        self.fields['mode_choice_mu_std'].required = False
        self.fields['t_star_std'].required = False
        self.fields['delta_std'].required = False
        self.fields['beta_std'].required = False
        self.fields['gamma_std'].required = False
        self.fields['car_vot_std'].required = False
        self.fields['dep_time_car_mu_distr'].required = False
        self.fields['dep_time_car_mu_mean'].required = False
        self.fields['dep_time_car_mu_std'].required = False
        self.fields['dep_time_car_constant_distr'].required = False
        self.fields['dep_time_car_constant_mean'].required = False
        self.fields['dep_time_car_constant_std'].required = False

class PreferencesFileForm(forms.Form):
    my_file = forms.FileField()
    
class PopulationForm(forms.ModelForm):

    def __init__(self, project=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if project:
            queryset = ZoneSet.objects.filter(project=project)
            self.fields['zone_set'].queryset = queryset

    class Meta:
        model = Population
        exclude = ('project', 'locked', 'generated')

class NetworkForm(forms.ModelForm):

    def __init__(self, project=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            qs1 = ZoneSet.objects.filter(project=project)
            qs2 = RoadNetwork.objects.filter(project=project)
            self.fields['zone_set'].queryset = qs1
            self.fields['road_network'].queryset = qs2

    class Meta:
        model = Network
        exclude = ('project',)


class PopulationSegmentForm(forms.ModelForm):
    class Meta:
        model = PopulationSegment
        exclude = ('population', 'locked', 'generated',)


class ZoneNodeRelationFileForm(forms.Form):
    my_file = forms.FileField()


class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = '__all__'


class AgentFileForm(forms.Form):
    my_file = forms.FileField()


class ParameterSetForm(forms.ModelForm):
    class Meta:
        model = ParameterSet
        # fields = '__all__'
        exclude = ('project', 'locked',)

class ParameterSetFileForm(forms.Form):
    my_file = forms.FileField()


class RunForm(forms.ModelForm):
    class Meta:
        model = Run
        exclude = ('project', 'status', 'start_date',
                   'end_date', 'time_taken','iterations')