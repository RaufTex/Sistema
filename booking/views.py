from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, redirect, get_object_or_404
from booking.forms import BookingForm, SearchBookingForm, PlaceForm
from booking.models import Booking, BookTime, Place, Building
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from SistemaGestao.decorators import required_to_be_admin
from SistemaGestao.views import index
from django.views import View
from datetime import datetime, timedelta
import operator
from collections import OrderedDict
import traceback
from django.utils import formats
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.views import View
from user.models import Settings
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic.edit import FormView

HOURS = [(6, "06-07"), (7, "07-08"), (8, "08-09"),
         (9, "09-10"), (10, "10-11"), (11, "11-12"),
         (12, "12-13"), (13, "13-14"), (14, "14-15"),
         (15, "15-16"),(16, "16-17"),(17, "17-18"),
         (18, "18-19"),(19, "19-20"),(20, "20-21"),
         (21, "21-22"),(22, ("22-23"))]

'''
@login_required(login_url='/?showLoginModal=yes')
@staff_member_required
def new_place(request):
    start_semester = Settings.objects.last().start_semester
    end_semester = Settings.objects.last().end_semester
    user = request.user
    if request.method == "POST":
        form_place = PlaceForm(request.user, request.POST)
        if (form_place.is_valid()):
            place = form_place.save(request.user)
            if place:
                request.session['place'] = place.pk
                return render(request, 'booking/showPlaces.html',
                              {'place': place})
            else:
                messages.error(request, _("Booking alread exists"))
    else:
        form_place = PlaceForm(request.user)
    return render(request, 'booking/newPlace.html',
                  {'form_place': form_place,
                   'start_semester': start_semester,
                   'end_semester': end_semester,
                   'is_staff': user.is_staff})
'''

@login_required(login_url='/?showLoginModal=yes')
@staff_member_required
def search_rec(request):
    #id = request.user.profile_user.id
    recs = Place.objects.all()
    return render(request, 'booking/searchRec.html', {'recs': recs})

@login_required(login_url='/?showLoginModal=yes')
@staff_member_required
def new_place(request):
    #start_semester = Settings.objects.last().start_semester
    #end_semester = Settings.objects.last().end_semester
    #user = request.user
    #form_class = PlaceForm
    #form = form_class(request.POST)
    if request.method == "POST":
        form = PlaceForm(request.POST)
        if form.is_valid():
            place = form.save(commit=False)
            place.save()
            #return render(request, 'booking/showPlaces.html',
            #              {'place': place})
            #if place:
            #    request.session['place'] = place.pk
            #    return render(request, 'booking/showPlaces.html',
            #                  {'place': place})
            #else:
            #    messages.error(request, _("Booking alread exists"))
    else:
        form = PlaceForm()
        #if form.is_valid():
        #    post = form.save(commit=False)
        #    post.save()
        #else:
        #    form = PlaceForm()
    return render(request, 'booking/newPlace.html', {'form': form})

class NewPlaceView(FormView):
    template_name = "booking/newPlace.html"
    form_class = PlaceForm
    success_url = "/"

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _('O recurso foi cadastrado com sucesso!'))
        return super(NewPlaceView, self).form_valid(form)

@login_required(login_url='/?showLoginModal=yes')
@staff_member_required
def search_user(request):
    id = request.user.profile_user.id
    users = UserProfile.objects.all().exclude(pk=id)
    return render(request, 'user/searchUser.html', {'users': users})

def search_booking_day_room(request, form_booking):
    form_days = form_booking.week_day()
    place_id = form_booking["room_name"].data
    booking_place = Place.objects.get(id=place_id)
    weekday = [(_("Monday")), (_("Tuesday")), (_("Wednesday")),
               (_("Thursday")), (_("Friday")), (_("Saturday")),
               (_("Sunday"))]

    n = len(form_days) + 1

    table = []

    for form_day in form_days:
        aux = []
        bookings = Booking.objects.filter(time__date_booking=str(form_day))
        for booking in bookings:
            if (booking.place.name == booking_place.name and
                    booking.status > 1):
                book = booking.time.get(date_booking=str(form_day))
                aux_tuple = (book.start_hour.hour, booking)
                aux.append(aux_tuple)

        table.append(aux)

    period = (formats.date_format(form_days[0], "SHORT_DATE_FORMAT") + " - " +
              formats.date_format(form_days[-1], "SHORT_DATE_FORMAT"))

    table_header = str(booking_place) + ": " + period

    return render(request, 'booking/template_table.html',
                  {'days': form_days, 'table': table, 'hours': HOURS,
                   'n': n, 'name': _("Grade Horária por Recurso"),
                   'column_header': weekday, 'table_header': table_header,
                   'place': booking_place})


