from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='header')
@stringfilter
def cut(val):
    return val.replace("_", " ").title()