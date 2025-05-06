from trips.models import Purchase

def user_purchases(request):
    if request.user.is_authenticated:
        purchases = Purchase.objects.filter(user=request.user).select_related('trip__destination_hotel__city').order_by('-purchase_date')[:5]
        return {'user_purchases': purchases}
    return {'user_purchases': []}