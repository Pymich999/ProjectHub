# custom_filters.py
from django import template
from django.db.models import Avg

register = template.Library()

@register.filter
def average(queryset, field):
    return queryset.aggregate(Avg(field))[f"{field}__avg"] or 0
