from django import template
from datetime import datetime
from random import randint
register = template.Library()

def google_chart(interval_type, show_entries=20, height="250px", from_time=None, chart_dom_ref=None):
    """
    Show the latest entries in an interval_type. By default it will
    show the latest 20 entries.
    """
    
    return {
        'interval_type': interval_type,
        'from_time': from_time,
        'height': height,
        'show_entries': show_entries,
        'chart_dom_ref': randint(0,100000000000000) if not chart_dom_ref else chart_dom_ref,
    }
register.inclusion_tag('arduinodataserver/includes/google_chart.html', takes_context=False)(google_chart)

@register.filter
def jsfloat(number, decimals=0):
    decimals = int(decimals)
    if decimals <= 0:
        return str(int(number))
    return str(round(float(number)*10**decimals)/10**decimals)
