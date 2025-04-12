from django.shortcuts import render, redirect, get_object_or_404
from trips.models import Trip, Country, City, Continent, Purchase
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

# Create your views here.

def home(request):
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
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
        messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'trips/registration/login.html', {'form': form})

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