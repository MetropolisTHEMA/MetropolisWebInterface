from django.shortcuts import render, redirect
from django.contrib import messages
from metro_app.models import (Run, Project, Population, RoadNetwork,
    ParameterSet, PopulationSegment, BackgroundTask, Agent)
from metro_app.forms import RunForm


def create_run(request, pk):
    current_project = Project.objects.get(id=pk)
    population = Population.objects.get(project=current_project)
    road_network = RoadNetwork.objects.get(project=current_project)
    
    if request.method == 'POST':
        run = Run(project=current_project)
        form = RunForm(request.POST, instance=run)
        if form.is_valid():
            try:
                form.save()
            except Exception as e:
                messages.error(request, e)
                return redirect('project_details', pk)
            else:
                messages.success(request, 'run created')
                return redirect('run_details', run.pk)

    form = RunForm(initial={
        'project': current_project,
        'population': population,
        'network': road_network,
        })
    context = {
        'form': form
    }
    return render(request, 'views/form.html', context)


def run_details(request, pk):
    run = Run.objects.get(id=pk)
    context = {
        'run': run
    }
    return render(request, 'views/details.html', context)


def delete_run(request, pk):
    run_to_delete = Run.objects.get(id=pk)
    if request.method == 'POST':
        run_to_delete.delete()
        return redirect('project_details', run_to_delete.project.pk)
    
    context = {
        'run_to_delete': run_to_delete
    }
    return render(request, 'delete.html', context)
