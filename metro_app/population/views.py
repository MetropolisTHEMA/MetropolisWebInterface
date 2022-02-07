from django.shortcuts import redirect, render
from metro_app.forms import PopulationForm, PopulationSegmentForm
from metro_app.models import Project, Population, PopulationSegment


def add_population(request, pk):
    project = Project.objects.get(id=pk)
    if request.method == 'POST':
        form = PopulationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_details', pk)

    form = PopulationForm()
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
            return redirect('project_details', 3)

    form = PopulationForm(instance=population)
    context = {
        'form': form,
        'parent_template': 'index.html'
    }
    return render(request, 'update.html', context)



def create_population_segment(request, pk):
    current_project = Project.objects.get(id=pk)
    population_segment = PopulationSegment(project=current_project)
    if request.method == 'POST':
        form = PopulationSegmentForm(request.POST, instance=population_segment)
        if form.is_valid():
            form.save()
            return redirect('project_details', pk)

    form = PopulationSegmentForm(initial={'project': current_project})
    context = {
        'form': form
    }
    return render(request, 'views/form.html', context)