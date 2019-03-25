$(document).ready(function () {
    // Validate Enter Press
    $( "#search" ).submit(function( event ) {
        validate();
        event.preventDefault();
    });
});

// Validate form
function validate() {
    if ( $('.search-bar input').val().trim() !== "" ) {
        document.forms[0].submit();
    }
}