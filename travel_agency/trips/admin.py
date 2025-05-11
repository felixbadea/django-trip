from django.contrib import admin
from trips.models import Continent, Country, City, Hotel, Airport, Trip, Purchase

# Register your models here.
"""
admin.site.register(Continent)
admin.site.register(Country)
admin.site.register(City)
admin.site.register(Hotel)
admin.site.register(Airport)
admin.site.register(Trip) --eliminata pe motiv de conflict cu @admin.register(Trip)
admin.site.register(Purchase)
"""

# Admin pentru Trip
@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        'destination_hotel',
        'destination_city',
        'departure_city',
        'departure_date',
        'trip_type',
        'price_adult',
        'places_adults',
        'promoted',
    )
    list_filter = ('trip_type', 'promoted', 'departure_date', 'destination_hotel__city__country__continent')
    search_fields = (
        'destination_hotel__name',
        'destination_city__name',
        'departure_city__name',
    )
    date_hierarchy = 'departure_date'
    list_per_page = 20

    # Personalizarea formularului
    fieldsets = (
        ('General', {
            'fields': ('promoted', 'trip_type'),
        }),
        ('Locations', {
            'fields': (
                ('departure_city', 'departure_airport'),
                ('destination_city', 'destination_hotel', 'destination_airport'),
            ),
        }),
        ('Details', {
            'fields': (
                ('departure_date', 'return_date'),
                'length_of_stay',
                ('price_adult', 'price_child'),
                ('places_adults', 'places_children'),
            ),
        }),
    )

    # Filtrarea dropdown-urilor pentru ForeignKey
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'departure_airport':
            kwargs['queryset'] = Airport.objects.select_related('city').order_by('city__name', 'name')
        if db_field.name == 'destination_airport':
            kwargs['queryset'] = Airport.objects.select_related('city').order_by('city__name', 'name')
        if db_field.name == 'destination_hotel':
            kwargs['queryset'] = Hotel.objects.select_related('city__country').order_by('city__name', 'name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Admin pentru Purchase
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('trip', 'adults', 'children', 'total_amount', 'purchase_date')
    list_filter = ('purchase_date', 'trip__destination_city')
    search_fields = ('trip__destination_hotel__name', 'trip__destination_city__name')
    date_hierarchy = 'purchase_date'
    list_per_page = 20

# Admin pentru alte modele (personalizare simplă)
@admin.register(Continent)
class ContinentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'continent')
    list_filter = ('continent',)
    search_fields = ('name',)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country__continent', 'country')
    search_fields = ('name', 'country__name')

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'standard')
    list_filter = ('standard', 'city__country')
    search_fields = ('name', 'city__name')

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')
    list_filter = ('city__country',)
    search_fields = ('name', 'city__name')

