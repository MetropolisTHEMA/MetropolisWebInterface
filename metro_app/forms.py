from django import forms
from .models import (Project, RoadType, RoadNetwork)


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
            'coment': forms.TextInput(attrs={'rows': 1}),
        }


class RoadNetworkForm(forms.ModelForm):
    class Meta:
        model = RoadNetwork
        fields = [
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
        fields = '__all__'
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }


class RoadTypeFileForm(forms.Form):
    my_file = forms.FileField()
