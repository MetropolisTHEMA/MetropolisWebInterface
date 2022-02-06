from django.shortcuts import render, redirect
from metro_app.forms import PreferencesForm
from metro_app.models import Project, Preferences


def add_preferences(request, pk):
    current_project = Project.objects.get(id=pk)
    if request.method == 'POST':
        preference = Preferences(project=current_project)
        form = PreferencesForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            return redirect('project_details', current_project.pk)

    form = PreferencesForm(initial={'project': current_project})
    context = {
        'form': form,
    }
    return render(request, 'views/form.html', context)


def update_preferences(request, pk):
    preference = Preferences.objects.get(id=pk)
    if request.method == 'POST':
        form = PreferencesForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            return redirect('project_details', preference.project.pk)

    form = PreferencesForm(instance=preference)
    context = {
        'form': form,
        'parent_template': 'index.html'
    }
    return render(request, 'update.html', context)


def delete_preferences(request, pk):
    preference_to_delete = Preferences.objects.get(id=pk)
    if request.method == 'POST':
        preference_to_delete.delete()
        return redirect('project_details', preference_to_delete.project.pk)

    context = {
        'preference_to_delete': preference_to_delete
    }
    return render(request, 'delete.html', context)