def search_booking_building_day(request, form_booking):
    form_day = form_booking.get_day()
    building_id = form_booking["building_name"].data
    building = Building.objects.get(id=building_id)
    places = Place.objects.filter(building=building)
    n = len(places) + 1

    places_ = []
    table = []

    for place in places:
        aux = []
        bookings = Booking.objects.filter(time__date_booking=str(form_day))
        for booking in bookings:
            if (booking.place.name == place.name and booking.status > 1):

                book = booking.time.get(date_booking=str(form_day))
                aux_tuple = (book.start_hour.hour, booking)
                aux.append(aux_tuple)

        table.append(aux)
        p = place.name.split('-')
        #places_.append(p[1])

    table_header = (str(building) + " | " +
                    formats.date_format(form_day, "SHORT_DATE_FORMAT"))

    return render(request, 'booking/template_table.html',
                  {'days': form_day, 'table': table, 'hours': HOURS,
                   'n': n, 'name': _(' Occupation'), 'column_header': places_,
                   'table_header': table_header, 'place': places})


def search_booking_responsible(request, form_booking):
    form_day = form_booking.get_day()
    search_booking_responsible = form_booking["responsible"].data
    booking_responsible = form_booking["responsible"].data
    hours = [(6, "06-07"), (7, "07-08"), (8, "08-09"),
             (9, "09-10"), (10, "10-11"), (11, "11-12"),
             (12, "12-13"), (13, "13-14"), (14, "14-15"),
             (15, "15-16"),(16, "16-17"),(17, "17-18"),
             (18, "18-19"),(19, "19-20"),(20, "20-21"),
             (21, "21-22"),(22, ("22-23"))]

    table = []
    responsible = booking_responsible.split('\r')

    bookings = Booking.objects.filter(responsible__contains=responsible[0])

    if len(responsible) > 1:
        responsible_ = responsible[1].split('\n')
        bookings = Booking.objects.filter(
            responsible__contains=responsible_[1])

    places, place_names = Booking.get_places(bookings)

    for place in place_names:
        aux = []
        for booking in bookings:
            p = booking.place.name.split('-')
            if (booking.status > 1 and p[1] == place):
                book = booking.time.get(date_booking=str(form_day))
                aux_tuple = (book.start_hour.hour, booking)
                aux.append(aux_tuple)

        table.append(aux)

    n = len(places) + 1

    print(table)
    return render(request, 'booking/template_table.html',
                  {'days': form_day, 'table': table,
                   'column_header': place_names, 'hours': hours,
                   'n': n, 'name': _(' Responsible'), 'place': places})


def search_booking_booking_name_week(request, form_booking):
    form_days = form_booking.days_list()
    search_booking_name = form_booking["booking_name"].data
    booking_name = form_booking["booking_name"].data
    place_id = Place.objects.get(pk=1)
    hours = [(6, "06-07"), (7, "07-08"), (8, "08-09"),
             (9, "09-10"), (10, "10-11"), (11, "11-12"),
             (12, "12-13"), (13, "13-14"), (14, "14-15"),
             (15, "15-16"),(16, "16-17"),(17, "17-18"),
             (18, "18-19"),(19, "19-20"),(20, "20-21"),
             (21, "21-22"),(22, ("22-23"))]
    n = len(form_days) + 1

    table = []

    for form_day in form_days:
        aux = []
        bookings = Booking.objects.filter(time__date_booking=str(form_day),
                                          name__contains=search_booking_name)
        print(bookings)
        for booking in bookings:
            if (booking.name == booking_name and booking.status > 1):
                book = booking.time.get(date_booking=str(form_day))
                aux_tuple = (book.start_hour.hour, booking)
                aux.append(aux_tuple)
                place_id = booking.place

        table.append(aux)

    return render(request, 'booking/template_table.html',
                  {'days': form_days, 'table': table,
                   'column_header': form_days, 'hours': hours,
                   'n': n, 'name': _(' Booking'), 'place': place_id})


