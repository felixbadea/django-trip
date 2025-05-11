from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Create your models here.

class Continent(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    continent = models.ForeignKey(Continent, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='city_images/', null=True, blank=True)
    video_url = models.URLField(max_length=200, null=True, blank=True, help_text="URL to a YouTube embed or video file")
    
    def __str__(self):
        return f"{self.name}, {self.country}"
    class Meta:
        unique_together = ['name', 'country']

class Hotel(models.Model):
    name = models.CharField(max_length=100)
    standard = models.IntegerField(choices=[(i, f"{i} stars") for i in range(1, 6)])  # 1-5 stars
    description = models.TextField()
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class Airport(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.city})"

class Trip(models.Model):
    TRIP_TYPES = (
        ('BB', 'Bed & Breakfast'),
        ('HB', 'Half Board'),
        ('FB', 'Full Board'),
        ('AI', 'All Inclusive'),
    )
    departure_city = models.ForeignKey(City, related_name='departure_trips', on_delete=models.CASCADE)
    departure_airport = models.ForeignKey(Airport, related_name='departure_trips', on_delete=models.CASCADE)
    destination_city = models.ForeignKey(City, related_name='destination_trips', on_delete=models.CASCADE)
    destination_hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    destination_airport = models.ForeignKey(Airport, related_name='destination_trips', on_delete=models.CASCADE)
    departure_date = models.DateField()
    return_date = models.DateField()
    length_of_stay = models.IntegerField()  # in days
    trip_type = models.CharField(max_length=2, choices=TRIP_TYPES)
    price_adult = models.DecimalField(max_digits=10, decimal_places=2)
    price_child = models.DecimalField(max_digits=10, decimal_places=2)
    promoted = models.BooleanField(default=False)
    places_adults = models.IntegerField()
    places_children = models.IntegerField()

    def __str__(self):
        return f"{self.departure_city} to {self.destination_hotel} ({self.departure_date})"
    
    def clean(self):
        if self.return_date <= self.departure_date:
            raise ValidationError("Return date must be after departure date.")
        if self.places_adults < 0 or self.places_children < 0:
            raise ValidationError("Number of places cannot be negative.")

  

class Purchase(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    adults = models.PositiveIntegerField()
    children = models.PositiveIntegerField()
    purchase_date = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.adults + self.children == 0:
            raise ValueError("At least one adult or child must be selected.")
        if self.adults > self.trip.places_adults or self.children > self.trip.places_children:
            raise ValueError("Not enough places available.")
        self.trip.places_adults -= self.adults
        self.trip.places_children -= self.children
        self.trip.save()
        super().save(*args, **kwargs)
    
    @property
    def total_amount(self):
        return self.adults * self.trip.price_adult + self.children * self.trip.price_child

    def __str__(self):
        return f"Purchase of {self.trip} for {self.adults} adults, {self.children} children"
    

    

    def save(self, *args, **kwargs):
        """Suprascrie save pentru a calcula total_amount și a verifica locurile."""
        # Verifică locurile disponibile
        if self.adults > self.trip.places_adults or self.children > self.trip.places_children:
            raise ValueError("Not enough places available for this trip!")
        
       
        # Redu locurile disponibile
        self.trip.places_adults -= self.adults
        self.trip.places_children -= self.children
        self.trip.save()

        super().save(*args, **kwargs)
    
    
@login_required
def purchase_trip(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    
    if request.method == 'POST':
        adults = int(request.POST.get('adults', 0))
        children = int(request.POST.get('children', 0))
        
        try:
            purchase = Purchase(trip=trip, adults=adults, children=children, user=request.user)  # Adăugat user
            purchase.save()
            return redirect('purchase_success', purchase_id=purchase.id)
        except ValueError as e:
            return render(request, 'trips/purchase.html', {'trip': trip, 'error': str(e)})
    
    return render(request, 'trips/purchase.html', {'trip': trip})

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} - {self.email}'
    
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='confirmed')

    def __str__(self):
        return f"Booking for {self.trip.destination_hotel.city.name} by {self.user.username}"