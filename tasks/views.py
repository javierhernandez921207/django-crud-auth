import os
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.utils import timezone
import stripe
from .forms import TaskForm
from .models import Product, Task
from django.contrib.auth.decorators import login_required
from .cart import Cart
# Create your views here.

def home(request):
    return render(request, 'home.html')


@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecomplete__isnull=True)
    return render(request, 'tasks.html', {'tasks': tasks, 'title': 'Pending Tasks'})


@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datecomplete__isnull=False)
    return render(request, 'tasks.html', {'tasks': tasks, 'title': 'Completed Tasks'})


@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {'form': TaskForm()})
    else:
        try:
            form = TaskForm(request.POST)
            newTask = form.save(commit=False)
            newTask.user = request.user
            newTask.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {'form': TaskForm(), 'error': 'Bad data passed in. Try again.'})


@login_required
def view_task(request, task_pk):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_pk, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'view_task.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_pk, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'view_task.html', {'task': task, 'form': form, 'error': 'Bad info'})


@login_required
def complete_task(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk, user=request.user)
    if request.method == 'POST':
        try:
            task.datecomplete = timezone.now()
            task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'view_task.html', {'task': task, 'error': 'Bad info'})
    else:
        return render(request, 'view_task.html', {'task': task})


@login_required
def delete_task(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')


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


@login_required
def shop(request):
    products = Product.objects.all()
    return render(request, 'shop.html', {'products': products})


@login_required
def cart(request):
    cart = Cart(request)
    products = cart.get_prods()
    total = 0
    for product in products:
        total += product.price
    return render(request, 'cart.html', {'products': products, 'total': total})


@login_required
def cart_add(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product = get_object_or_404(Product, pk=product_id)
        cart.add(product=product)
        cart_len = cart.__len__()
        response = JsonResponse({'cart_quantity': cart_len})
        return response


@login_required
def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product = get_object_or_404(Product, pk=product_id)
        cart.delete(product=product)
        cart_len = cart.__len__()
        response = JsonResponse({'cart_quantity': cart_len})
        return response
    return redirect('cart')


@login_required
def checkout(request):  
    cart = Cart(request)  
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    HOST_DIR = os.environ.get('HOST_DIR')
    line_items = []
    for product in cart.get_prods():
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': product.name,
                },
                'unit_amount': int(product.price * 100),
            },
            'quantity': 1,
        })
         
    checkout_session = stripe.checkout.Session.create(
        line_items= line_items,
        mode='payment',
        success_url= HOST_DIR + '/shop/success/',
        cancel_url= HOST_DIR + '/cart/',
    )
    request.session['checkout_session_id'] = checkout_session.id
    return redirect(checkout_session.url, code=303)

def success(request):
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    if request.session['checkout_session_id']:
        session = stripe.checkout.Session.retrieve(request.session['checkout_session_id'])
        print(session)
    cart = Cart(request)
    for product in cart.get_prods():
        cart.delete(product=product)
    return render(request, 'success.html')
