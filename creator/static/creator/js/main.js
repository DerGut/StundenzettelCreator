$(document).ready(function(){
    $(".datepicker").flatpickr({});
    $(".daterangepicker").flatpickr({
        altInput: true,
        altFormat: "F j",
        dateFormat: "Y-m-d",
        mode: "range"
    });
    $(".collapsible").collapsible();
});
