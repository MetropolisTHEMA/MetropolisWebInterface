from django.shortcuts import redirect, render
from metro_app.forms import PopulationForm
from metro_app.models import Population


def add_population(request, pk):
    if request.method == 'POST':
        form = PopulationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_details', 3)

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
