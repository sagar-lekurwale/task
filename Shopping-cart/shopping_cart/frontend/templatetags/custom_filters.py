from django import template

register = template.Library()

@register.filter
def custom_floatformat(value, decimal_places=2):
    try:
        float_value = float(value)
        formatted_value = "{:.{}f}".format(float_value, decimal_places)
        return formatted_value
    except (ValueError, TypeError):
        return value