function preferences(){
    document.getElementById("id_mode_choice_mu_distr").disabled = true
    document.getElementById("id_mode_choice_mu_mean").disabled = true
    document.getElementById("id_mode_choice_mu_std").disabled = true
    document.getElementById("id_t_star_std").disabled = true
    /*document.getElementById("id_t_star_mean").disabled = true*/
    document.getElementById("id_delta_std").disabled = true
   /* document.getElementById("id_delta_mean").disabled = true*/
   /* document.getElementById("id_beta_mean").disabled = true*/
    document.getElementById("id_beta_std").disabled = true
    /*document.getElementById("id_gamma_mean").disabled = true*/
    document.getElementById("id_gamma_std").disabled = true
    document.getElementById("id_car_vot_std").disabled = true

    choice_model = document.getElementById("id_mode_choice_model")
    choice_model.addEventListener('change', function(){
        if (choice_model.value =="0"){
            document.getElementById("id_mode_choice_mu_distr").disabled = true
            document.getElementById("id_mode_choice_mu_mean").disabled = true
            document.getElementById("id_mode_choice_mu_std").disabled = true
        }
        else {
            document.getElementById("id_mode_choice_mu_distr").disabled = false
            document.getElementById("id_mode_choice_mu_mean").disabled = false
            document.getElementById("id_mode_choice_mu_std").disabled = false
        }
    })

    t_star = document.getElementById("id_t_star_distr")
    t_star.addEventListener('change', function(){
        if (t_star.value =="0"){
            /*document.getElementById("id_t_star_distr").disabled = true*/
            document.getElementById("id_t_star_std").disabled = true
            /*document.getElementById("id_t_star_mean").disabled = true*/
        }
        else {
            /*document.getElementById("id_t_star_distr").disabled = false*/
            document.getElementById("id_t_star_std").disabled = false
            */document.getElementById("id_t_star_mean").disabled = false*/
        }
    })

    delta = document.getElementById("id_delta_distr")
    delta.addEventListener('change', function(){
        if (delta.value =="0"){
            /*document.getElementById("id_delta_mean").disabled = true*/
            document.getElementById("id_delta_std").disabled = true
        }
        else {
            /*document.getElementById("id_delta_mean").disabled = false*/
            document.getElementById("id_delta_std").disabled = false
        }
    })
    
    beta = document.getElementById("id_beta_distr")
    beta.addEventListener('change', function(){
        if (beta.value =="0"){
            /*document.getElementById("id_beta_mean").disabled = true*/
            document.getElementById("id_beta_std").disabled = true
        }
        else {
            /*document.getElementById("id_beta_mean").disabled = false*/
            document.getElementById("id_beta_std").disabled = false
        }
    })

    gamma = document.getElementById("id_gamma_distr")
    gamma.addEventListener('change', function(){
        if (gamma.value =="0"){
            /*document.getElementById("id_gamma_mean").disabled = true*/
            document.getElementById("id_gamma_std").disabled = true
        }
        else {
            /*document.getElementById("id_gamma_mean").disabled = false*/
            document.getElementById("id_gamma_std").disabled = false
        }
    })

    car_vot = document.getElementById("id_car_vot_distr")
    car_vot.addEventListener('change', function(){
        if (car_vot.value == "0"){
            document.getElementById("id_car_vot_std").disabled = true
        }
        else {
            document.getElementById("id_car_vot_std").disabled = false
        }
    })

    dep_time_car_choice_model = document.getElementById("id_dep_time_car_choice_model")
    dep_time_car_choice_model.addEventListener('change', function(){
        console.log(dep_time_car_choice_model)
        if (dep_time_car_choice_model.value == "1"){
            document.getElementById("id_dep_time_car_mu_distr").disabled = true
            document.getElementById("id_dep_time_car_mu_mean").disabled = true
            document.getElementById("id_dep_time_car_mu_std").disabled = true

            document.getElementById("id_dep_time_car_constant_distr").disabled = false
            document.getElementById("id_dep_time_car_constant_mean").disabled = false
            document.getElementById("id_dep_time_car_constant_std").disabled = false
        }
        else {
            document.getElementById("id_dep_time_car_mu_distr").disabled = false
            document.getElementById("id_dep_time_car_mu_mean").disabled = false
            document.getElementById("id_dep_time_car_mu_std").disabled = false

            document.getElementById("id_dep_time_car_constant_distr").disabled = true
            document.getElementById("id_dep_time_car_constant_mean").disabled = true
            document.getElementById("id_dep_time_car_constant_std").disabled = true
        }
    })

    console.log(dep_time_car_choice_model);
}

preferences();