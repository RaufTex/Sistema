# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _, ugettext as __
from django.db import models, connection
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import copy
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

CATEGORY = (('', '----------'), ('1', _('Without Aprooved')),
            ('2', _('With Aprooved')))

WEEKDAYS = (('0', _("Monday")), ('1', _("Tuesday")), ('2', _("Wednesday")),
            ('3', _("Thursday")), ('4', _("Friday")), ('5', _("Saturday")),
            ('6', _("Sunday")))

DEPARTAMENTOS = (('0', _('---')), ('1', _('Recurso do ICEB')), ('2', _('DEBIO')),
           ('3', _('DECBI')), ('4', _('DECOM')),
           ('5', _('DEEST')), ('6', _('DEFIS')), ('7', _('DEMAT')),
           ('8', _('DEEMA')), ('9', _('DEQUI')))


class Building(models.Model):
    name = models.CharField('Departamento',max_length=200)

    def __str__(self):
        return self.name


class Place(models.Model):
    opcoes_default = (
        ('0', '----'),
        ('1', 'Não'),
        ('2', 'Sim'),
    )

    name = models.CharField('Nome',max_length=200)
    capacity = models.IntegerField('Capacidade')
    building = models.ForeignKey(Building, verbose_name='Departamento')
    #location = models.CharField(max_length=50)
    place_id = models.CharField(max_length=200)
    #is_laboratory = models.BooleanField(default=False)
    tipo = models.CharField('Tipo', max_length=45)
    """
    " Se o recurso possui um projetor. 1 se sim, 0 para não
    """
    possui_projetor = models.CharField('Possui Projetor?', max_length = 1, choices = opcoes_default, default='0')

    """
    " Se o recurso possui quadro. 1 se sim, 0 para não
    """
    possui_quadro_branco = models.CharField('Possui Quadro Branco?', max_length = 1, choices = opcoes_default, default='0')

    """
    " Se o recurso possui quadro negro. 1 se sim, 0 para não
    """
    possui_quadro_negro = models.CharField('Possui Quadro Negro?', max_length = 1, choices = opcoes_default, default='0')

    descricao = models.TextField('Descrição', max_length=255, default='...')
    def __str__(self):
        try:
            return (self.building.name + " | " + self.name +
                    " - Capacidade: " + str(self.capacity))
        except:
            return self.name

    def exists(self, building, name):
        #week_days = [1 if int(x) == 6 else int(x) + 2 for x in week_days]
        return Place.objects.filter(place_id = self.place_id,
                                   building = self.building,
                                   name = self.name,
                                   #building_name = building,
                                   #place_name = name,
                                   ).exists()


    def save(self, *args, **kwargs):
        super(Place, self).save(*args, **kwargs)

    def delete(self):
        #self.time.all().delete()
        super(Place, self).delete()

class BookTime(models.Model):
    start_hour = models.TimeField(null=False, blank=False)
    end_hour = models.TimeField(null=False, blank=False)
    date_booking = models.DateField(null=False, blank=False)

    def add_days(self, nr_days):
        delta = timedelta(days=nr_days)
        self.date_booking = self.date_booking + delta

    def next_week_day(self, nr_weekday):
        diff_of_weekdays = self.date_booking.weekday() - nr_weekday
        if diff_of_weekdays > 0:
            self.add_days(7 - diff_of_weekdays)
        elif diff_of_weekdays < 0:
            self.add_days(diff_of_weekdays * (-1))
        else:
            self.add_days(7)

    def get_str_weekday(self):
        return self.date_booking.strftime("%A")

    def __str__(self):
        return (str(self.date_booking) + " | " +
                str(self.start_hour) + " - " + str(self.end_hour))

    def delete_booktime(self, booking):
        if booking.time.count() == 1:
            booking.delete()
        else:
            booking.time.remove(self)
            super(BookTime, self).delete()

'''
class Tag(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    @staticmethod
    def get_tags():
        tags = Tag.objects.all()
        choices = []
        for tag in tags:
            new_choice = (tag, tag)
            choices.append(new_choice)
        choices = sorted(choices, key=lambda tag_tuple:
                         tag_tuple[0].name)
        choices.insert(0, ('', ''))
        return choices
'''

