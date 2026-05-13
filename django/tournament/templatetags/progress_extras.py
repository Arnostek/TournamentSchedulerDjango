from django import template

register = template.Library()

@register.filter
def divisibleby_total(played, total):
    try:
        return int(100 * float(played) / float(total))
    except (ZeroDivisionError, ValueError, TypeError):
        return 0
