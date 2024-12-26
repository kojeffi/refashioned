# from django import template

# register = template.Library()

# @register.filter(name='mult')
# def mult(value, arg):
#     try:
#         return float(value) * float(arg)
#     except (ValueError, TypeError):
#         return 0

from django import template

register = template.Library()

@register.filter(name='range')
def filter_range(value):
    return range(1, value + 1)
