from django import template
from django.db.models.aggregates import Sum
from datetime import datetime, timedelta
from random import randint
register = template.Library()

from arduinodataserver import models

def get_latest_minutes_sum(meter, minutes=5):
    
    from_time = datetime.now() - timedelta(minutes=int(minutes))
    data_entries = models.MeterData.objects.filter(meter=meter, created__gt=from_time)
    data_entries = data_entries.aggregate(total=Sum('diff'))
    
    if data_entries:
        total = data_entries.get("total", 0)
        if total:
            return total
    return 0
    
register.simple_tag(get_latest_minutes_sum)
