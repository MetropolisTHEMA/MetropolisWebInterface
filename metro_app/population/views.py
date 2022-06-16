from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from metro_app.forms import PopulationForm, PopulationSegmentForm
from metro_app.models import (Project, Population, PopulationSegment, 
                              Agent, BackgroundTask)
                              


def list_of_populations(request, pk):
    current_project = Project.objects.get(id=pk)
    populations = Population.objects.filter(project=current_project)
    total_populations = populations.count()
    context = {
        'current_project': current_project,
        'populations': populations,
        'total_populations': total_populations,

    }
    return render(request, 'list.html', context)

def add_population_not_to_use(request, pk):
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
        'project': current_project,
        'form': form
    }
    return render(request, 'form.html', context)

def add_population(request, pk):
    current_project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        population = Population(project=current_project)
        form = PopulationForm(current_project, request.POST, instance=population)
        if form.is_valid():
            form.save()
            messages.success(request, 'Population successfully added')
            return redirect('population_details', population.pk)

    else:
        form = PopulationForm(project=current_project,
            initial={'project': current_project})
    context = {
        'project': current_project,
        'form': form
    }
    return render(request, 'form.html', context)

def update_population(request, pk):
    population = Population.objects.get(id=pk)
    if request.method == 'POST':
        form = PopulationForm(population.project, request.POST, instance=population)
        if form.is_valid():
            form.save()
            messages.success(request, 'Population successfully updated')
            return redirect('list_of_populations', population.project.pk)
    else:
        form = PopulationForm(project=population.project, instance=population)

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
    return render(request, 'details.html', context)

def delete_population(request, pk):
    population = Population.objects.get(id=pk)
    if request.method == 'POST':
        population.delete()
        return redirect('list_of_populations', population.project.pk)

    context = {
        'population_to_delete': population,
    }
    return render(request, 'delete.html', context)

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
            'population': population,
            'form': form,
        }
        return render(request, 'form.html', context)

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