BOOKING_STATUS = ((0, _("Denied")), (1, _("Pending")), (2, _("Approved")))


class Booking(models.Model):
    user = models.ForeignKey(User, related_name="bookings",
                             on_delete=models.CASCADE)
    #responsible = models.CharField(max_length=100, default=' ')
    time = models.ManyToManyField(BookTime, related_name="booking_time")
    place = models.ForeignKey(Place, related_name="booking_place")
    name = models.CharField(max_length=50)
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)
    status = models.PositiveSmallIntegerField(choices=BOOKING_STATUS,
                                              default=1)
    #tags = models.ManyToManyField(Tag, related_name="tags")

    #engineering = models.CharField(choices=ENGINEERINGS, max_length=5)

    def __str__(self):
        return (self.name + " " + self.user.email + " | " + str(self.place) +
                " - " + str(self.start_date) + " - " + str(self.end_date))

    def exists(self, start_hour, end_hour, week_days):
        week_days = [1 if int(x) == 6 else int(x) + 2 for x in week_days]
        return Booking.objects.filter(place_id = self.place.place_id,
                                   time__date_booking__gte = self.start_date,
                                   time__date_booking__lt = self.end_date,
                                   time__start_hour = start_hour,
                                   time__end_hour = end_hour,
                                   time__date_booking__week_day__in = week_days
                                   ).exists()


    def save(self, *args, **kwargs):
        if (not self.user.profile_user.category):
            self.status = 1  # status for pending booking

        if Place.objects.filter(name=self.place.name):
            self.place = Place.objects.get(name=self.place.name)
        else:
            self.place.save()
            self.place_id = self.place.pk

        super(Booking, self).save(*args, **kwargs)

    def delete(self):
        self.time.all().delete()
        super(Booking, self).delete()

    def update_status(self, status):
        Booking.objects.filter(pk=self.pk).update(status=status)
        self.refresh_from_db()

    def update_start_date(self):
        all_booktimes = self.time.order_by('date_booking')
        self.start_date = all_booktimes.first().date_booking
        self.save()

    def update_end_date(self):
        all_booktimes = self.time.order_by('date_booking')
        self.end_date = all_booktimes.last().date_booking
        self.save()

    def delete_booktime(self, id_booktime, user):
        booktime = BookTime.objects.get(pk=id_booktime)
        all_booktimes = self.time.order_by('date_booking')
        if (user.profile_user.is_staff() or self.user.id == user.id) and \
                booktime in all_booktimes:
            booktime.delete()
            if(all_booktimes.count() > 1):
                self.update_start_date()
                self.update_end_date()
        else:
            raise PermissionDenied()

    @staticmethod
    def get_bookings():
        bookings = Booking.objects.values('name').order_by('-name').distinct()
        choices = ()
        for booking in bookings:
            new_choice = (booking['name'], booking['name'])
            choices = (new_choice,) + choices
        return choices

    @staticmethod
    def get_responsibles():
        bookings = Booking.objects.values('responsible').distinct()
        choices = ()
        for booking in bookings:
            new_choice = (booking['responsible'], booking['responsible'])
            choices = (new_choice,) + choices
        return choices

    @staticmethod
    def get_places(bookings):
        place_name = []
        place = []

        for booking in bookings:
            p = booking.place.name.split('-')
            if (booking.status > 1) and (p[1] not in place_name):
                place_name.append(p[1])
                place.append(booking.place)
        return place, place_name


class Validation():

    def hasNumbers(self, string):
        if any(char.isdigit() for char in string):
            return True

    def hasLetters(self, number):
        if any(char.isalpha() for char in number):
            return True

    def hasSpecialCharacters(self, string):
        for character in '@#$%^&+=/\{[]()}-_+=*!§|':
            if character in string:
                return True


def date_range(start_date, end_date):
    return [start_date + timedelta(days=x)
            for x in range(0, (end_date - start_date).days + 1)]
