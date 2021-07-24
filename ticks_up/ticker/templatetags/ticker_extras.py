from django import template
from django.template.defaultfilters import stringfilter
from utils.graphs import draw_graph

register = template.Library()

@register.filter(name='header')
@stringfilter
def cut(val):
    return val.replace("_", " ").title()

@register.filter(name='draw_graph')
def draw_graph(**kwargs):
    return draw_graph(**kwargs)