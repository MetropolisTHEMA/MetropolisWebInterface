from django.shortcuts import redirect, render
from django.contrib import messages
from metro_app.forms import PopulationForm, PopulationSegmentForm
from metro_app.models import (Project, Population, PopulationSegment, 
                              Agent, BackgroundTask)
from metro_app.simulation_io import generate_agents
from django_q.tasks import async_task
from metro_app.hooks import str_hook


def add_population(request, pk):
    current_project = Project.objects.get(id=pk)
    population = Population(project=current_project)
    if request.method == 'POST':
        form = PopulationForm(request.POST, instance=population)
        if form.is_valid():
            form.save()
            messages.success(request, 'Population successfully added')
            return redirect('population_details', population.pk)

    form = PopulationForm(initial={'project':current_project})
    context = {
        'form': form
    }
    return render(request, 'views/form.html', context)


def update_population(request, pk):
    population = Population.objects.get(id=pk)
    if request.method == 'POST':
        form = PopulationForm(request.POST, instance=population)
        if form.is_valid():
            form.save()
            return redirect('project_details', population.project.pk)

    form = PopulationForm(instance=population)
    context = {
        'form': form,
        'parent_template': 'index.html'
    }
    return render(request, 'update.html', context)


def population_details(request, pk):
    population = Population.objects.get(id=pk)
    #project = population.project
    tasks = population.backgroundtask_set.order_by('-start_date')[:5]
    context = {
        'population': population,
        'tasks': tasks,
    }
    return render(request, 'views/details.html', context)


def create_population_segment(request, pk):
    population = Population.objects.get(id=pk)
    agent = population.agent_set.all()

    if agent.exists():
        messages.warning(request, 'There exists an agent already created. \
        So you can not create or add an popuation segment.')
        return redirect('population_details', pk)
    else:

        if request.method == 'POST':
            population_segment = PopulationSegment(population=population)
            form = PopulationSegmentForm(request.POST, instance=population_segment)
            if form.is_valid():
                form.save()
                messages.success(request, 'Population segment created')
                return redirect('population_details', pk)

        form = PopulationSegmentForm(initial={'population': population})
        context = {
            'form': form,
        }
        return render(request, 'views/form.html', context)


def update_population_segment(request, pk):
    population_segment = PopulationSegment.objects.get(id=pk)
    if request.method == 'POST':
        form = PopulationSegmentForm(request.POST, instance=population_segment)
        if form.is_valid():
            form.save()
            return redirect('project_details', population_segment.project.pk)
    
    form = PopulationSegmentForm(instance=population_segment)
    context = {
        'form': form,
        'parent_template': 'index.html'
    }
    return render(request, 'update.html', context)


def delete_population_segment(request, pk):
    population_segment_to_delete = PopulationSegment.objects.get(id=pk)
    if request.method == 'POST':
        population_segment_to_delete.delete()
        return redirect('project_details', population_segment.project.pk)

    context = {
        'population_segment_to_delete': population_segment_to_delete,
    }
    return render(request, 'delete.html', context)


def population_segment_details(request, pk):
    population_segment = PopulationSegment.objects.get(id=pk)
    context = {
        'population_segment': population_segment
    }
    return render(request, 'views/details.html', context)


def generate_agents_input(request, pk):
    population = Population.objects.get(id=pk)    
    # population_segment = population.populationsegment_set.all()
    task_id = async_task(generate_agents, population,  hook=str_hook)
    description = 'Generating agents'
    db_task = BackgroundTask(
        project=population.project,
        id=task_id,
        description=description,
        population=population)
    db_task.save()
    messages.success(request, "Task successfully started")
    return redirect('population_details', pk)
    