def search_booking_room_period(request, form_booking):
    form_days = form_booking.days_list()
    place_id = form_booking["room_name"].data
    booking_place = Place.objects.get(id=place_id)

    n = len(form_days) + 1

    table = []

    for form_day in form_days:
        aux = []
        bookings = Booking.objects.filter(time__date_booking=form_day)
        for booking in bookings:
            if (booking.place.name == booking_place.name and
                    booking.status > 1):
                book = booking.time.get(date_booking=str(form_day))
                aux_tuple = (book.start_hour.hour, booking)
                aux.append(aux_tuple)

        table.append(aux)
    period = (formats.date_format(form_days[0], "SHORT_DATE_FORMAT") + " - " +
              formats.date_format(form_days[-1], "SHORT_DATE_FORMAT"))
    table_header = (str(booking_place) + " | " + period)

    return render(request, 'booking/template_table.html',
                  {'days': form_days, 'table': table, 'hours': HOURS,
                   'n': n, 'name': _(' Recurso'), 'column_header': form_days,
                   'table_header': table_header, 'place': booking_place})

search_options = {'opt_day_room': search_booking_day_room,
                  'opt_booking_week': search_booking_booking_name_week,
                  'opt_building_day': search_booking_building_day,
                  'opt_room_period': search_booking_room_period}
                  #'opt_responsible': search_booking_responsible}


class SearchBookingQueryView(View):
    form_class = SearchBookingForm
    template_name = 'booking/searchBookingQuery.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, self.template_name, {'search_booking': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            option = request.POST.get('search_options')
            try:
                return search_options[option](request, form)
            except Exception as e:
                messages.error(request, _('Invalid option'))
                print(e)
                traceback.print_exc()
        return render(request, self.template_name, {'search_booking': form})


class NewBooking(View):

    def get(self, request):
        return render(request, 'booking/newBooking2.html')

@login_required(login_url='/?showLoginModal=yes')
def new_booking(request):
    start_semester = Settings.objects.last().start_semester
    end_semester = Settings.objects.last().end_semester
    user = request.user
    if request.method == "POST":
        form_booking = BookingForm(request.user, request.POST)
        if (form_booking.is_valid()):
            booking = form_booking.save(request.user)
            if booking:
                request.session['booking'] = booking.pk
                return render(request, 'booking/showDates.html',
                              {'booking': booking})
            else:
                messages.error(request, _("Booking alread exists"))
    else:
        form_booking = BookingForm(request.user)
    return render(request, 'booking/newBooking.html',
                  {'form_booking': form_booking,
                   'start_semester': start_semester,
                   'end_semester': end_semester,
                   'is_staff': user.is_staff})


def search_booking_table(request):
    if request.method == "POST":
        form_booking = SearchBooking(request.POST)
        if(form_booking.is_valid()):
            bookings = form_booking.search()
            return render(request, 'booking/template_table.html',
                          {'form_booking': form_booking,
                           'bookings': bookings})
    form_booking = SearchBooking()
    return render(request, 'booking/searchBookingTable.html',
                  {'form_booking': form_booking})


@login_required(login_url='/?showLoginModal=yes')
def search_booking(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'booking/searchBooking.html',
                  {'bookings': bookings, 'name': ""})


@login_required(login_url='/?showLoginModal=yes')
@staff_member_required
def all_bookings(request):
        bookings = Booking.objects.all()
        name = _("All Bookings")
        return render(request, 'booking/searchBooking.html',
                      {'bookings': bookings, 'name': name})


