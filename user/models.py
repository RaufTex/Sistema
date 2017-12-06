# -*- coding: utf-8 -*-
#from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group


CATEGORY = (('', '----'), ('1', _('Reserva Imediata')),
            ('2', _(u'Requer Aprovação')))

DEPARTAMENTOS = (('0', '----'), ('1', _('Recurso do ICEB')), ('2', _('DEBIO')),
           ('3', _('DECBI')), ('4', _('DECOM')),
           ('5', _('DEEST')), ('6', _('DEFIS')), ('7', _('DEMAT')),
           ('8', _('DEEMA')), ('9', _('DEQUI')))

class UserProfile(models.Model):
    registration_number = models.CharField(
        max_length=20, unique=True,
        error_messages={'unique': _('Registration Number already used.')})
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name="profile_user")
    category = models.BooleanField(_('Reserva Imediata'),default=False)
    #engineering = models.CharField(choices=ENGINEERING, max_length=15,
                                   #default=1)
    departamento_pertence = models.CharField(_('Departamento:'),choices=DEPARTAMENTOS, max_length=20, default = 0)

    def create_user(self):
        if not hasattr(self, "user"):
            self.user = User()

    def name(self, name):
        self.create_user()
        names = name.split()
        self.user.first_name = names.pop(0)
        self.user.last_name = str.join(" ", names)

    def full_name(self):
        self.create_user()
        name = str.join(" ", [self.user.first_name, self.user.last_name])
        return name

    def clean_fields(self, exclude=None):
        validation = Validation()

        # Registration Number validation
        registration_number = self.registration_number

        if (len(registration_number) != 11):
            raise ValidationError({'registration_number':
                                  [_('Registration number \
                                      must have 9 digits.'), ]})

        if validation.hasLetters(registration_number):
            raise ValidationError({'registration_number':
                                  [_('Registration number \
                                      cannot contain letters.'), ]})

        if validation.hasSpecialCharacters(registration_number):
            raise ValidationError({'registration_number':
                                  [_('Registration number \
                                      cannot contain special characters.'), ]})

    def save(self, *args, **kwargs):
        self.user.save()
        self.user_id = self.user.pk
        super(UserProfile, self).save(*args, **kwargs)

    def make_as_academic_staff(self):
        try:
            academic_staff = Group.objects.get(name="academic_staff")
        except:
            academic_staff, created = (Group.objects.
                                       get_or_create(name="academic_staff"))

        self.create_user()
        self.user.groups.add(academic_staff)

    def make_as_admin(self):
        try:
            admin = Group.objects.get(name="admin")
        except:
            admin, created = Group.objects.get_or_create(name="admin")

        self.create_user()
        self.user.groups.add(admin)

    def is_admin(self):
        try:
            self.user.groups.get(name="admin")
            return True
        except Group.DoesNotExist:
            return False

    def is_academic_staff(self):
        try:
            self.user.groups.get(name="academic_staff")
            return True
        except Group.DoesNotExist:
            return False

    @staticmethod
    def get_users():
        users = UserProfile.objects.all()
        choices = []
        for user in users:
            new_choice = (user, user)
            choices.append(new_choice)
        choices = sorted(choices, key=lambda user_tuple:
                         user_tuple[0].full_name())
        choices.insert(0, ('', ''))
        return choices

    def __str__(self):
        return '\n'.join((self.full_name(), '<' + self.user.username + '>'))


class Settings(models.Model):
    start_semester = models.DateField(null=False, blank=False)
    end_semester = models.DateField(null=False, blank=False)

    def get_start(self):
        return Settings.objects.last().start_semester

    def get_end(self):
        return Settings.objects.last().end_semester


class Validation():

    def hasNumbers(self, string):
        if (string is not None):
            if any(char.isdigit() for char in string):
                return True

            return False

        else:
            return False

    def hasLetters(self, number):
        if (number is not None):
            if any(char.isalpha() for char in number):
                return True

            return False

        else:
            return False

    def hasSpecialCharacters(self, string):
        if (string is not None):
            for character in '[]':
                if character in string:
                    return True

        return False
