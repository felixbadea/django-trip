function validateSearchForm() {
    var departureCity = document.getElementsByName('departure_city')[0].value;
    var destinationCity = document.getElementsByName('destination_city')[0].value;
    var departureDate = document.getElementsByName('departure_date')[0].value;
    var tripType = document.getElementsByName('trip_type')[0].value;
    var hotelStandard = document.getElementsByName('hotel_standard')[0].value;
    var lengthOfStay = document.getElementsByName('length_of_stay')[0].value;

    if (!departureCity && !destinationCity && !departureDate && !tripType && !hotelStandard && !lengthOfStay) {
        alert('Please select at least one search criterion.');
        return false;
    }
    if (lengthOfStay && parseInt(lengthOfStay) < 1) {
        alert('Length of stay must be at least 1 day.');
        return false;
    }
    return true;
}