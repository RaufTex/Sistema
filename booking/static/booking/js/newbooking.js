var buildings = Building.all();

function getCookie(name) {
    var cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

var csrftoken = getCookie('csrftoken');
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function breadcrumbsadd(index){
    $("#breadcrumbs ul li:eq(" + index + ")").addClass("active")

}

function back(index){
    $("#breadcrumbs ul li:eq(" + index + ")").removeClass("active")
    $("#page" + (index + 1)).hide();
    $("#page" + index).show();
}

$("#booking-buildings tbody").on("click", "td", function(){
    $(".building-selected").removeClass("building-selected");
    $(this).addClass("building-selected");
});

$("#booking-places tbody").on("click", "td", function(){
    $(".place-selected").removeClass("place-selected");
    $(this).addClass("place-selected");
});

function test(places){
    for(var i = 0; i < places.length; i++){
        var p = places[i];

        if(i % 3 == 0) {
            var text = "<tr>" + p.td_place() + "</tr";
            $('#booking-places tr:last').after(text);
        }

        else {
            $('#booking-places td:last').after(p.td_place());
        }
    }
}



$(document).ready(function(){
    $("#slider_begin_time").slider({
        min: 7,
        max: 23,
        step: 1,
        create: function( event, ui ) {
            $("#input_slider_begin_time").val("7:00");
        }
    });
    $("#slider_end_time").slider({
        min: 7,
        max: 23,
        step: 1,
        create: function( event, ui ) {
            $("#input_slider_end_time").val("7:00");
        }
    });
    var building = '';
    var building_name = '';
    var place = '';
    var place_name = '';
    var booking_name = '';
    var start_date = '';
    var end_date = '';
    var start_hour = '';
    var end_hour = '';
    var ar_week_days = '';
    var ar_week_days_names = '';

    $("#page1").show();
    $("#page2").hide();
    $("#page3").hide();
    $("#page4").hide();
    $("#period-dates").hide();
    $("#id_week_days").hide();

    $(".btn-back").on("click", function() {
        var val = $(this).val();
        val = val - 1;

        back(val);
    });


    $("#input_slider_begin_time").attr("disabled", true);
    $( "#slider_begin_time" ).on( "slidechange", function( event, ui ) {
        var text = $( "#slider_begin_time" ).slider("value");
        text = text + ":00";
        $("#input_slider_begin_time").val(text);
    });

    $("#input_slider_end_time").attr("disabled", true);
    $( "#slider_end_time" ).on( "slidechange", function( event, ui ) {
        var text = $( "#slider_end_time" ).slider("value");
        text = text + ":00";
        $("#input_slider_end_time").val(text);
    });

    $('input[name=times]', '#page2').click(function(){
        if($('input[name=times]:checked', '#page2').val() == "interval"){
           $("#period-dates").show();
           $("#one-day").hide();
           $("#id_week_days").show();
        }

        else{
           $("#period-dates").hide();
           $("#one-day").show();
           $("#id_week_days").hide();
        }
    });

    breadcrumbsadd(0);

    var booking = new Booking();
    $("#next-date").click(function(){

        booking_name = $("#name_of_booking").val();
        if(!booking.check_name_element($("#name_of_booking"))){
            return 0;
        }
        $("#page1").hide();
        $("#page2").show();
        $("#page3").hide();
        $("#page4").hide();

        breadcrumbsadd(1);
        booking.removeError($("#name_of_booking"));
    });

    $("#next-building").click(function() {
        start_hour = $( "#slider_begin_time" ).slider("value") + ":00:00";
        end_hour = $( "#slider_end_time" ).slider("value") + ":00:00";

        ar_week_days = [];
        ar_week_days_names = [];

        $("input[name=week_days]:checked").each(function(index){
            ar_week_days.push($(this).val());
            ar_week_days_names.push($(this).parent().text());
        });

        if($('input[name=times]:checked', '#page2').val() == "interval") {
            var startDate = $("#id_start_date").val();
            var endDate = $("#id_end_date").val();

           try {
                var StartDateinISO = $.datepicker.parseDate('mm/dd/yy', startDate);
            }
            catch(err) {
                StartDateinISO = $.datepicker.parseDate('dd/mm/yy', startDate);
            }
            start_date = $.datepicker.formatDate( "yy-mm-dd", new Date(StartDateinISO));

            try{
                var EndDateinISO = $.datepicker.parseDate('mm/dd/yy', endDate);
            }catch(err){
                var EndDateinISO = $.datepicker.parseDate('dd/mm/yy', endDate);
            }
            end_date = $.datepicker.formatDate( "yy-mm-dd", new Date(EndDateinISO));

            if(!booking.check_date($("#id_start_date")) || !booking.check_date($("#id_end_date")) ||
                !booking.check_interval_date($("#id_start_date"), $("#id_end_date"))) {
                return 0;
            }

            else if(!booking.check_time($('#input_slider_begin_time'), $('#input_slider_end_time'), $("#id_start_date"))) {
                return 0;
            }

            else if(!booking.check_weekdays($('#id_week_days'), ar_week_days)) {
                return 0;
            }
        }

        else {
            var startDate = $('#id_one_day_date').val();
            var endDate = $('#id_one_day_date').val();

            try {
                var StartDateinISO = $.datepicker.parseDate('mm/dd/yy', startDate);
            }
            catch(err) {
                StartDateinISO = $.datepicker.parseDate('dd/mm/yy', startDate);
            }
            start_date = $.datepicker.formatDate( "yy-mm-dd", new Date(StartDateinISO));

            try{
                var EndDateinISO = $.datepicker.parseDate('mm/dd/yy', endDate);
            }catch(err){
                var EndDateinISO = $.datepicker.parseDate('dd/mm/yy', endDate);
            }
            end_date = $.datepicker.formatDate( "yy-mm-dd", new Date(EndDateinISO));

            if(!booking.check_date($("#id_one_day_date")) ||
                !booking.check_time($('#input_slider_begin_time'), $('#input_slider_end_time'), $('#id_one_day_date'))) {
                return 0;
            }
        }

        if(start_date == end_date) {
            var weekdays = new Array(7);
            weekdays[0] = "Sunday";
            weekdays[1] = "Monday";
            weekdays[2] = "Tuesday";
            weekdays[3] = "Wednesday";
            weekdays[4] = "Thursday";
            weekdays[5] = "Friday";
            weekdays[6] = "Saturday";

            var weekdayOneDate = new Date(start_date);
            ar_week_days.push(weekdayOneDate.getDay()+1);
            ar_week_days_names = weekdays[weekdayOneDate.getDay()+1];
        }

        $("#page1").hide();
        $("#page2").hide();
        $("#page3").show();
        $("#page4").hide();
        $("#booking-buildings").find(".place-span").remove();

        breadcrumbsadd(2);

        booking.removeError($("#id_one_day_date"));
        booking.removeError($("#id_start_date"));
        booking.removeError($("#id_end_date"));

        booking.removeError($("#input_slider_begin_time"));
        booking.removeError($("#input_slider_end_time"));

        for(var i = 0; i < buildings.length; i++){
            var b = buildings[i];

            if(i % 2 == 0){
                var text = "<tr>" + b.td_place() + "</tr";
                $('#booking-buildings tr:last').after(text);
            }

            else{
                $('#booking-buildings td:last').after(b.td_place());
            }
        }
     });

    $("#next-place").click(function(){
        building = $(".building-selected > input").attr("value");
        building_name = $(".building-selected").text();
        //TODO: get the id of building
        if(!$('td').hasClass("building-selected")) {
            booking.addSpan($('#booking-buildings'), 'Please, select a building to continue');
            $('.help-block').css('text-align', 'center');
            return 0;
        }

        $("#page1").hide();
        $("#page2").hide();
        $("#page3").hide();
        $("#page4").show();

        breadcrumbsadd(3);
        $('.help-block').empty();
        //TODO: breadcrumps refresh
        $("#booking-places").find(".place-span").remove();
        //places = Place.all();
        var id = $(".building-selected > input").attr("value");
        booking.post_form(building, start_date, end_date, start_hour, end_hour, ar_week_days, test);
    });

    $("#next-finish").click(function(){
        place = $(".place-selected > input").attr("value");
        place_name = $(".place-selected").text();

        if(!$('td').hasClass("place-selected")) {
            booking.addSpan($('#booking-places'), 'Please, select a place to continue');
            $('.help-block').css('text-align', 'center');
            return false;
        }

        $('.help-block').empty();
    });

    $("#newbooking").submit(function(){
        var place = $(".place-selected > input").attr("value");
        var building = $(".building-selected > input").attr("value");

        $("#booking-building-hidden").val(building);
        $("#booking-place-hidden").val(place);
        $("#input_slider_end_time").prop("disabled", false);
        $("#input_slider_begin_time").prop("disabled", false);

        if($('input[name=times]:checked', '#page2').val() == "oneday") {
            var date = $("#id_one_day_date").val();
            $("#id_start_date").val(date);
            $("#id_end_date").val(date);

            var weekdayOneDate = new Date(date);
            var day = weekdayOneData.getDay() - 1;

            if(day == -1){
                day = 6;
            }

            $("input[name='week_days'][value='" + day + "']").prop("checked", true);
        }
    });
});
