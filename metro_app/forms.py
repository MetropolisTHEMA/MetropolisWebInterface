from django import forms
from .models import *

class NodeForm(forms.ModelForm):
    my_file = forms.FileField()

    class Meta:
        model=Node
        fields = [
            'network',
            'my_file',
        ]


class ProjectForm(forms.ModelForm):
    class Meta:
        model=Project
        fields ='__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Give a name for the project'}),
            'coment':forms.TextInput(attrs={'rows':1}),
        }


class RoadNetworkForm(forms.ModelForm):
    class Meta:
        model=RoadNetwork
        fields = '__all__'
        widgets = {
            'nb_nodes': forms.TextInput(attrs = {'placeholder ': 'Total number of nodes in the road network'}),
            'nb_edges': forms.TextInput(attrs = {'placeholder ': 'Total number of edges in the road network'}),
            'comments': forms.TextInput(attrs = {'rows':1}),
            'tags': forms.TextInput(attrs = {'rows':1}),
        }
