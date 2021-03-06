# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-22 23:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_userprofile_departamento_pertence'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='category',
            field=models.CharField(choices=[(b'', b'----'), (b'1', 'Reserva Imediata'), (b'2', 'Requer Aprova\xe7\xe3o')], max_length=20, verbose_name='Categoria:'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='departamento_pertence',
            field=models.CharField(choices=[(b'0', b'----'), (b'1', 'Recurso do ICEB'), (b'2', 'DEBIO'), (b'3', 'DECBI'), (b'4', 'DECOM'), (b'5', 'DEEST'), (b'6', 'DEFIS'), (b'7', 'DEMAT'), (b'8', 'DEEMA'), (b'9', 'DEQUI')], default=0, max_length=20, verbose_name='Departamento:'),
        ),
    ]
