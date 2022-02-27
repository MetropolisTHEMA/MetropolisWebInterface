from django.shortcuts import render, redirect
from django.contrib import messages
from metro_app.models import Project, ParameterSet
from metro_app.forms import ParameterSetForm, ParameterSetFileForm
from datetime import timedelta
import json

def set_parameters(request, pk):
    current_project = Project.objects.get(id=pk)
    if request.method == 'POST':
        parameter_set = ParameterSet(project=current_project)
        form = ParameterSetForm(request.POST, instance=parameter_set)
        if form.is_valid():
            form.save()
            return redirect('project_details', current_project.pk)

    form = ParameterSetForm(initial={'project': current_project})

    context = {
        'form': form,
    }
    return render(request, 'views/form.html', context)


def upload_parameters(request, pk):
    current_project = Project.objects.get(id=pk)
    parameters = ParameterSet.objects.all()
    if parameters.count() > 0:
        messages.warning(request, "Fail !!! ParameterSet table already contains data")
        return redirect('project_details', pk)
    
    if request.method == 'POST':
        form = ParameterSetFileForm(request.POST, request.FILES)
        if form.is_valid():
            list_parameter_set = []
            file = request.FILES['my_file']
            if file.name.endswith('.json'):
                data = json.load(file)
                if type(data) == dict:
                    if data["learn_process"] == 'Exponential':
                        learn_process = 0
                    elif data["learn_process"] == 'Linear':
                        learn_process = 1
                    elif data["learn_process"] == 'quadratic':
                        learn_process = 2
                    else:
                        learn_process = 3

                    parameter_set_instance = ParameterSet(
                        project=current_project,
                        name=data.get("nme", 'Unknown'),
                        period_start=timedelta(seconds=data["period_start"]),
                        period_end=timedelta(seconds=data["period_end"]),
                        period_interval=timedelta(seconds=data.get("period_interval", 0)),
                        learn_process=learn_process,
                        learn_param=data.get("learn_param", .1),
                        iter_value=data.get("max_iter", 50)
                    )
                    list_parameter_set.append(parameter_set_instance)
                elif type(data) == list:
                    for feature in data:
                        larn_process_distr = 'Exponential'
                        try:
                            learn_process_distr = feature["learn_process"]
                        except KeyError:
                            learn_process_distr = 'Exponential'
                    
                        if learn_process_distr == 'Exponential':
                            learn_process = 0
                        elif learn_process_distr == 'Linear':
                            learn_process = 1
                        elif learn_process_distr == 'Quadratic':
                            learn_process = 2
                        elif learn_process_distr == 'Genetic':
                            learn_process = 3
                    
                        parameter_set_instance = ParameterSet(
                            project=current_project,
                            name=feature.get("name", "Unknown"),
                            period_start=timedelta(seconds=feature["period_start"]),
                            period_end=timedelta(seconds=feature["period_end"]),
                            period_interval=timedelta(seconds=feature.get("period_interval", 0)),
                            learn_process=learn_process,
                            learn_param=feature.get("learn_param", .1),
                            iter_value=feature.get("max_iter", 50)
                        )
                        list_parameter_set.append(parameter_set_instance)

                try:
                    ParameterSet.objects.bulk_create(list_parameter_set)
                except Exception as e:
                    messages.error(request, e)
                    return redirect('upload_parameters', pk)
                else:
                    parameters = ParameterSet.objects.all()
                    if parameters.count() > 0:
                        messages.success(request, 'preferences file successfully\
                                        uploaded')
                        return redirect('project_details', pk)
            else:
                messages.error(request, 'File format not recognized')
                return redirect('upload_parameters', pk)

    form = ParameterSetFileForm()
    context = {
        'form': form
    }
    return render(request, 'parameters/parameters.html', context)