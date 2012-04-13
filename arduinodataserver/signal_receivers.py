from datetime import timedelta, datetime
from django.db.models.aggregates import Sum

import logging
logger = logging.getLogger('measurements')

WEEK_START_SUNDAY = False

def update_hourly(sender, interval=None, **kwargs):
    """Every time a new object is created in models.MeterData, do summing of
    hourly data."""
    
    import models
    
    instance = kwargs['instance']

    from_time = instance.created
    from_time = from_time.replace(minute=0, second=0, microsecond=0)
    insert_interval(instance, models.INTERVAL_HOURLY, from_time, interval=interval)

def update_daily(sender, interval=None, **kwargs):
    """Every time a new object is created in models.MeterData, do summing of
    daily data."""
    
    import models
    
    instance = kwargs['instance']

    from_time = instance.created
    from_time = from_time.replace(hour=0, minute=0, second=0, microsecond=0)
    insert_interval(instance, models.INTERVAL_DAILY, from_time, interval=interval)
    
def update_weekly(sender, interval=None, **kwargs):
    """Every time a new object is created in models.MeterData, do summing of
    weekly data."""
    
    import models
    
    instance = kwargs['instance']

    # Calculate from where the week started...
    days_from_weekstart = instance.created.weekday()
    
    if WEEK_START_SUNDAY:
        if days_from_weekstart == 7:
            days_from_weekstart = 0
        else:
            days_from_weekstart += 1
    
    from_time = instance.created - timedelta(days=days_from_weekstart)
    
    from_time = from_time.replace(hour=0, minute=0, second=0, microsecond=0)
    
    insert_interval(instance, models.INTERVAL_WEEKLY, from_time, interval=interval)

def update_monthly(sender, interval=None, **kwargs):
    """Every time a new object is created in models.MeterData, do summing of
    monthly data."""
    
    import models
    
    instance = kwargs['instance']

    from_time = instance.created
    from_time = from_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    insert_interval(instance, models.INTERVAL_MONTHLY, from_time, interval=interval)

def update_annually(sender, interval=None, **kwargs):
    """Every time a new object is created in models.MeterData, do summing of
    annual data."""
    
    import models
    
    instance = kwargs['instance']

    from_time = instance.created
    from_time = from_time.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    insert_interval(instance, models.INTERVAL_ANNUALLY, from_time, interval=interval)
    

def insert_interval(meter_data, name_id, from_time, interval=None):
    """
    Do the actual insertion of new data for some interval. If the interval
    is not represented, then create it.
    """
    import models
    
    if meter_data.meter.is_counter:
        
        latest_reading = models.MeterData.objects.filter(meter=meter_data.meter).exclude(id=meter_data.id).order_by('-created')
        
        if latest_reading and latest_reading[0].created > meter_data.created:
            # Something has been updated
            recalculate_interval(meter_data.meter, name_id, from_time, interval=interval)
            return
        elif latest_reading:
            delta = meter_data.diff
        elif meter_data.diff:
            delta = meter_data.diff
        else:
            delta = 1
    
    else:
        delta = meter_data.data_point
    
    # Only use one kind of interval
    if interval:
        interval_types = [interval]
    else:
        interval_types = models.IntervalType.objects.filter(meter_set=meter_data.meter,
                                                            name=name_id)

    for interval_type in interval_types:
    
        try:
            interval = models.Interval.objects.get(from_time=from_time, 
                                                   interval_type=interval_type,
                                                   )
            interval.total = interval.total + (delta * interval_type.unit_fraction)
            interval.data_entries += 1
            interval.average = interval.total / interval.data_entries

        except models.Interval.DoesNotExist:
            interval = models.Interval(from_time=from_time,
                                       interval_type=interval_type)
            interval.total = (delta * interval_type.unit_fraction)
            interval.average = interval.total
            interval.data_entries = 1
        
        interval.save()


def recalculate_interval(meter, name_id, from_time, interval=None):
    """Recreates the summary of a whole interval in case something has been
    created in the middle, updated or deleted"""
    import models
    
    meter_data = models.MeterData.objects.filter(created__gte=from_time,
                                                 created__lte=models.Interval.get_to_time(from_time, name_id),
                                                 meter=meter)
    meter_data = meter_data.aggregate(total_diffs=Sum('diff'))
    
    if meter_data:
        total_diff = meter_data.get('total_diffs', 0)
    else:
        total_diff = 0
    
    # Only use one kind of interval
    if interval:
        interval_types = [interval]
    else:
        interval_types = models.IntervalType.objects.filter(meter_set=meter,
                                                            name=name_id)

    for interval_type in interval_types:
        
        try:
            interval = models.Interval.objects.get(from_time=from_time, 
                                                   interval_type=interval_type,
                                                   )
            interval.total = interval.total + (total_diff * interval_type.unit_fraction)
    
        except models.Interval.DoesNotExist:
            interval = models.Interval(from_time=from_time,
                                       interval_type=interval_type)
            interval.total = (total_diff * interval_type.unit_fraction)
        
        interval.save()
    


def create_interval_backlog(interval_type, **kwargs):
    
    import models
    
    data_entries = models.MeterData.objects.filter(meter__in=[m.id for m in interval_type.meter_set.all()])
    if interval_type.backlog:
        now = datetime.now()
        from_time = now - timedelta(days=interval_type.backlog)
        data_entries.filter(created__gte=from_time)
    
    # Delete all existing data
    models.Interval.objects.filter(interval_type=interval_type).delete()
    
    # Iterate all data entries and add them in intervals
    for data in data_entries:
        models.INTERVAL_FUNCTIONS[interval_type.name](models.MeterData, instance=data, interval=interval_type)
    
