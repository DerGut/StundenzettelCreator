$(document).ready(function(){
    $('.daterangepicker').flatpickr({
        altInput: true,
        altFormat: "F j",
        dateFormat: "Y-m-d",
        mode: "range"
    });
    $('.collapsible').collapsible();

    $('.show-advanced').click(function () {
        $('.advanced-fields').css('display', 'block');
    });
});
