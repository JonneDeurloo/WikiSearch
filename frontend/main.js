$(document).ready(function () {
    $('#search').validate({
        rules: {
            q: {
                required: true
            }
        }, 
        messages: {
            q: {
                required: " "
            }
        }
    })
});
