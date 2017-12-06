from django import template
from user.models import CATEGORY, DEPARTAMENTOS
from django.utils.translation import ugettext as _

register = template.Library()


@register.filter(name='category')
def category(user):
    try:
        return _(CATEGORY[int(user.category)][1])
    except:
        return ''

@register.filter(name='departamento_pertence')
def departamento_pertence(user):
    try:
        return _(DEPARTAMENTOS[int(user.departamento_pertence)][1])
    except:
        return ''

@register.filter(name='type')
def is_admin(user):
    if user.is_admin():
        return _('Admin')
    else:
        return _('Academic User')


@register.filter(name='is_admin')
def is_admin(user):
    if hasattr(user, 'profile_user'):
        return user.profile_user.is_admin()
    else:
        return False
