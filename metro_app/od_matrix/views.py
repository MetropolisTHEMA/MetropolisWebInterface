from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from metro_app.models import (ODMatrix, Project, Zone, 
                              BackgroundTask, ODPair)
from metro_app.forms import ODPairFileForm, ODMatrixForm
from metro_app.filters import ODPairFilter
from metro_app.tables import ODPairTable
from django_q.tasks import async_task
from metro_app.hooks import str_hook
import csv
from django_tables2 import RequestConfig


def list_of_od_matrix(request, pk):
    current_project = Project.objects.get(id=pk)
    od_matrix = ODMatrix.objects.filter(project=current_project)
    total_od_matrix = od_matrix.count()
    context = {
        'current_project': current_project,
        'od_matrix': od_matrix,
        'total_od_matrix': total_od_matrix,

    }
    return render(request, 'list.html', context)

def async_task_for_od_pair_file(file, od_matrix_id):
    if file.name.endswith('.csv'):
        file = file.read().decode('utf-8').splitlines()
        data = csv.DictReader(file)
    elif file.name.endswith('.tsv'):
        file = file.read().decode('utf-8').splitlines()
        data = csv.DictReader(file, delimiter='\t')
    else:
        return "Error: Uploaded file format not recongnized"

    od_matrix = ODMatrix.objects.get(id=od_matrix_id)
    zoneset = od_matrix.zone_set
    zones = Zone.objects.filter(zone_set=zoneset)
    zone_instance_dict = {zone.zone_id: zone for zone in zones}
    
    compteur = 0
    od_matrix_size=0
    list_od_pair_instance = []
    for row in data:
        try:
            origin = zone_instance_dict[int(row['origin'])]
            destination = zone_instance_dict[int(row['destination'])]
        except TypeError:
            return 'Uploaded file format not recongnized'
        except KeyError:
            pass
            # compteur = compteur+1
        else:
            od_matrix_size += int(row['size'])
            od_pair_instance = ODPair(
                origin=origin,
                destination=destination,
                size=row['size'],
                matrix=od_matrix,
            )
            list_od_pair_instance.append(od_pair_instance)
    if list_od_pair_instance:
        try:
            ODPair.objects.bulk_create(list_od_pair_instance)
        except Exception:
            return "There is a problem with your file"
        else:
            od_matrix.size = od_matrix_size
            od_matrix.save()
            return "Your OD pair file has been successfully imported !"
    else:
        return "No data uploaded"

def upoload_od_pair(request, pk):
    template = "od_matrix/od_pair.html"
    od_matrix = ODMatrix.objects.get(id=pk)
    od_pair = od_matrix.odpair_set.all()
    if od_pair.exists():
        messages.warning(request, "ODPair already contains data")
        return redirect('od_matrix_details', pk)
    zoneset = od_matrix.zone_set
    zones = Zone.objects.filter(zone_set=zoneset)
    if not zones.exists():
        msg = "Please upload Zone first before uploading OD pair !"
        messages.warning(request, msg)
        return redirect('od_matrix_details', pk)
  
    if request.method == 'POST':
        form = ODPairFileForm(request.POST, request.FILES)
        if form.is_valid():
            my_file = request.FILES['my_file']
            task_id = async_task(async_task_for_od_pair_file,
                                    my_file, pk, hook=str_hook )
            description  = "Importing OD Pair"
            db_task = BackgroundTask(
                project=od_matrix.project,
                id=task_id,
                description=description,
                od_matrix=od_matrix
            )
            db_task.save()
            messages.success(request, "Task successfully started")
            return redirect('od_matrix_details', pk)
        else:
            messages.error(request, 'You file does not respect Metropolisormat guidelines')
            return render(request, template, {'form': form})
    else:
        form = ODPairFileForm()
        return render(request, template, {'form': form})

def create_od_matrix_not_to_use(request, pk):
    """A roadnetwork depends on a project. It
     must be created inside the project"""
    
    project = Project.objects.get(id=pk)
    form = ODMatrixForm(initial={'project': project})
    if request.method == 'POST':
        od_matrix = ODMatrix(project=current_project)
        form = ODMatrixForm(data=request.POST, instance=od_matrix)
        if form.is_valid():
            form.save()
            messages.success(request, "OD matrix cessfully created")
            return redirect('od_matrix_details', od_matrix.pk)

    context = {
        'project': project,
        'form': form}
    return render(request, 'form.html', context)

