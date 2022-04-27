from django.shortcuts import render, redirect, get_object_or_404 
from django.http import Http404
from django.contrib import messages
from metro_app.models import (Run, Project, Population, Network,
    ParameterSet, PopulationSegment, BackgroundTask, Agent)
from metro_app.forms import RunForm
from metro_app.simulation_io import to_input_json
from django_q.tasks import async_task
from metro_app.hooks import str_hook



def list_of_runs(request, pk):
    current_project = Project.objects.get(id=pk)
    runs = Run.objects.filter(project=current_project)
    total_runs = runs.count()
    context = {
        'current_project': current_project,
        'runs': runs,
        'total_runs': total_runs,

    }
    return render(request, 'list.html', context)

def create_run(request, pk):
    current_project = Project.objects.get(id=pk)
    population = Population.objects.filter(project=current_project)
    network = Network.objects.filter(project=current_project)
    if not population.exists() or not network.exists():
        msg = "There is no population or/and netwwork"
        messages.error(request, msg)
    """"try:
        population = Population.objects.filter(project=current_project)
        road_network = RoadNetwork.objects.filter(project=current_project)
    except Population.DoesNotExist:
        raise Http404("Create a population first")
    except RoadNetwork.DoesNotExist:
        raise Http404('There is no road net work created yet')"""
    
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
        })
    context = {
        'project': current_project,
        'form': form
    }
    return render(request, 'form.html', context)


def run_details(request, pk):
    run = Run.objects.get(id=pk)
    tasks = run.backgroundtask_set.order_by('-start_date')[:5]
    context = {
        'run': run,
        'tasks': tasks,
    }
    return render(request, 'details.html', context)

def update_run(request, pk):
    run = Run.objects.get(id=pk)
    if request.method == 'POST':
        form = RunForm(request.POST, instance=run)
        if form.is_valid():
            form.save()
            return redirect('list_of_runs', run.project.pk)

    form = RunForm(instance=run)
    context = {
        'form': form,
        'parent_template': 'index.html'
    }
    return render(request, 'update.html', context)

def delete_run(request, pk):
    run_to_delete = Run.objects.get(id=pk)
    if request.method == 'POST':
        run_to_delete.delete()
        return redirect('list_of_runs', run_to_delete.project.pk)
    
    context = {
        'run_to_delete': run_to_delete
    }
    return render(request, 'delete.html', context)


def generate_run_input(request, pk):
    run = Run.objects.get(id=pk)
    task_id = async_task(to_input_json, run, hook=str_hook)
    description = 'Generating input'
    db_task = BackgroundTask(
        run=run,
        project=run.project,
        id=task_id,
        description=description,
    )
    db_task.save()
    messages.success(request, "Task successfully started")
    return redirect('run_details', pk)


