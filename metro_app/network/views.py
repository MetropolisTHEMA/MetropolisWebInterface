from django.shortcuts import redirect, render
from metro_app.models import Project, Network
from metro_app.forms import NetworkForm

def create_network2(request, pk):
    current_project = Project.objects.get(id=pk)
    network = Network(project=current_project)
    if request.method == 'POST':
        form = NetworkForm(request.POST, instance=network)
        if form.is_valid():
            form.save()
            return redirect('project_details', pk)

    form = NetworkForm(initial={'project':current_project})
    context = {
        'form': form
    }
    return render(request, 'views/form.html', context)