def create_od_matrix(request, pk):
    current_project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        od_matrix = ODMatrix(project=current_project)
        form = ODMatrixForm(od_matrix.project, request.POST, instance=od_matrix)
        if form.is_valid():
            form.save()
            messages.success(request, 'OD matrix cessfully created')
            return redirect('od_matrix_details', od_matrix.pk)
    else:
        form = ODMatrixForm(project=current_project,
            initial={'project': current_project})
    context = {
        'project': current_project,
        'form': form
    }
    return render(request, 'form.html', context)

def update_od_matrix_not_to_use(request, pk):
    od_matrix = ODMatrix.objects.get(id=pk)
    form = ODMatrixForm(instance=od_matrix)
    if request.method == 'POST':
        form = ODMatrixForm(request.POST, instance=od_matrix)
        if form.is_valid():
            form.save()
            return redirect('list_of_od_matrix', od_matrix.project.pk)

    context = {
        'form': form,
        'parent_template': 'base.html',
    }
    return render(request, 'update.html', context)

def update_od_matrix(request, pk):
    od_matrix = ODMatrix.objects.get(id=pk)
    if request.method == 'POST':
        form = ODMatrixForm(od_matrix.project, request.POST, instance=od_matrix)
        if form.is_valid():
            form.save()
            messages.success(request, 'OD Matrix successfully updated')
            return redirect('list_of_od_matrix', od_matrix.project.pk)
    else:
        form = ODMatrixForm(project=od_matrix.project, instance=od_matrix)

    context = {
        'form': form,
        'parent_template': 'base.html',
    }
    return render(request, 'update.html', context)



def od_matrix_details(request, pk):
    od_matrix = ODMatrix.objects.get(id=pk)
    tasks = od_matrix.backgroundtask_set.order_by('-start_date')[:5]
    context = {
        'od_matrix': od_matrix,
        'tasks': tasks,
    }
    return render(request, 'details.html', context)


def delete_od_matrix(request, pk):
    od_matrix_to_delete = ODMatrix.objects.get(id=pk)
    if request.method == 'POST':
        od_matrix_to_delete.delete()
        return redirect('list_of_od_matrix', od_matrix_to_delete.project.pk)

    context = {
        'od_matrix_to_delete': od_matrix_to_delete
    }
    return render(request, 'delete.html', context)

def od_pair_table(request, pk):
    """
    This function is for displaying database Edges table in front end UI.
    Users can sort, filter and paginate through pages
    """
    od_matrix = ODMatrix.objects.get(id=pk)
    od_pair = ODPair.objects.select_related().filter(matrix=od_matrix)
    filter = ODPairFilter(request.GET, queryset=od_pair)
    table = ODPairTable(filter.qs)
    RequestConfig(request).configure(table)  # For sorting table column
    table.paginate(page=request.GET.get("page", 1), per_page=15)

    current_path = request.get_full_path()
    network_attribute = current_path.split("/")[4]

    context = {
        "table": table,
        "filter": filter,
        'od_matrix': od_matrix,
        "network_attribute": network_attribute
    }
    return render(request, 'table/table.html', context)

def delete_od_pair(request, pk):
    od_matrix = ODMatrix.objects.get(id=pk)
    od_pair = ODPair.objects.filter(matrix=od_matrix)
    if od_pair:
        if request.method == 'POST':
            try:
                od_pair.delete()
            except Exception as e:
                msg = "Unable to delete ODPair of {}".format(self.od_matrix)
                messages.error(request, msg)
                return redirect('od_matrix_details', pk)
            else:
                msg = "ODPair of {} successfully deleted".format(od_matrix)
                messages.success(request, msg)
                return redirect('od_matrix_details', pk)
    else:
        messages.warning(request, "There is no data to delete")
        return redirect('od_matrix_details', pk)
    
    context = {
        'od_matrix': od_matrix,
        'od_pair_to_delete': od_pair,
    }
    return render(request, 'delete.html', context)