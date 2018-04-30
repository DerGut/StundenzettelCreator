$(document).ready(function(){
    let datepickerOptions = {
        altInput: true,
        altFormat: "F j",
        dateFormat: "Y-m-d"
    };
    $(".datepicker").flatpickr(datepickerOptions);
    datepickerOptions.mode = "range";
    $(".daterangepicker").flatpickr(datepickerOptions);
    $(".collapsible").collapsible();
});
