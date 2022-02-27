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
    class Meta:
        model = ODMatrix
        fields = [
            'zone_set', 'locked',
            'name', 'comment', 'tags',
        ]


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
        exclude = ('project',)


class PreferencesFileForm(forms.Form):
    my_file = forms.FileField()
    

class PopulationForm(forms.ModelForm):
    class Meta:
        model = Population
        fields = '__all__'
        exclude = ('locked',)


class NetworkForm(forms.ModelForm):
    class Meta:
        model = Network
        fields = '__all__'


class PopulationSegmentForm(forms.ModelForm):
    class Meta:
        model = PopulationSegment
        exclude = ('locked', 'generated',)


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
        fields = '__all__'
        exclude = ('locked',)

class ParameterSetFileForm(forms.Form):
    my_file = forms.FileField()


class RunForm(forms.ModelForm):
    class Meta:
        model = Run
        fields = '__all__'