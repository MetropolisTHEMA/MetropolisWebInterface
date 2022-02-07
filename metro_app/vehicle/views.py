from metro_app.models import Project,  Vehicle, VehicleSet
from metro_app.forms import VehicleFileForm, VehicleForm, VehicleSetForm
from django.shortcuts import render, redirect
import json


def upload_vehicle(request, pk):
    vehicle_set = VehicleSet.objects.get(id=pk)
    if request.method == 'POST':
        list_vehicle = []
        form = VehicleFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['my_file']
            if file.name.endswith('.json'):
                data = json.load(file)
                for feature in data:
                    vehicle = Vehicle(
                        vehicle_set=vehicle_set,
                        vehicle_id=feature['id'],
                        name=feature.get('name', None),
                        length=feature.get('length', None),
                        speed_multiplicator=feature.get(
                            'speed_multiplicator', None),
                        speed_function=feature.get('speed_function', None)
                    )
                    list_vehicle.append(vehicle)
            Vehicle.objects.bulk_create(list_vehicle)
            return redirect('vehicle_set_details', pk)

    form = VehicleFileForm()
    context = {
        'form': form,
    }
    return render(request, 'vehicle/vehicle.html', context)


def add_vehicle(request, pk):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vehicle_set_details', pk)

    form = VehicleForm()
    context = {
        'form': form,
    }
    return render(request, 'views/form.html', context)


def update_vehicle(request, pk):

    vehicle = Vehicle.objects.get(id=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            return redirect('vehicle_set_details', pk)

    form = VehicleForm(instance=vehicle)
    context = {
        'form': form,
        'parent_template': 'index.html'
    }
    return render(request, 'update.html', context)


def delete_vehicle(request, pk):
    vehicle_to_delete = Vehicle.objects.get(id=pk)
    if request.method == 'POST':
        vehicle_to_delete.delete()
        return redirect('vehicle_set_details', pk)

    context = {
        'vehicle_to_delete': vehicle_to_delete,
    }
    return render(request, 'delete.html', context)


def create_vehicle_set(request, pk):
    """a vehicle set depends on a project. It
     must be created inside the project"""
    current_project = Project.objects.get(id=pk)
    if request.method == 'POST':
        form = VehicleSetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_details', current_project.pk)

    form = VehicleSetForm()
    context = {
        'form': form,
    }
    return render(request, 'views/form.html', context)


def vehicle_set_details(request, pk):
    vehicleset = VehicleSet.objects.get(id=pk)
    context = {
        'vehicleset': vehicleset,
    }
    return render(request, 'views/details.html', context)


def update_vehicle_set(request, pk):
    vehicle_set = VehicleSet.objects.get(id=pk)
    if request.method == 'POST':
        form = VehicleSetForm(request.POST, instance=vehicle_set)
        if form.is_valid():
            form.save()
            return redirect('project_details', vehicle_set.project.pk)

    form = VehicleSetForm(instance=vehicle_set)
    context = {
        'form': form,
        'parent_template': 'index.html'
    }
    return render(request, 'update.html', context)


def delete_vehicle_set(request, pk):
    vehicle_set_to_delete = VehicleSet.objects.get(id=pk)
    if request.method == 'POST':
        vehicle_set_to_delete.delete()
        return redirect('project_details', vehicle_set_to_delete.project.pk)

    context = {
        'vehicle_set_to_delete': vehicle_set_to_delete,
    }
    return render(request, 'delete.html', context)
