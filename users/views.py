from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm

#: Let's right our custom function for the sign up form.


def register(request):
    # If this is a post request we need to process the form data.
    if request.method == 'POST':
        # Let's create a form instance from POST data.
        form = RegisterForm(request.POST)
        # Check wether the form is valid
        if form.is_valid():
            # Now we have an instance from POST data and checked if it's valid,
            # let's save a new signed up object from the form's data.
            form.save()
            # Get username and display it in a message.
            username = form.cleaned_data.get('username')
            messages.success(request, 'Account created for ' + username)
            return redirect('login')
    # If a GET (or any other method) request, we will create a blank form
    else:
        form = RegisterForm()

    context = {'form': form}
    return render(request, 'registration/register.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, username)
            redirect('home')
        # else:
        #    messages.info(request, 'Username or password incorrect')

    context = {}
    return render(request, 'registration/login.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')
