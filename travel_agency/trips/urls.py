from django.urls import path
from trips import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_trips, name='search_trips'),
    path('trip/<int:trip_id>/', views.trip_detail, name='trip_detail'),
    path('trip/<int:trip_id>/purchase/', views.purchase_trip, name='purchase_trip'),
    path('purchase/<int:purchase_id>/success/', views.purchase_success, name='purchase_success'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('contact/', views.contact, name='contact'),
]