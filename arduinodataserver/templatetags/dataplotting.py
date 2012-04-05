from django import template
from datetime import datetime
from random import randint
register = template.Library()

def google_chart(interval_type, show_entries=20, height="250px", from_time=None, hide_unfinished=False):
    """
    Show the latest entries in an interval_type. By default it will
    show the latest 20 entries.
    """
    from arduinodataserver import models
    
    intervals = models.Interval.objects.filter(interval_type=interval_type,)
    
    if hide_unfinished:
        intervals = intervals.filter(to_time__lte=datetime.now())
    if from_time:
        intervals = intervals.filter(from_time__gte=from_time)
    
    intervals = intervals.order_by('-from_time')
    intervals = intervals[:show_entries]
    intervals = intervals.reverse()
    
    return {
        'interval_type': interval_type,
        'intervals': intervals,
        'height': height,
        'chart_id': randint(0,100000000000000),
    }
register.inclusion_tag('arduinodataserver/includes/google_chart.html', takes_context=False)(google_chart)

@register.filter
def jsfloat(number, decimals=0):
    decimals = int(decimals)
    if decimals <= 0:
        return str(int(number))
    return str(round(float(number)*10**decimals)/10**decimals)
