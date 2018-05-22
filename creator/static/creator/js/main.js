$(document).ready(function(){
    // Initialize the date picker and advanced section collapsible
    let datepickerOptions = {
        altInput: true,
        altFormat: "F j",
        dateFormat: "Y-m-d"
    };
    $(".datepicker").flatpickr(datepickerOptions);
    datepickerOptions.mode = "range";
    $(".daterangepicker").flatpickr(datepickerOptions);
    $(".collapsible").collapsible();

    // Reopen the advanced section if the validation returned an error
    if ($(".advanced-fields").find(".errorlist").length) {
        M.Collapsible.getInstance($(".collapsible")).open(0);
    }
});
