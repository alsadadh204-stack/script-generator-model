from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json
from .models import UserProfile


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email_or_user = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        # Check by email or username
        user = None
        try:
            target = User.objects.filter(email=email_or_user).first() or User.objects.filter(username=email_or_user).first()
            if target:
                user = authenticate(request, username=target.username, password=password)
        except Exception:
            pass

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password. Use demo login or create an account.')

    return render(request, 'pages/auth/login.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, 'Please provide an email and password.')
            return render(request, 'pages/auth/signup.html')

        if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'pages/auth/signup.html')

        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.full_name = full_name or email.split('@')[0].capitalize()
        profile.save()

        login(request, user)
        return redirect('home')

    return render(request, 'pages/auth/signup.html')


def logout_view(request):
    logout(request)
    return redirect('landing')


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'pages/profile.html', {'profile': profile})


@login_required
def update_profile_settings(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            profile = request.user.profile

            if 'theme' in data:
                profile.theme = data['theme']
            if 'language' in data:
                profile.language = data['language']
            if 'preferred_model' in data:
                profile.preferred_model = data['preferred_model']
            if 'full_name' in data:
                profile.full_name = data['full_name']

            profile.save()
            return JsonResponse({'status': 'success', 'message': 'Preferences updated successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
