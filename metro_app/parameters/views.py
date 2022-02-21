from metro_app.models import Project, ParameterSet
from metro_app.models import ParameterSetForm, ParameterSetFileForm


def set_parameter(request, pk):
    project = Project.objects.get(id=pk)
    pass