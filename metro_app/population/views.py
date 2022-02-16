from django.shortcuts import redirect, render
from metro_app.forms import PopulationForm, PopulationSegmentForm
from metro_app.models import Project, Population, PopulationSegment


def add_population(request, pk):
    current_project = Project.objects.get(id=pk)
    population = Population(project=current_project)

    if request.method == 'POST':
        form = PopulationForm(request.POST, instance=population)
        if form.is_valid():
            form.save()
            return redirect('project_details', pk)

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
    context = {
        'population': population
    }
    return render(request, 'views/details.html', context)


def create_population_segment(request, pk):
    population = Population.objects.get(id=pk)
    if request.method == 'POST':
        form = PopulationSegmentForm(request.POST, instance=population)
        if form.is_valid():
            form.save()
            return redirect('project_details', pk)

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
        return redirect('project_details', population_segment.project.pkk)

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