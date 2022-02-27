from django.shortcuts import render, redirect
from django.contrib import messages
from metro_app.forms import PreferencesForm
from metro_app.models import Project, Preferences, Vehicle
from metro_app.forms import PreferencesFileForm
import json


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


def read_file_func(file):
    data = json.load(file)
    pass



def upload_preferences(request, pk):
    project = Project.objects.get(id=pk)
    preferences = Preferences.objects.all()
    if preferences.count() > 0:
        messages.warning(request, "Fail! Agent already contains agents data. \
                            Delete them before importing again")
        return redirect('upload_preferences', pk)

    if request.method == 'POST':
        vehicles = Vehicle.objects.all()
        vehicle_instance_dict = {vehicle.vehicle_id: vehicle for vehicle in vehicles}
        form = PreferencesFileForm(request.POST, request.FILES)
        if form.is_valid():
            list_preferences = []
            file = request.FILES['my_file']
            data = json.load(file)
            
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

                        departure_time_model = feature['departure_time_model']
                        departure_time_model_distribution = list(departure_time_model.keys())[0]
                        if departure_time_model_distribution == 'Logit':
                            dep_time_car_constant_distr = 1
                            dep_time_car_constant_mean = departure_time_model["Logit"]['mu']['Normal']['mean']
                            dep_time_car_constant_std = departure_time_model["Logit"]['mu']['Normal']['std']
                        elif departure_time_model_distribution == 'Constant':
                            distribution = departure_time_model["Constant"]
                            dep_time_car_choice_model = 1
                            if distribution == 'Constant':
                                dep_time_car_constant_distr = 0
                                dep_time_car_constant_mean = 0
                                dep_time_car_constant_std = 0
                            elif distribution == 'Uniform':
                                dep_time_car_constant_distr = 1
                                dep_time_car_constant_mean = distribution['Uniform']['mean']
                                dep_time_car_constant_std = distribution['Uniform']['std']
                            elif distribution == 'Normal':
                                dep_time_car_constant_distr = 2
                                dep_time_car_constant_mean = distribution['Normal']['mean']
                                dep_time_car_constant_std = distribution['Normal']['std']
                            elif distribution == 'Log-normal':
                                dep_time_car_constant_distr = 3
                                dep_time_car_constant_mean = distribution['Log-normal']['mean']
                                dep_time_car_constant_std = distribution['Log-normal']['std']
                            
                            delta = feature['delta']
                            delta_distribution = list(delta.keys())[0]
                            if delta_distribution == 'Constant':
                                delta_distr = 1
                                delta_mean = delta['Constant']
                                delta_std = "125"
                            
                            dep_time_car_mu_distr = feature.get('dep_time_car_mu_dist', 1)
                            dep_time_car_mu_mean = feature.get('dep_time_car_mu_mean', None)
                            dep_time_car_mu_std = feature.get('dep_time_car_mu_std', None)

                        t_star = feature['t_star']
                        t_star_distribution = list(t_star.keys())[0]
                        if t_star_distribution == 'Constant':
                            t_star_distr = 0
                            t_star_mean = t_star['Constant']
                            t_star_std = 0
                        elif t_star_distribution == 'Uniform':
                            t_star_distr = 1
                            t_star_mean = t_star['Uniform']['mean']
                            t_star_std =t_star['Uniform']['std'],
                        elif t_star_distribution == 'Normal':
                            t_star_distr = 2,
                            t_star_mean = t_star['Normal']['mean']
                            t_star_std =t_star['Normal']['std'],
                        elif t_star_distribution == 'Log-normal':
                            t_star_distr = 3,
                            t_star_mean = t_star['Uniform']['mean']
                            t_star_std =t_star['Uniform']['std']

                        beta = feature['beta']
                        beta_distribution = list(beta.keys())[0]
                        if beta_distribution == 'Constant':
                            beta_distr = 0
                            beta_mean = beta['Constant']
                            beta_std = 0
                        elif beta_distribution == 'Uniform':
                            beta_distr = 1
                            beta_mean = beta['Uniform']['mean']
                            beta_std =beta['Uniform']['std'],
                        elif beta_distribution == 'Normal':
                            beta_distr = 2,
                            beta_mean = beta['Normal']['mean']
                            beta_std = beta['Normal']['std'],
                        elif beta_distribution == 'Log-normal':
                            beta_distr = 3,
                            beta_mean = beta['Uniform']['mean']
                            beta_std = beta['Uniform']['std'],

                        gamma = feature['gamma']
                        gamma_distribution = list(gamma.keys())[0]
                        if gamma_distribution == 'Constant':
                            gamma_distr = 0
                            gamma_mean = gamma['Constant']
                            gamma_std = 0
                        elif gamma_distribution == 'Uniform':
                            gamma_distr = 1
                            gamma_mean = gamma['Uniform']['mean']
                            gamma_std =gamma['Uniform']['std'],
                        elif gamma_distribution == 'Normal':
                            gamma_distr = 2,
                            gamma_mean = gamma['Normal']['mean']
                            gamma_std = gamma['Normal']['std'],
                        elif gamma_distribution == 'Log-normal':
                            gamma_distr = 3,
                            gamma_mean = gamma['Uniform']['mean']
                            gamma_std = gamma['Uniform']['std'],

                        delta = feature['delta']
                        delta_distribution = list(delta.keys())[0]
                        if delta_distribution == 'Constant':
                            delta_distr = 0
                            delta_mean = delta['Constant']
                            delta_std = "0"
                        elif delta_distribution == 'Uniform':
                            delta_distr = 1
                            delta_mean = delta['Uniform']['mean']
                            delta_std =delta['Uniform']['std'],
                        elif delta_distribution == 'Normal':
                            delta_distr = 2,
                            delta_mean = delta['Normal']['mean']
                            delta_std = delta['Normal']['std'],
                        elif delta_distribution == 'Log-normal':
                            delta_distr = 3,
                            delta_mean = delta['Uniform']['mean']
                            delta_std = delta['Uniform']['std']

                        preference_instance = Preferences(
                            project=project,
                            mode_choice_model=mode_choice_model,
                            mode_choice_mu_distr=mode_choice_mu_distr,
                            mode_choice_mu_mean=mode_choice_mu_mean,
                            mode_choice_mu_std=mode_choice_mu_std,
                            t_star_distr=t_star_distr,
                            t_star_mean=t_star_mean, # feature['t_star']['Uniform']['mean'],
                            t_star_std=t_star_std, # feature['t_star']['Uniform']['std'],
                            delta_distr=delta_distr,
                            delta_mean=delta['Constant'],
                            delta_std=delta_std,
                            beta_distr=2,
                            beta_mean=feature['beta']['Normal']['mean'],
                            beta_std=feature['beta']['Normal']['std'],
                            gamma_distr=2,
                            gamma_mean=feature['gamma']['Normal']['mean'],
                            gamma_std=feature['gamma']['Normal']['std'],
                            desired_arrival=feature['desired_arrival'],
                            vehicle=vehicle,
                            dep_time_car_choice_model=dep_time_car_choice_model,
                            dep_time_car_mu_distr=dep_time_car_mu_distr,
                            dep_time_car_mu_mean=dep_time_car_mu_mean,
                            dep_time_car_mu_std=dep_time_car_mu_std,
                            #dep_time_car_constant_distr=dep_time_car_constant_distr,
                            #dep_time_car_constant_mean=dep_time_car_constant_mean,
                            #dep_time_car_constant_std=dep_time_car_constant_std,
                            car_vot_distr=3,
                            car_vot_mean=feature['car_vot']['Log-normal']['mean'],
                            car_vot_std=feature['car_vot']['Log-normal']['std'],
                            name=feature.get('name', None),
                            comment=feature.get('comment', 'No comment'),
                            tags=feature.get('tags', 'No tags')               
                        )
                        list_preferences.append(preference_instance)
            elif type(data) == dif type(data) == list:ict:
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
