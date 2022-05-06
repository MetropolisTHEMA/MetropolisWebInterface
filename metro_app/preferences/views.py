from django.shortcuts import render, redirect
from django.contrib import messages
from metro_app.forms import PreferencesForm
from metro_app.models import Project, Preferences, Vehicle
from metro_app.forms import PreferencesFileForm
import json
from datetime import timedelta


def list_of_preferences(request, pk):
    current_project = Project.objects.get(id=pk)
    preferences = Preferences.objects.filter(project=current_project)
    total_preferences = preferences.count()
    context = {
        'current_project': current_project,
        'preferences': preferences,
        'total_preferences': total_preferences,

    }
    return render(request, 'list.html', context)

def add_preferences(request, pk):
    current_project = Project.objects.get(id=pk)
    if request.method == 'POST':
        preference = Preferences(project=current_project)
        form = PreferencesForm(request.POST, instance=preference)
        print(form)
        if form.is_valid():
            form.save()
            return redirect('project_details', current_project.pk)
   
    form = PreferencesForm(initial={'project': current_project})

    current_path = request.get_full_path()
    context = {
        'project': current_project,
        'form': form,
        'url_path': current_path
    }
    return render(request, 'form.html', context)

def read_field_func(field, std=0):

    try:
        isinstance(field.keys, dict)
    except AttributeError:
        field_distr = 0
        field_mean = 0
        field_std = std
        #raise Exception('error of pring')
        return field_distr, field_mean, field_std
    else:

        field_distribution = list(field.keys())[0]
        if field_distribution == 'Constant':
            field_distr = 0
            field_mean = field['Constant']
            field_std = std
        elif  field_distribution == 'Uniform':
            field_distr = 1
            field_mean = field['Uniform']['mean']
            field_std = field['Uniform']['std']
        elif field_distribution == 'Normal':
            field_distr = 2
            field_mean = field['Normal']['mean']
            field_std = field['Normal']['std']
        elif field_distribution == 'Log-normal':
            field_distr = 3
            field_mean = field['Uniform']['mean']
            field_std = field['Uniform']['std']
        return field_distr, field_mean, field_std, field_distribution

def read_field_func2(field, std=0):

    try:
        list(field.keys())[0]
    except AttributeError:
        field_model = 1
        field_distr = 0
        field_mean = 0
        field_std = std
        return field_distr, field_mean, field_std, field_model
    else:
        field_distribution = list(field.keys())[0]
        if field_distribution == 'Logit':
            field_model = 1
            field_distr = 1
            field_mean = field["Logit"]['mu']['Normal']['mean']
            field_std = field["Logit"]['mu']['Normal']['std']

        elif field_distribution == 'Constant':
            distribution = field['Constant']
            field_model = 1
            try:
                list(distribution.keys())[0]
            except AttributeError:
                field_distr = 0
                field_mean = 0
                field_std = 0
                return field_distr, field_mean, field_std,field_model
            else:
                if list(distribution.keys())[0] == 'Constant':
                    field_distr = 0
                    field_mean = 0
                    field_std = 0
                elif list(distribution.keys())[0] == 'Uniform':
                    field_distr = 1 
                    field_mean = distribution['Uniform']['mean']
                    field_std = distribution['Uniform']['std']
                elif list(distribution.keys())[0] == 'Normal':
                    field_distr = 2
                    field_mean = distribution['Normal']['mean']
                    field_std = distribution['Normal']['std']
                elif list(distribution.keys())[0] == 'Log-normal':
                    field_distr = 3
                    field_mean = distribution['Log-normal']['mean']
                    field_std = distribution['Log-normal']['std']     

    return field_distr, field_mean, field_std, field_model


