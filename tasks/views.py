from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
# Create your views here.


def home(request):
    return render(request, 'home.html')

def tasks(request):
    return render(request, 'tasks.html')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': UserCreationForm()})
    else:
        # POST, create a new user
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except:
                return render(request, 'signup.html', {'form': UserCreationForm(), 'error': 'Username already taken'})
        else:
            return render(request, 'signup.html', {'form': UserCreationForm(), 'error': 'Passwords did not match'})

def singout(request):
    logout(request)
    return redirect('index')

def singin(request):
    if request.method == 'POST':
        user = AuthenticationForm(data=request.POST)
        if user.is_valid():
            # log in the user
            user = user.get_user()
            login(request, user)
            return redirect('tasks')
        else:
            return render(request, 'signin.html', {'form': AuthenticationForm(), 'error': 'Username or password is incorrect'})
    else:
        return render(request, 'signin.html', {'form': AuthenticationForm()})
