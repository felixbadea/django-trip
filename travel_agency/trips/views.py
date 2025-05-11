from django.shortcuts import render, redirect, get_object_or_404
from trips.models import Trip, Country, City, Continent, Purchase, ContactMessage
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseRedirect

# Create your views here.

def home(request):
    print(f"Request URL: {request.path}")  # Debug
    promoted_trips = Trip.objects.filter(promoted=True).select_related(
        'destination_hotel__city__country__continent',
        'departure_city__country__continent',
        'departure_airport',
        'destination_airport'
    )[:3]
    upcoming_trips = Trip.objects.filter(departure_date__gte=timezone.now()).select_related(
        'destination_hotel__city__country__continent',
        'departure_city__country__continent'
    )[:3]
    popular_countries = Country.objects.filter(
        city__destination_trips__isnull=False
    ).distinct()[:3]
    popular_continents = Continent.objects.filter(
        country__city__destination_trips__isnull=False
    ).distinct()[:3]

    context = {
        'promoted_trips': promoted_trips,
        'upcoming_trips': upcoming_trips,
        'popular_countries': popular_countries,
        'popular_continents': popular_continents,
    }
    return render(request, 'trips/home.html', context)

def search_trips(request):
    trips = Trip.objects.all()
    query = request.GET.get('q')
    country = request.GET.get('country')
    continent = request.GET.get('continent')
    date_start = request.GET.get('date_start')
    date_end = request.GET.get('date_end')
    
    if query:
        trips = trips.filter(
            Q(destination_city__name__icontains=query) |
            Q(destination_hotel__name__icontains=query) |
            Q(departure_city__name__icontains=query)
        )
    
    if country:
        trips = trips.filter(destination_hotel__city__country__id=country)
    
    if continent:
        trips = trips.filter(destination_hotel__city__country__continent=continent)
    
    if date_start:
        try:
            date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
            trips = trips.filter(departure_date__gte=date_start)
        except ValueError:
            pass
    
    if date_end:
        try:
            date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
            trips = trips.filter(departure_date__lte=date_end)
        except ValueError:
            pass
    
    # Paginare
    paginator = Paginator(trips, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Context pentru formular
    cities = City.objects.all()
    countries = Country.objects.all()
    continents = Continent.objects.all()
    trip_types = Trip.TRIP_TYPES
    hotel_standards = [(i, f"{i} stars") for i in range(1, 6)]

    return render(request, 'trips/search.html', {
        'page_obj': page_obj,
        'trips': trips,
        'cities': cities,
        'countries': countries,
        'continents': continents,
        'trip_types': trip_types,
        'hotel_standards': hotel_standards,
        'query': query,
    })

def trip_detail(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    similar_trips = Trip.objects.filter(destination_city=trip.destination_city).exclude(id=trip_id)[:3]
    return render(request, 'trips/trip_detail.html', {'trip': trip, 'similar_trips': similar_trips})



def purchase_success(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    return render(request, 'trips/purchase_success.html', {'purchase': purchase})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! Please log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'trips/registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                # Suport pentru 'next'
                next_url = request.POST.get('next', request.GET.get('next', 'home'))
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AuthenticationForm()
    return render(request, 'trips/registration/login.html', {
        'form': form,
        'next': request.GET.get('next', '')
    })

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

@login_required
def purchase_trip(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    
    if request.method == 'POST':
        adults = int(request.POST.get('adults', 0))
        children = int(request.POST.get('children', 0))
        
        try:
            purchase = Purchase(trip=trip, adults=adults, children=children, user=request.user)
            purchase.save()
            return redirect('purchase_success', purchase_id=purchase.id)
        except ValueError as e:
            return render(request, 'trips/purchase.html', {'trip': trip, 'error': str(e)})
    
    return render(request, 'trips/purchase.html', {'trip': trip})

def about(request):
    return render(request, 'trips/about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        ContactMessage.objects.create(name=name, email=email, message=message)
        # Trimite email (opțional)
        try:
            send_mail(
                subject=f'Mesaj nou de la {name}',
                message=f'Mesaj: {message}\nEmail: {email}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['badeafelix611@gmail.com'],
            )
            return HttpResponseRedirect('/?success=1')
        except Exception as e:
            print(f"Eroare la trimiterea email-ului: {e}")
            return render(request, 'base.html', {'error': f'Eroare la trimiterea mesajului: {e}'})
    return render(request, 'base.html') # Fallback pentru acces direct

# Gestionarea username-ului si a password pentru userul logat
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User

@login_required
def manage_account(request):
    if request.method == 'POST':
        # Gestionare schimbare username si password
        #username_form = UserChangeForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)
        """
        if username_form.is_valid():
            username_form.save()
            messages.success(request, 'Username updated successfully!')
            return redirect('manage_account')
        """
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # se păstrează utilizatorul logat
            messages.success(request, 'Password updated successfully!')
            return redirect('manage_account')
        
        messages.error(request, 'Please correct the errors below.')
    else:
        #username_form = UserChangeForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)
    
    return render(request, 'manage_account.html', {
        #'username_form': username_form,
        'password_form': password_form
    })