def upload_preferences(request, pk):
    # storage = messages.get_messages(request)
    # storage.used = True
    vehicles = Vehicle.objects.all()
    if not vehicles.exists():
        msg = "Please upload or set Vehicle first"
        messages.warning(request, msg)
        return redirect('project_details', pk)

    project = Project.objects.get(id=pk)
    preferences = Preferences.objects.filter(project=project)
    if not preferences:
        messages.warning(request, "Fail! Preferences already contains data.")
        return redirect('upload_preferences', pk)

    if request.method == 'POST':
        vehicle_instance_dict = {vehicle.vehicle_id: vehicle for vehicle in vehicles}
        form = PreferencesFileForm(request.POST, request.FILES)
        if form.is_valid():
            list_preferences = []
            file = request.FILES['my_file']
            data = json.load(file)
            if type(data) == list:
                for feature in data:
                    try:
                        vehicle=vehicle_instance_dict[feature['vehicle']]
                    except KeyError:
                        messages.error(request, "vehicle ids don't match with vehicle table data")
                        return redirect('project_details', pk)
                    else:
                        mode_choice = feature['mode_choice']
                        if mode_choice == 'Deterministic':
                            mode_choice_model = 0
                            mode_choice_mu_distr=0
                            mode_choice_mu_mean=0
                            mode_choice_mu_std=0
                        elif mode_choice == 'First':
                            mode_choice_model = 2
                            mode_choice_mu_distr=0
                            mode_choice_mu_mean=0
                            mode_choice_mu_std=0
                        elif type(mode_choice) == dict:
                            mode_choice_model_key = list(mode_choice.keys())[0]
                            if mode_choice_model_key == 'Logit':
                                mode_choice_model = 1
                                mode_choice_mu_distr = 2
                                mode_choice_mu_mean = mode_choice['Logit']['mu']['Normal']['mean']
                                mode_choice_mu_std = mode_choice['Logit']['mu']['Normal']['std']

                        # departure_time_model_distribution
                        dep_time_model = feature['departure_time_model']
                        dep_time_model = read_field_func2(dep_time_model)
                            
                        dep_time_car_mu_distr = feature.get('dep_time_car_mu_dist', 1)
                        dep_time_car_mu_mean = feature.get('dep_time_car_mu_mean', None)
                        dep_time_car_mu_std = feature.get('dep_time_car_mu_std', None)

                        t_star = feature['t_star']
                        t_star = read_field_func(t_star, 0)
                        beta = feature['beta']
                        beta = read_field_func(beta, 0)
                        gamma = feature['gamma']
                        gamma = read_field_func(gamma)
                    
                        delta = feature['delta']
                        delta = read_field_func(delta,0)

                        preference_instance = Preferences(
                            project=project,
                            mode_choice_model=mode_choice_model,
                            mode_choice_mu_distr=mode_choice_mu_distr,
                            mode_choice_mu_mean=mode_choice_mu_mean,
                            mode_choice_mu_std=mode_choice_mu_std,
                            t_star_distr=t_star[0],
                            t_star_mean=timedelta(seconds=float(t_star[1])),
                            t_star_std=timedelta(seconds=float(t_star[2])),
                            delta_distr=delta[0],
                            delta_mean=timedelta(seconds=float(delta[1])),
                            delta_std=timedelta(seconds=float(delta[2])),
                            beta_distr=beta[0],
                            beta_mean=beta[1],
                            beta_std=beta[2],
                            gamma_distr=gamma[0],
                            gamma_mean=gamma[1],
                            gamma_std=gamma[2],
                            desired_arrival=feature['desired_arrival'],
                            vehicle=vehicle,
                            dep_time_car_choice_model=1,  # dep_time_model[3],
                            dep_time_car_mu_distr=dep_time_car_mu_distr,
                            dep_time_car_mu_mean=dep_time_car_mu_mean,
                            dep_time_car_mu_std=dep_time_car_mu_std,
                            dep_time_car_constant_distr=dep_time_model[0],
                            dep_time_car_constant_mean=timedelta(seconds=dep_time_model[1]),
                            dep_time_car_constant_std=timedelta(seconds=dep_time_model[2]),
                            car_vot_distr=3,
                            car_vot_mean=feature['car_vot']['Log-normal']['mean'],
                            car_vot_std=feature['car_vot']['Log-normal']['std'],
                            name=feature.get('name', None),
                            comment=feature.get('comment', 'No comment'),
                            tags=feature.get('tags', 'No tags')               
                        )
                        list_preferences.append(preference_instance)
            elif type(data) == dict:
                pass
            try:
                Preferences.objects.bulk_create(list_preferences)
            except Exception as e:
                messages.error(request, e)
                return redirect('upload_preferences', pk)
            else:
                preferences = Preferences.objects.all()
                if preferences.count() > 0:
                    messages.success(request, 'preferences file successfully\
                                            uploaded')
                    return redirect('project_details', pk)
                else:
                    messages.warning(request, 'No data is uploaded')
                    return redirect('project_details', pk)
    
    form = PreferencesFileForm()
    context = {
        'form': form
    }
    return render(request, 'preferences/preferences.html', context)



def update_preferences(request, pk):
    preference = Preferences.objects.get(id=pk)
    if request.method == 'POST':
        form = PreferencesForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            return redirect('list_of_preferences', preference.project.pk)

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
        return redirect('list_of_preferences', preference_to_delete.project.pk)

    context = {
        'preference_to_delete': preference_to_delete
    }
    return render(request, 'delete.html', context)
