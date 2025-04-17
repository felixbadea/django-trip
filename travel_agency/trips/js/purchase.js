function validateForm() {
    var adults = parseInt(document.getElementsByName('adults')[0].value);
    var children = parseInt(document.getElementsByName('children')[0].value);
    if (adults + children <= 0) {
        alert('Please select at least one adult or child.');
        return false;
    }
    return true;
}