@login_required(login_url='/?showLoginModal=yes')
@staff_member_required
def pending_bookings(request):
        bookings = Booking.objects.filter(status=1)
        name = _("Pending Bookings")
        return render(request, 'booking/pendingBooking.html',
                      {'bookings': bookings, 'name': name})


@login_required(login_url='/?showLoginModal=yes')
def cancel_booking(request, id):
    if request.session['booking']:
        id = int(id)
        if(id == request.session.get('booking')):
            request.session.pop('booking')
            Booking.objects.get(pk=id).delete()
            messages.success(request, _("Booking has been canceled"))
            return redirect("index")
        else:
            messages.error(request, _("You cannot cancel this booking"))
            return index(request)
    else:
        return redirect("index")


@login_required(login_url='/?showLoginModal=yes')
def confirm_booking(request, id):
    if request.session.get('booking'):
        id = int(id)
        if id == request.session.get('booking'):
            request.session.pop('booking')
            messages.success(request, _("Booking has been saved."))
            return index(request)
        else:
            messages.error(request, _("You cannot confirm this booking"))
            return index(request)
    else:
        return index(request)


@login_required(login_url='/?showLoginModal=yes')
def delete_booking(request, id):
    try:
        booking = Booking.objects.get(pk=id)
        if (request.user.profile_user.is_admin() or
                booking.user.id == request.user.id):
            booking.delete()
            messages.success(request, _('Booking deleted!'))
        else:
            messages.error(request, _('You cannot delete this booking.'))
    except:
        messages.error(request, _('Booking not found.'))
    return search_booking(request)


@login_required(login_url='/?showLoginModal=yes')
@staff_member_required
def approve_booking(request, id):
    try:
        booking = Booking.objects.get(pk=id)
        booking.update_status(status=2)
        messages.success(request, _('Booking Approved!'))
    except:
        messages.error(request, _('Booking not found.'))
    return pending_bookings(request)


@login_required(login_url='/?showLoginModal=yes')
@staff_member_required
def deny_booking(request, id):
    try:
        booking = Booking.objects.get(pk=id)
        booking.update_status(status=0)
        print(booking.status)
        messages.success(request, _('Booking Denied!'))
    except:
        messages.error(request, _('Booking not found.'))
    return pending_bookings(request)


@login_required(login_url='/?showLoginModal=yes')
def delete_booktime(request, booking_id, booktime_id):
    try:
        booking = Booking.objects.get(pk=booking_id)
        booking.delete_booktime(booktime_id, request.user)
        if booking.time.count() == 0:
            booking.delete()
        messages.success(request, _('Booking deleted!'))
    except PermissionDenied:
        messages.error(request, _('You cannot delete this booking.'))
    except (ObjectDoesNotExist, Booking.DoesNotExist):
        messages.error(request, _('Booking not found.'))
    return show_booktimes(request, booking_id)


@login_required(login_url='/?showLoginModal=yes')
def show_booktimes(request, booking_id):
    try:
        booking = Booking.objects.get(pk=booking_id)
        return render(request, 'booking/showBookTimes.html',
                      {'booking': booking})
    except:
        messages.error(request, _('Booking not found.'))
    if request.user.profile_user.is_admin():
        return all_bookings(request)
    else:
        return search_booking(request)


@login_required(login_url='/?showLoginModal=yes')
def booking_details(request, booking_id):
    try:
        booking = Booking.objects.get(pk=booking_id)
        #tags = booking.tags.all()
        return render(request, 'booking/bookingDetails.html',
                      {'booking': booking})
    except:
        messages.error(request, _('Booking not found.'))
    if request.user.is_staff:
        return all_bookings(request)
    else:
        return search_booking(request)

'''
@login_required(login_url='/?showLoginModal=yes')
def tagged_bookings(request, tag_id):
    try:
        tag = Booking.objects.get(tags__id=tag_id).name
        name = _("Tagged Bookings ")
        bookings = Booking.objects.filter(tags__id=tag_id).prefetch_related('tags')
        return render(request, 'booking/searchBooking.html',
                      {'bookings': bookings, 'name': name})
    except:
        messages.error(request, _('Booking not found.'))
        return redirect("index")
'''
