from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm  # Assume this is your custom signup form

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request,
                f'Account created successfully for {username}!',
                extra_tags='alert alert-success alert-dismissible show'
            )
            return redirect('accounts:login')
        else:
            messages.error(
                request,
                'Signup failed. Please correct the errors below.',
                extra_tags='alert alert-warning alert-dismissible show'
            )
    else:
        form = CustomUserCreationForm()

    context = {
        'form': form,
        'title': 'Register Users',
    }
    return render(request, 'accounts/signup.html', context)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(
                request,
                f'Welcome back, {user.username}!',
                extra_tags='alert alert-success alert-dismissible show'
            )
            return redirect('home')  # Replace 'home' with your dashboard or homepage
        else:
            messages.error(
                request,
                'Invalid username or password. Please try again.',
                extra_tags='alert alert-warning alert-dismissible show'
            )
    else:
        form = AuthenticationForm()

    context = {
        'form': form,
        'title': 'Login',
    }
    return render(request, 'accounts/login.html', context)


def logout_view(request):
    logout(request)
    messages.success(
        request,
        'You have been logged out successfully.',
        extra_tags='alert alert-info alert-dismissible show'
    )
    return redirect('accounts:login')  # Redirect to login page after logout
