from django import forms
from .models import (Project, RoadType, RoadNetWork)


class NodeForm(forms.Form):
    my_file = forms.FileField()


class EdgeForm(forms.Form):
    my_file = forms.FileField()


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Give a name for the project'}),
            'coment': forms.TextInput(attrs={'rows': 1}),
        }


class RoadNetWorkForm(forms.ModelForm):
    class Meta:
        model = RoadNetWork
        fields = [
            'abstract',
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
