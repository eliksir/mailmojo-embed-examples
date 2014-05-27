from datetime import datetime
from django import template

register = template.Library()


@register.filter
def to_datetime(value):
    return datetime.fromtimestamp(int(value))
